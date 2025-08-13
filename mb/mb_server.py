# modbus_server.py
# ---------------------------------------------------------------------------
# Servidor Modbus TCP – versão refatorada e modular
# Foco: clareza, reuso, elegância e robustez
# ---------------------------------------------------------------------------

import asyncio
import threading
import logging
import struct
import time
from dataclasses import dataclass
from typing import Dict, Optional

from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSlaveContext,
    ModbusServerContext,
    ModbusSequentialDataBlock as SequentialBlockBase,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian

from react.react_var import ReactVar
from react.react_factory import ReactFactory

# ===========================
# Configuração e Logging
# ===========================

logger = logging.getLogger("modbus")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

# Endianness global do projeto (BB por padrão).
BYTEORDER = Endian.Big
WORDORDER = Endian.Big


# ===========================
# Utilidades comuns
# ===========================

def u16(v: int) -> int:
    """Normaliza para 16 bits sem sinal."""
    return int(v) & 0xFFFF

def safe_type(rv: ReactVar) -> str:
    """Tipo upper da ReactVar ou ''."""
    return (rv.type() or "").upper() if isinstance(rv, ReactVar) else ""

def is_bool_type(rv: ReactVar) -> bool:
    """Aceita somente BOOL/BOOLEAN."""
    return isinstance(rv, ReactVar) and safe_type(rv) in ("BOOL", "BOOLEAN")

def read_float_words(value: float) -> list[int]:
    """FLOAT -> [hi, lo] segundo BYTEORDER/WORDORDER."""
    b = BinaryPayloadBuilder(byteorder=BYTEORDER, wordorder=WORDORDER)
    b.add_32bit_float(float(value))
    return b.to_registers()

def try_get_value(rv: ReactVar, default):
    """Leitura segura de rv._value."""
    try:
        return rv._value if rv._value is not None else default
    except Exception:
        return default

def decode_skip_word(decoder: BinaryPayloadDecoder) -> None:
    """Consome 1 word para manter alinhamento do decoder."""
    try:
        _ = decoder.decode_16bit_uint()
    except Exception:
        pass

def to_int_addr(addr_raw) -> Optional[int]:
    """Converte ADDRESS (string '00' ou ReactVar._value) em int."""
    try:
        if hasattr(addr_raw, "_value"):
            addr_raw = addr_raw._value
        if addr_raw is None:
            return None
        return int(str(addr_raw).strip())
    except Exception:
        return None

def to_point_str(point_raw) -> str:
    """Normaliza MB_POINT."""
    if hasattr(point_raw, "_value"):
        point_raw = point_raw._value
    return str(point_raw or "").strip().lower()


# ===========================
# Estruturas de mapeamento
# ===========================

@dataclass(frozen=True)
class MappingEntry:
    """Entrada de mapeamento para um endereço."""
    dtype: str           # "FLOAT", "INTEGER", "UNSIGNED", "BOOL"
    rv: ReactVar         # referência da variável
    is_low_word: bool    # True se esta entrada representa a low-word de um FLOAT

class MappingService:
    """
    Constrói caches O(1) para HR/IR/CO/DI.
    Para FLOAT em HR/IR, mapeia também a low-word (addr+1) via is_low_word=True.
    """
    def __init__(self, react_factory: ReactFactory):
        self.rf = react_factory
        self.hr: Dict[int, MappingEntry] = {}
        self.ir: Dict[int, MappingEntry] = {}
        self.co: Dict[int, MappingEntry] = {}
        self.di: Dict[int, MappingEntry] = {}

    def rebuild(self) -> None:
        """Reconstrói todos os caches a partir de df['MODBUS']."""
        self.hr.clear(); self.ir.clear(); self.co.clear(); self.di.clear()

        df = self.rf.df.get("MODBUS")
        if df is None:
            logger.warning("DF 'MODBUS' ausente – caches vazios.")
            return

        for _, row in df.iterrows():
            try:
                addr = to_int_addr(row.get("ADDRESS"))
                if addr is None:
                    continue
                point = to_point_str(row.get("MB_POINT"))
                rv = row.get("CLP100")
                if not isinstance(rv, ReactVar):
                    continue
                dtype = safe_type(rv)
            except Exception:
                continue

            if point in ("hr", "ir"):
                # Registradores
                if dtype == "FLOAT":
                    base = MappingEntry(dtype="FLOAT", rv=rv, is_low_word=False)
                    low  = MappingEntry(dtype="FLOAT", rv=rv, is_low_word=True)
                    if point == "hr":
                        self.hr[addr] = base
                        self.hr[addr + 1] = low
                    else:
                        self.ir[addr] = base
                        self.ir[addr + 1] = low
                elif dtype in ("INTEGER", "UNSIGNED"):
                    entry = MappingEntry(dtype=dtype, rv=rv, is_low_word=False)
                    (self.hr if point == "hr" else self.ir)[addr] = entry
                else:
                    # Tipo não suportado para registrador => ignora mapeamento
                    continue

            elif point in ("co", "di"):
                # Bits
                if is_bool_type(rv):
                    entry = MappingEntry(dtype="BOOL", rv=rv, is_low_word=False)
                    (self.co if point == "co" else self.di)[addr] = entry
                else:
                    continue

    # Lookups
    def lookup_hr(self, addr: int) -> Optional[MappingEntry]:
        return self.hr.get(addr)

    def lookup_ir(self, addr: int) -> Optional[MappingEntry]:
        return self.ir.get(addr)

    def lookup_co(self, addr: int) -> Optional[MappingEntry]:
        return self.co.get(addr)

    def lookup_di(self, addr: int) -> Optional[MappingEntry]:
        return self.di.get(addr)


