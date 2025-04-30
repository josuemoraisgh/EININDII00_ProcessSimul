from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.datastore import ModbusSequentialDataBlock as BaseModbusDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.constants import Endian
from react.react_var import ReactVar
from react.react_factory import ReactFactory
from PySide6.QtCore import QThread
import asyncio

class InvalidDataBlock(BaseModbusDataBlock):
    def __init__(self):
        super().__init__(0, [0])
    def validate(self, address, count=1):
        return False
    def getValues(self, address, count=1):
        raise NotImplementedError("Tipo de dado inválido.")
    def setValues(self, address, values):
        raise NotImplementedError("Tipo de dado inválido.")

class DynamicDataBlock(BaseModbusDataBlock):
    def __init__(self, slave_id: int, reactFactory: ReactFactory, point_type: str):
        super().__init__(0, [0])
        self.slave_id = slave_id
        self.reactFactory = reactFactory
        self.point_type = point_type

    def validate(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        df = self.reactFactory.df.get("MODBUS")
        addr = address
        end = address + count
        while addr < end:
            addr_str = f"{addr:02}"
            row = df.loc[
                (df["ADDRESS"].apply(lambda a: a and a._value == addr_str)) &
                (df["MB_POINT"].apply(lambda a: a and a._value.lower() == self.point_type.lower()))
            ]
            if row.empty:
                builder.add_16bit_int(0)
                addr += 1
                continue
            data = row.iloc[0].get("CLP100")
            if not isinstance(data, ReactVar):
                builder.add_16bit_int(0)
                addr += 1
                continue
            val = data._value or 0
            dtype = data.type()
            try:
                if dtype == "FLOAT":
                    builder.add_32bit_float(float(val))
                    addr += 2
                elif dtype == "INTEGER":
                    builder.add_16bit_int(int(val))
                    addr += 1
                elif dtype == "UNSIGNED":
                    builder.add_16bit_uint(int(val))
                    addr += 1
                else:
                    builder.add_16bit_int(0)
                    addr += 1
            except Exception:
                builder.add_16bit_int(0)
                addr += 1
        return builder.to_registers()

    def setValues(self, address, values):
        decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=Endian.Big)
        df = self.reactFactory.df.get("MODBUS")
        if df is None:
            return
        row = df.loc[
            (df["ADDRESS"].apply(lambda a: a and a._value == f"{address:02}")) &
            (df["MB_POINT"].apply(lambda a: a and a._value.lower() == "hr"))
        ]
        if row.empty:
            return
        data = row.iloc[0].get("CLP100")
        if not isinstance(data, ReactVar):
            return
        dtype = data.type()
        try:
            if dtype == "FLOAT" and len(values) >= 2:
                data.setValue(decoder.decode_32bit_float())
            elif dtype == "INTEGER":
                data.setValue(decoder.decode_16bit_int())
            elif dtype == "UNSIGNED":
                data.setValue(decoder.decode_16bit_uint())
        except Exception:
            pass

class ModbusServerThread(QThread):
    def __init__(self, reactFactory: ReactFactory, num_slaves=1, address="0.0.0.0", port=502):
        super().__init__()
        self.reactFactory = reactFactory
        self.num_slaves = num_slaves
        self.address = address
        self.port = port
        self._should_stop = False
        self.loop = None

    def run(self):
        asyncio.run(self._run_server_forever())

    async def _run_server_forever(self):
        self.loop = asyncio.get_event_loop()
        print(f"[START] Iniciando Modbus TCP em {self.address}:{self.port}...")
        slaves = {
            sid: ModbusSlaveContext(
                di=InvalidDataBlock(),
                co=InvalidDataBlock(),
                hr=DynamicDataBlock(sid, self.reactFactory, "hr"),
                ir=DynamicDataBlock(sid, self.reactFactory, "ir")
            ) for sid in range(1, self.num_slaves + 1)
        }
        context = ModbusServerContext(slaves=slaves, single=False)
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'LASEC'
        identity.ProductName = 'Transparent Simulator'
        identity.ModelName = 'Transparent Model'
        identity.MajorMinorRevision = '2.0'

        await StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=(self.address, self.port),
            defer_start=False,
            serve_forever=False
        )

        while not self._should_stop:
            await asyncio.sleep(0.5)

        print("[STOP] Encerrando Modbus...")

    def stop(self):
        self._should_stop = True