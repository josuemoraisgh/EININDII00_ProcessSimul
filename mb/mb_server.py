from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.datastore import ModbusSequentialDataBlock as BaseModbusDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartTcpServer
from pymodbus.constants import Endian
from react.react_var import ReactVar
from react.react_factory import ReactFactory
from PySide6.QtCore import QThread
import asyncio

class InvalidDataBlock(BaseModbusDataBlock):
    """Data block que rejeita qualquer leitura ou escrita."""
    def __init__(self):
        super().__init__(0, [0])

    def validate(self, address, count=1):
        return False

    def getValues(self, address, count=1):
        raise NotImplementedError("Tipo de dado inválido.")

    def setValues(self, address, values):
        raise NotImplementedError("Tipo de dado inválido.")

class DynamicDataBlock(BaseModbusDataBlock):
    """Data block que lê/escreve diretamente de/agora ReactVar já inicializados."""
    def __init__(self, slave_id: int, reactFactory: ReactFactory, point_type: str):
        super().__init__(0, [0])
        self.slave_id = slave_id
        self.reactFactory = reactFactory
        self.point_type = point_type  # 'hr' ou 'ir'

    def validate(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        df = self.reactFactory.df.get("MODBUS")
        if df is None:
            return [0] * count

        for addr in range(address, address + count):
            mask_addr = df["ADDRESS"].apply(lambda a: a._value == f"{addr:02}")
            mask_pt   = df["MB_POINT"].apply(lambda a: a._value == self.point_type)
            mask = mask_addr & mask_pt
            if not mask.any():
                builder.add_16bit_int(0)
                continue

            col_idx = df.columns.get_loc("PROCESS_VARIABLE")
            data: ReactVar = df.loc[mask].iloc[0, col_idx]
            val = data._value
            dtype = data.type()

            if dtype == "FLOAT":
                builder.add_32bit_float(val)
            elif dtype == "INTEGER":
                builder.add_16bit_int(val)
            else:
                builder.add_16bit_uint(val)

        return builder.to_registers()

    def setValues(self, address, values):
        decoder = BinaryPayloadDecoder.fromRegisters(values,
            byteorder=Endian.Big, wordorder=Endian.Big)
        df = self.reactFactory.df.get("MODBUS")
        if df is None:
            return
        mask = (
            df["ADDRESS"].apply(lambda a: a._value == f"{address:02}") &
            df["MB_POINT"].apply(lambda a: a._value == "hr")
        )
        if not mask.any():
            return

        col_idx = df.columns.get_loc("PROCESS_VARIABLE")
        data: ReactVar = df.loc[mask].iloc[0, col_idx]
        dtype = data.type()
        try:
            if dtype == "FLOAT" and len(values) >= 2:
                valor = decoder.decode_32bit_float()
                data.setValue(valor)
            elif dtype == "INTEGER" and len(values) >= 1:
                valor = decoder.decode_16bit_int()
                data.setValue(valor)
            else:
                valor = decoder.decode_16bit_uint()
                data.setValue(valor)
        except Exception as e:
            print(f"[WARN] Erro ao decodificar/escrever em {address}: {e}")

class ModbusServerThread(QThread):
    """Thread que executa um servidor Modbus TCP baseado em dados dinâmicos do ReactFactory."""
    def __init__(self, reactFactory: ReactFactory, num_slaves=1, address="0.0.0.0", port=5020):
        super().__init__()
        self.reactFactory = reactFactory
        self.num_slaves = num_slaves
        self.address = address
        self.port = port
        self.loop = None
        self.server = None

    async def _start_server(self):
        slaves = {}
        for sid in range(1, self.num_slaves + 1):
            slaves[sid] = ModbusSlaveContext(
                di=InvalidDataBlock(),
                co=InvalidDataBlock(),
                hr=DynamicDataBlock(sid, self.reactFactory, "hr"),
                ir=DynamicDataBlock(sid, self.reactFactory, "ir")
            )
        context = ModbusServerContext(slaves=slaves, single=False)
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'LASEC'
        identity.ProductName = 'Transparent Simulator'
        identity.ModelName = 'Transparent Model'
        identity.MajorMinorRevision = '2.0'

        await StartTcpServer(
            context=context,
            identity=identity,
            address=(self.address, self.port),
            allow_reuse_address=True,
            defer_start=False
        )

    def run(self):
        print(f"Iniciando Modbus TCP em {self.address}:{self.port}...")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server())
        self.loop.run_forever()

    def stop(self):
        if self.loop and self.loop.is_running():
            print("Encerrando Modbus...")
            self.loop.call_soon_threadsafe(self.loop.stop)