# ===========================
# Blocos base reusáveis
# ===========================

class _BaseRegisterBlock(SequentialBlockBase):
    """
    Base para HR/IR (16 bits por word) usando MappingService.
    Regras de leitura:
      - INTEGER/UNSIGNED: 1 word
      - FLOAT: 2 words (se remaining>=2) ou 1 word; suporta desalinhado com is_low_word.
    """
    def __init__(self, unit_id: int, mapping: MappingService, point_type: str, read_only: bool):
        super().__init__(0, [0])
        self.unit_id = unit_id
        self.mapping = mapping
        self.point_type = point_type   # "hr" ou "ir"
        self.read_only = read_only

    def validate(self, address, count=1):
        return True  # responderemos zeros se não mapeado

    def _lkp(self, addr: int) -> Optional[MappingEntry]:
        return (self.mapping.lookup_hr(addr) if self.point_type == "hr"
                else self.mapping.lookup_ir(addr))

    def _read_entry_words(self, entry: MappingEntry, remaining: int) -> tuple[list[int], int]:
        """
        Converte a entry em words Modbus e retorna (words, step_addr).
        step_addr indica de quantos endereços avançar após responder.
        """
        dt = entry.dtype

        if dt == "FLOAT":
            val = float(try_get_value(entry.rv, 0.0))
            words = read_float_words(val)  # [hi, lo] segundo config
            if entry.is_low_word:
                # Low-word isolada
                return [words[1]], 1
            # Base/high: pode responder 2 words se houver espaço
            if remaining >= 2:
                return words, 2
            return [words[0]], 1

        if dt == "INTEGER":
            val = int(try_get_value(entry.rv, 0))
            return [u16(val)], 1

        if dt == "UNSIGNED":
            val = int(try_get_value(entry.rv, 0))
            return [u16(val)], 1

        # Desconhecido -> 0
        logger.warning(f"{self.point_type.upper()}: tipo desconhecido '{dt}'")
        return [0], 1

    def getValues(self, address, count=1):
        regs: list[int] = []
        addr = address
        end_addr = address + count

        while addr < end_addr:
            remaining = end_addr - addr
            entry = self._lkp(addr)
            if entry is None:
                regs.append(0); addr += 1
                continue

            try:
                words, step = self._read_entry_words(entry, remaining)
                regs.extend(words)
                addr += step
            except Exception as e:
                logger.error(f"Erro ao ler {self.point_type.upper()} {addr:02}: {e}")
                regs.append(0); addr += 1

        # Garante tamanho exato
        if len(regs) != count:
            regs = (regs + [0] * count)[:count]
        return regs

    def setValues(self, address, values):
        if self.read_only:
            logger.warning(f"Escrita ignorada em {self.point_type.upper()} (RO). Addr inicial: {address}")
            return


