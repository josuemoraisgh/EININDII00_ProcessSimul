import asyncio
import threading
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.datastore import ModbusSequentialDataBlock as BaseModbusDataBlock
from react.react_var import ReactVar
from react.react_factory import ReactFactory

class InvalidDataBlock(BaseModbusDataBlock):
    def __init__(self):
        super().__init__(0, [0])

    def validate(self, address, count=1): return False
    def getValues(self, address, count=1): raise NotImplementedError("Tipo inválido")
    def setValues(self, address, values): raise NotImplementedError("Tipo inválido")

class DynamicDataBlock(BaseModbusDataBlock):
    def __init__(self, slave_id: int, reactFactory: ReactFactory, point_type: str):
        super().__init__(0, [0])
        self.slave_id = slave_id
        self.reactFactory = reactFactory
        self.point_type = point_type

    def validate(self, address, count=1): return True

    def getValues(self, address, count=1):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        df = self.reactFactory.df.get("MODBUS")

        addr = address
        while addr < address + count:
            addr_str = f"{addr:02}"
            row = df.loc[
                (df["ADDRESS"].apply(lambda a: a and a._value == addr_str)) &
                (df["MB_POINT"].apply(lambda a: a and a._value.lower() == self.point_type.lower()))
            ]

            if row.empty or "CLP100" not in row.columns:
                print(f"[WARN] Nenhuma variável CLP100 encontrada no endereço {addr}")
                builder.add_16bit_int(0)
                addr += 1
                continue

            data = row.iloc[0]["CLP100"]
            if not isinstance(data, ReactVar):
                print(f"[WARN] CLP100 no endereço {addr} não é ReactVar")
                builder.add_16bit_int(0)
                addr += 1
                continue

            val = data._value if data._value is not None else 0
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
                    print(f"[WARN] Tipo desconhecido '{dtype}' em {addr}")
                    builder.add_16bit_int(0)
                    addr += 1
            except Exception as e:
                print(f"[ERRO] Erro ao ler {addr}: {e}")
                builder.add_16bit_int(0)
                addr += 1

        return builder.to_registers()

    def setValues(self, address, values):
        df = self.reactFactory.df.get("MODBUS")
        decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=Endian.Big)
        row = df.loc[
            (df["ADDRESS"].apply(lambda a: a and a._value == f"{address:02}")) &
            (df["MB_POINT"].apply(lambda a: a and a._value.lower() == "hr"))
        ]
        if row.empty or "CLP100" not in row.columns:
            print(f"[WARN] Nenhuma variável hr encontrada para {address}")
            return

        data = row.iloc[0]["CLP100"]
        if not isinstance(data, ReactVar):
            print(f"[WARN] CLP100 não é ReactVar em {address}")
            return

        dtype = data.type()
        try:
            if dtype == "FLOAT" and len(values) >= 2:
                data.setValue(decoder.decode_32bit_float())
            elif dtype == "INTEGER":
                data.setValue(decoder.decode_16bit_int())
            elif dtype == "UNSIGNED":
                data.setValue(decoder.decode_16bit_uint())
            else:
                print(f"[WARN] Escrita inválida em {address}: tipo={dtype}")
        except Exception as e:
            print(f"[ERRO] Escrita falhou em {address}: {e}")

class ModbusServer:
    def __init__(self, reactFactory: ReactFactory):
        self.reactFactory = reactFactory
        self._server_thread = None
        self._stop_event = threading.Event()
        self._loop = None
        self._current_port = None

    def start(self, port=502):
        if self._server_thread and self._server_thread.is_alive():
            if self._current_port == port:
                print(f"[WARN] Servidor já em execução na porta {port}")
                return
            else:
                print(f"[INFO] Reiniciando servidor em nova porta {port}")
                self.stop()
        self._stop_event.clear()
        self._current_port = port
        self._server_thread = threading.Thread(target=self._run, args=(port,), daemon=True)
        self._server_thread.start()

    def stop(self):
        if self._loop and self._loop.is_running():
            print("[CMD] Sinalizando parada do Modbus...")
            self._stop_event.set()
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._server_thread.join()
            print("[INFO] Servidor parado.")

    def _run(self, port):
        asyncio.run(self._start_async_server(port))

    async def _start_async_server(self, port):
        self._loop = asyncio.get_event_loop()
        print(f"[START] Iniciando Modbus TCP em 0.0.0.0:{port}...")
        print("[INFO] Criando slaves Modbus...")
        slaves = {
            sid: ModbusSlaveContext(
                di=InvalidDataBlock(),
                co=InvalidDataBlock(),
                hr=DynamicDataBlock(sid, self.reactFactory, "hr"),
                ir=DynamicDataBlock(sid, self.reactFactory, "ir")
            ) for sid in range(1, 2)
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
            address=("0.0.0.0", port),
            allow_reuse_address=True,
            stop_condition=self._check_stop
        )

    async def _check_stop(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(0.1)
        return True