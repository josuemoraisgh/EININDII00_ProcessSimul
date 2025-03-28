from PySide6.QtCore import QThread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import random

class InvalidDataBlock(BaseModbusDataBlock):
    def validate(self, address, count=1):
        return False

    def getValues(self, address, count=1):
        raise NotImplementedError("Tipo de dado inválido.")

    def setValues(self, address, values):
        raise NotImplementedError("Tipo de dado inválido.")

class DynamicDataBlockHR(BaseModbusDataBlock):
    def __init__(self, slave_id):
        super().__init__()
        self.slave_id = slave_id

    def validate(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        data_Value = 0.0
        data_type = "REAL"       
        if data_type == "REAL":
            builder.add_32bit_float(data_Value)
            return builder.to_registers()
        elif data_type == "INTEGER":
            builder.add_32bit_int(data_Value)
            return builder.to_registers()
        elif data_type == "STRING":
            builder.add_string(data_Value.encode("ascii"))
            return builder.to_registers()
        else: # UNSIGNED
            return data_Value

    def setValues(self, address, data_Value):
        data_type = "REAL" 
        decoder = BinaryPayloadDecoder.fromRegisters(data_Value, byteorder=Endian.Big, wordorder=Endian.Big)
        if data_type == "REAL" and len(data_Value) >= 2:
            valor_float = decoder.decode_32bit_float()
            # self.values[0] = valor_float
        elif data_type == "INTEGER" and len(data_Value) >= 2:
            valor_int = decoder.decode_32bit_int()
            # self.values[10] = valor_int
        elif data_type == "STRING" and len(data_Value) >= 4:
            valor_str = decoder.decode_string(8).decode('ascii')
            # self.values[20] = valor_str

class DynamicDataBlockIR(BaseModbusDataBlock):
    def __init__(self, slave_id):
        super().__init__()
        self.slave_id = slave_id

    def validate(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        return [random.randint(1000, 9999) + (self.slave_id * 10000) for _ in range(count)]

    def setValues(self, address, values):
        print(f"Slave {self.slave_id} escreveu valores {values} no endereço {address}")

# --- Classe para rodar o servidor em thread ---
class ModbusServerThread(QThread):
    def __init__(self, num_slaves=3, address="0.0.0.0", port=5020):
        super().__init__()
        self.num_slaves = num_slaves
        self.address = address
        self.port = port
        self._running = False

    def run(self):
        slaves = {}
        for slave_id in range(1, self.num_slaves + 1):
            slaves[slave_id] = ModbusSlaveContext(
                di=InvalidDataBlock(),
                co=InvalidDataBlock(),
                hr=DynamicDataBlockHR(slave_id), # MV
                ir=DynamicDataBlockIR(slave_id) # PV
            )

        context = ModbusServerContext(slaves=slaves, single=False)

        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Laboratório de Automação Sistemas Eletrônicos e Controle'
        identity.ProductCode = 'LASEC'
        identity.VendorUrl = 'http://www.lasec.feelt.ufu.br/'
        identity.ProductName = 'Transparent Simulator'
        identity.ModelName = 'Transparent Model'
        identity.MajorMinorRevision = '2.0'

        print(f"Iniciando servidor Modbus TCP em thread com {self.num_slaves} slaves em {self.address}:{self.port}...")
        self._running = True
        StartTcpServer(context=context, identity=identity, address=(self.address, self.port))

    def stop(self):
        if self.isRunning():
            self.terminate()  # Termina a thread
            self.wait()
            print("Servidor Modbus encerrado.")

# --- Exemplo simples de uso ---
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
    import sys

    app = QApplication(sys.argv)

    janela = QWidget()
    janela.setWindowTitle("Modbus Server em Thread")

    servidor_thread = ModbusServerThread(num_slaves=3, port=5020)

    def iniciar_servidor():
        if not servidor_thread.isRunning():
            servidor_thread.start()
            print("Servidor iniciado.")

    def parar_servidor():
        servidor_thread.stop()

    botao_iniciar = QPushButton("Iniciar Servidor")
    botao_parar = QPushButton("Parar Servidor")

    botao_iniciar.clicked.connect(iniciar_servidor)
    botao_parar.clicked.connect(parar_servidor)

    layout = QVBoxLayout(janela)
    layout.addWidget(botao_iniciar)
    layout.addWidget(botao_parar)

    janela.show()

    sys.exit(app.exec())