class _BaseBitBlock(SequentialBlockBase):
    """
    Base para CO/DI (bits), reusando MappingService.
    """
    def __init__(self, unit_id: int, mapping: MappingService, point_type: str, read_only: bool):
        super().__init__(0, [0])
        self.unit_id = unit_id
        self.mapping = mapping
        self.point_type = point_type   # "co" ou "di"
        self.read_only = read_only

    def validate(self, address, count=1):
        return True

    def _lkp(self, addr: int) -> Optional[MappingEntry]:
        return (self.mapping.lookup_co(addr) if self.point_type == "co"
                else self.mapping.lookup_di(addr))

    def getValues(self, address, count=1):
        out = []
        for i in range(count):
            addr = address + i
            entry = self._lkp(addr)
            if entry is None:
                logger.warning(f"Nenhuma {self.point_type.upper()} mapeada em {addr}")
                out.append(False); continue
            if entry.dtype != "BOOL":
                logger.warning(f"{self.point_type.upper()} {addr} com tipo inválido: {entry.dtype}")
                out.append(False); continue
            try:
                out.append(bool(try_get_value(entry.rv, False)))
            except Exception as e:
                logger.error(f"Erro ao ler {self.point_type.upper()} {addr}: {e}")
                out.append(False)
        return out

    def setValues(self, address, values):
        if self.read_only:
            logger.warning(f"Escrita ignorada em {self.point_type.upper()} (RO). Addr inicial: {address}")
            return

        for i, raw in enumerate(values):
            addr = address + i
            entry = self._lkp(addr)
            if entry is None:
                logger.warning(f"Nenhuma {self.point_type.upper()} para escrita em {addr}")
                continue
            if entry.dtype != "BOOL":
                logger.warning(f"Escrita em {self.point_type.upper()} {addr} rejeitada: destino não-BOOL")
                continue
            try:
                entry.rv.setValue(bool(raw))
            except Exception as e:
                logger.error(f"Escrita {self.point_type.upper()} falhou em {addr}: {e}")


# ===========================
# Blocos concretos
# ===========================

class HRDataBlock(_BaseRegisterBlock):
    def __init__(self, unit_id: int, mapping: MappingService):
        super().__init__(unit_id, mapping, point_type="hr", read_only=False)

    def setValues(self, address, values):
        """
        FC06/FC16: percorre o range decodificando por tipo:
          - FLOAT base: consome 2 words. Low-word isolada é ignorada (consome 1 word).
          - INTEGER/UNSIGNED: consome 1 word.
          - Endereço não mapeado: consome 1 word (skip).
        """
        decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=BYTEORDER, wordorder=WORDORDER)
        addr = address
        remaining = len(values)

        while remaining > 0:
            entry = self.mapping.lookup_hr(addr)

            # Low-word de FLOAT (escrita desalinhada) é ignorada por desenho:
            if entry and entry.dtype == "FLOAT" and entry.is_low_word:
                logger.warning(f"Escrita na low-word de FLOAT em HR {addr} ignorada (use endereço base).")
                decode_skip_word(decoder)
                addr += 1
                remaining -= 1
                continue

            if entry is None:
                logger.warning(f"HR {addr} não mapeado; ignorando 1 word.")
                decode_skip_word(decoder)
                addr += 1
                remaining -= 1
                continue

            try:
                if entry.dtype == "FLOAT":
                    if remaining < 2:
                        logger.warning(f"Escrita FLOAT em HR {addr} requer 2 words (restam {remaining}). Abortando.")
                        return
                    value = decoder.decode_32bit_float()
                    if value == value and value not in (float("inf"), float("-inf")):
                        entry.rv.setValue(float(value))
                    else:
                        logger.warning(f"Valor FLOAT inválido (NaN/Inf) em HR {addr}; ignorado.")
                    addr += 2
                    remaining -= 2

                elif entry.dtype == "INTEGER":
                    value = decoder.decode_16bit_int()
                    entry.rv.setValue(int(value))
                    addr += 1
                    remaining -= 1

                elif entry.dtype == "UNSIGNED":
                    value = decoder.decode_16bit_uint()
                    entry.rv.setValue(int(value))
                    addr += 1
                    remaining -= 1

                else:
                    logger.warning(f"Tipo inválido em HR {addr}: {entry.dtype}. Consumindo 1 word.")
                    decode_skip_word(decoder)
                    addr += 1
                    remaining -= 1

            except Exception as e:
                logger.error(f"Escrita HR falhou em {addr}: {e}")
                decode_skip_word(decoder)
                addr += 1
                remaining -= 1


class IRDataBlock(_BaseRegisterBlock):
    def __init__(self, unit_id: int, mapping: MappingService):
        super().__init__(unit_id, mapping, point_type="ir", read_only=True)


