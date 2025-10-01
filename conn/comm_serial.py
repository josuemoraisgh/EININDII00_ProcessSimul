import sys
import re
import ctypes
from ctypes import wintypes
import threading
import time
import serial
import serial.tools.list_ports

class CommSerial:
    def __init__(self):
        self._sp = None
        self._reader_thread = None
        self._reader_callback = None
        self._stop_reader = threading.Event()

    # ---------------------- UTIL ----------------------
    @staticmethod
    def _is_windows():
        return sys.platform.startswith("win")

    @staticmethod
    def _normalize_port_name(port_name: str) -> str:
        """
        No Windows, portas não-COM (ex.: CNCA0) precisam do prefixo '\\\\.\\'.
        COMx pode ser usado normalmente. Em outros SOs, retorna como veio.
        """
        if not CommSerial._is_windows():
            return port_name
        up = port_name.upper()
        if up.startswith("COM"):
            return port_name  # 'COM11', etc.
        # CNCA0/CNCB0/nomes simbólicos
        if not port_name.startswith(r"\\.\\"[0:2]):  # evita duplicar se já vier com \\.\...
            return r'\\.\\' + port_name
        return port_name

    @staticmethod
    def _map_bytesize(val):
        # aceita 5..8 ou constants
        if isinstance(val, int):
            mapping = {
                5: serial.FIVEBITS,
                6: serial.SIXBITS,
                7: serial.SEVENBITS,
                8: serial.EIGHTBITS
            }
            return mapping.get(val, serial.EIGHTBITS)
        return val

    @staticmethod
    def _map_parity(val):
        # aceita 'N','E','O','M','S' ou constants
        if isinstance(val, str):
            up = val.upper()
            return {
                'N': serial.PARITY_NONE,
                'E': serial.PARITY_EVEN,
                'O': serial.PARITY_ODD,
                'M': serial.PARITY_MARK,
                'S': serial.PARITY_SPACE
            }.get(up, serial.PARITY_NONE)
        return val

    @staticmethod
    def _map_stopbits(val):
        # aceita 1, 1.5, 2 ou constants
        if isinstance(val, (int, float)):
            if float(val) == 1.0:
                return serial.STOPBITS_ONE
            if float(val) == 1.5:
                return serial.STOPBITS_ONE_POINT_FIVE
            if float(val) == 2.0:
                return serial.STOPBITS_TWO
        return val

    # ---------------------- LISTAGEM ----------------------
    @staticmethod
    def _pyserial_ports_dict():
        d = {}
        for p in serial.tools.list_ports.comports():
            d[p.device.upper()] = p.device
        return d

    @staticmethod
    def _qdd_ports_dict_windows():
        """
        Usa QueryDosDeviceW para listar devices DOS (inclui CNCA0/CNCB0).
        Filtra padrões de portas úteis. Só Windows.
        """
        QDD = ctypes.windll.kernel32.QueryDosDeviceW
        QDD.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        QDD.restype = wintypes.DWORD

        size = 32768  # buffer grande
        buf = ctypes.create_unicode_buffer(size)
        rc = QDD(None, buf, size)
        if rc == 0:
            # se falhar, retorna vazio (sem quebrar)
            return {}

        names = [s for s in buf[:rc].split('\x00') if s]
        pat = re.compile(r"^(COM\d+|CNC[A-Z]\d+)$", re.IGNORECASE)  # COMx e CNCA0/CNCB0...
        d = {}
        for n in names:
            if pat.match(n):
                d[n.upper()] = n
        return d

    @property
    def available_ports(self):
        """
        Retorna lista de portas (strings):
        - Primeiro as não-COM (ex.: CNCA0/CNCB0)
        - Depois as COMx
        Sem entradas vazias e sem duplicatas.
        """
        py = self._pyserial_ports_dict()
        if self._is_windows():
            qdd = self._qdd_ports_dict_windows()
            # merge de chaves (UPPER) -> nome mostrado
            merged = {}
            merged.update(qdd)  # garante não-COM presentes
            merged.update(py)   # se também existir via pyserial, mantém nome do pyserial

            # ordenar: não-COM primeiro (k.startswith("COM") == False => 0), depois COM (True => 1)
            ordered_keys = sorted(merged.keys(), key=lambda k: (k.startswith("COM"), k))

            # montar lista final, sem vazios e sem duplicar (case-insensitive)
            out, seen = [], set()
            for k in ordered_keys:
                name = merged.get(k)
                if not name:
                    continue
                u = name.upper()
                if u not in seen:
                    out.append(name)
                    seen.add(u)
            return out
        else:
            # Em Unix, ficar só com o que o pyserial enxerga, ordenado e limpo
            vals = [v for v in py.values() if v]
            # remover duplicatas preservando ordem
            out, seen = [], set()
            for name in sorted(vals):
                u = name.upper()
                if u not in seen:
                    out.append(name)
                    seen.add(u)
            return out


    @property
    def is_open(self):
        """Retorna True se a porta serial estiver aberta."""
        return self._sp is not None and self._sp.is_open

    # ---------------------- LEITURA ASSÍNCRONA ----------------------
    def listen_reader(self, data_func):
        """Configura o callback para receber dados e inicia uma thread de leitura."""
        self._reader_callback = data_func
        if self._reader_thread is None or not self._reader_thread.is_alive():
            self._stop_reader.clear()
            self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self._reader_thread.start()

    def _reader_loop(self):
        """Loop interno que verifica e lê dados da porta serial, chamando o callback."""
        while not self._stop_reader.is_set():
            if self.is_open:
                try:
                    bytes_available = self._sp.in_waiting
                    if bytes_available:
                        data = self._sp.read(bytes_available)
                        if data and self._reader_callback:
                            self._reader_callback(data)
                    else:
                        # leitura mínima não bloqueante (timeout=0), só para captar bytes soltos
                        data = self._sp.read(1)
                        if data and self._reader_callback:
                            self._reader_callback(data + self._sp.read(self._sp.in_waiting))
                except serial.SerialException:
                    # porta caiu? encerra leitura
                    self._stop_reader.set()
                    break
            time.sleep(0.01)  # 10 ms

    # ---------------------- ABRIR/FECHAR/IO ----------------------
    def open_serial(self, port, baudrate=9600, bytesize=8, parity='N', stopbits=1, func_read=None):
        """
        Abre a porta serial especificada com os parâmetros de configuração.
        Aceita COMx e não-COM (ex.: CNCA0) no Windows.
        """
        try:
            if self._sp is not None and self._sp.is_open:
                self._sp.close()

            port_norm = self._normalize_port_name(port)
            self._sp = serial.Serial(
                port=port_norm,
                baudrate=int(baudrate),
                bytesize=self._map_bytesize(bytesize),
                parity=self._map_parity(parity),
                stopbits=self._map_stopbits(stopbits),
                timeout=0  # não bloqueante para o loop de leitura
            )

            if func_read is not None:
                self.listen_reader(func_read)

            return True
        except serial.SerialException as e:
            print("Erro ao abrir porta serial:", e)
            self._sp = None
            return False

    def close_serial(self):
        """Fecha a porta serial e encerra a thread de leitura."""
        if self._sp is not None:
            if self._sp.is_open:
                self._stop_reader.set()
                self._sp.close()
                if self._reader_thread is not None:
                    self._reader_thread.join(timeout=1)
                return True
        return False

    def read_serial(self):
        """Lê os dados disponíveis na porta serial."""
        if self._sp is not None and self._sp.is_open:
            try:
                n = self._sp.in_waiting
                if n:
                    return self._sp.read(n)
            except serial.SerialException as e:
                print("Erro ao ler da porta serial:", e)
        return b''

    def write_serial(self, write_data: bytes):
        """
        Escreve bytes na porta serial.
        Retorna True se todos os bytes foram enviados.
        """
        if self._sp is not None and self._sp.is_open and write_data:
            try:
                written = self._sp.write(write_data)
                return written >= len(write_data)
            except serial.SerialException as e:
                print("Erro ao escrever na porta serial:", e)
        return False


# --- Exemplo de uso ---
if __name__ == "__main__":
    def callback(data: bytes):
        print("Recebido:", data)

    comm = CommSerial()
    print("Portas disponíveis:", comm.available_ports)

    # Troque pelo nome desejado, ex.: "CNCA0" (Windows, com0com) ou "COM6"
    target_port = "CNCA0"  # ou "COM6", "/dev/ttyUSB0", etc.

    if comm.open_serial(port=target_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, func_read=callback):
        print("Porta serial aberta com sucesso:", target_port)
        time.sleep(0.5)

        if comm.write_serial(b'Hello, Serial!'):
            print("Dados enviados com sucesso.")
        else:
            print("Falha ao enviar dados.")

        time.sleep(2)
        comm.close_serial()
        print("Porta serial fechada.")
    else:
        print("Falha ao abrir a porta serial:", target_port)