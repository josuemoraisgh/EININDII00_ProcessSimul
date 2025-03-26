from PySide6.QtCore import QThread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.device import ModbusDeviceIdentification
import random

# --- Seus DataBlocks personalizados ---
class InvalidDataBlock(BaseModbusDataBlock):
    def validate(self, address, count=1):
        return False

    def getValues(self, address, count=1):
        raise NotImplementedError("Tipo de dado inválido.")

    def setValues(self, address, values):
        raise NotImplementedError("Tipo de dado inválido.")

class DynamicDataBlock(BaseModbusDataBlock):
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
                hr=DynamicDataBlock(slave_id),
                ir=DynamicDataBlock(slave_id)
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