class CoilDataBlock(_BaseBitBlock):
    def __init__(self, unit_id: int, mapping: MappingService):
        super().__init__(unit_id, mapping, point_type="co", read_only=False)


class DiscreteInputDataBlock(_BaseBitBlock):
    def __init__(self, unit_id: int, mapping: MappingService):
        super().__init__(unit_id, mapping, point_type="di", read_only=True)


# ===========================
# Servidor Modbus TCP
# ===========================

@dataclass
class IdentityInfo:
    vendor: str = "LASEC"
    product: str = "Transparent Simulator"
    model: str = "Transparent Model"
    version: str = "2.0"

class ModbusServer:
    """
    Servidor Modbus TCP em thread separada com shutdown limpo via stop_condition.
    """
    def __init__(self, react_factory: ReactFactory, identity: IdentityInfo | None = None):
        self.rf = react_factory
        self.mapping = MappingService(react_factory)
        self.identity = identity or IdentityInfo()

        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._port: Optional[int] = None

    # -------- ciclo de vida --------
    def start(self, port: int = 502):
        """Inicia (ou reinicia) o servidor na porta fornecida."""
        if self._thread and self._thread.is_alive():
            if self._port == port:
                logger.warning(f"Servidor já em execução na porta {port}")
                return
            self.stop()

        self.mapping.rebuild()
        self._stop_evt.clear()
        self._port = port
        self._thread = threading.Thread(target=self._run, args=(port,), daemon=True)
        self._thread.start()

    def stop(self):
        """Solicita parada e aguarda a thread terminar (shutdown limpo)."""
        if self._thread and self._thread.is_alive():
            logger.info("Sinalizando parada do Modbus...")
            self._stop_evt.set()
            # Deixe o stop_condition encerrar; não chame loop.stop() aqui.
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("Thread não encerrou no timeout. Forçando loop.stop().")
                if self._loop and self._loop.is_running():
                    try:
                        self._loop.call_soon_threadsafe(self._loop.stop)
                    except Exception as e:
                        logger.warning(f"Falha ao solicitar loop.stop(): {e}")
                self._thread.join(timeout=2.0)

    def _run(self, port: int):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            logger.info(f"Iniciando Modbus TCP em 0.0.0.0:{port}...")
            self._stop_evt.clear()
            self._loop.run_until_complete(self._start_async_server(port))
        except Exception as e:
            logger.error(f"Falha no loop principal do servidor: {e}")
        finally:
            logger.info("Encerrando loop de eventos Modbus...")
            try:
                pending = asyncio.all_tasks(self._loop)
                for t in pending:
                    t.cancel()
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as e:
                logger.warning(f"Erro ao cancelar tarefas: {e}")
            try:
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            except Exception as e:
                logger.warning(f"Erro ao encerrar asyncgens: {e}")
            self._loop.close()
            self._loop = None
            logger.info("Loop de eventos Modbus encerrado.")

    async def _start_async_server(self, port: int):
        # Cria data blocks com o serviço de mapeamento
        slaves = {
            sid: ModbusSlaveContext(
                di=DiscreteInputDataBlock(sid, self.mapping),
                co=CoilDataBlock(sid, self.mapping),
                hr=HRDataBlock(sid, self.mapping),
                ir=IRDataBlock(sid, self.mapping),
            )
            for sid in range(1, 2)  # ajuste se for usar múltiplos unit IDs
        }
        context = ModbusServerContext(slaves=slaves, single=False)

        ident = ModbusDeviceIdentification()
        ident.VendorName = self.identity.vendor
        ident.ProductName = self.identity.product
        ident.ModelName = self.identity.model
        ident.MajorMinorRevision = self.identity.version

        await StartAsyncTcpServer(
            context=context,
            identity=ident,
            address=("0.0.0.0", port),
            allow_reuse_address=True,
            stop_condition=self._stop_condition,
        )

    async def _stop_condition(self):
        """Retorna True quando _stop_evt for sinalizado (encerra o servidor)."""
        while not self._stop_evt.is_set():
            await asyncio.sleep(0.1)
        return True


# ===========================
# Exemplo de uso (opcional)
# ===========================
if __name__ == "__main__":
    rf = ReactFactory()        # adapte para seu projeto
    server = ModbusServer(rf)
    server.start(port=5020)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
