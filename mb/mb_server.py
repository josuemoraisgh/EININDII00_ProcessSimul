from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer
from pymodbus.constants import Endian
from react.react_var import ReactVar
from PySide6.QtCore import QThread
from react.react_db import ReactDB
import random

class InvalidDataBlock(BaseModbusDataBlock):
    def validate(self, address, count=1):
        return False

    def getValues(self, address, count=1):
        raise NotImplementedError("Tipo de dado inválido.")

    def setValues(self, address, values):
        raise NotImplementedError("Tipo de dado inválido.")

from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pymodbus.datastore import ModbusSequentialDataBlock as BaseModbusDataBlock

class DynamicDataBlock(BaseModbusDataBlock):
    def __init__(self, slave_id, reactDB):
        super().__init__(0x00, [0]*100)  # inicialização base fictícia
        self.reactDB = reactDB
        self.slave_id = slave_id

    def validate(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        addr = address
        for i in range(count):
            try:
                # Filtra linha correspondente ao endereço atual e ponto "hr"
                row = self.reactDB.df["MODBUS"].query(f'ADDRESS == "{addr}" and MB_POINT == "hr"')
                if row.empty:
                    builder.add_16bit_int(0)  # valor default caso não encontre
                    continue

                data: ReactVar = row.iloc[0, 5]  # índice 5: coluna com ReactVar
                data_value = data.getValue()
                data_type = data.type()
                addr = addr + (data.byteSize()/2)
                if data_type == "REAL":
                    builder.add_32bit_float(data_value)
                elif data_type == "INTEGER":
                    builder.add_32bit_int(data_value)
                elif data_type == "STRING":
                    builder.add_string(data_value.encode("ascii"))
                else:  # UNSIGNED ou outros tipos
                    builder.add_32bit_uint(data_value)

            except Exception as e:
                print(f"Erro ao processar endereço {addr}: {e}")
                builder.add_16bit_int(0)

        return builder.to_registers()

    def setValues(self, address, data_Value):
        decoder = BinaryPayloadDecoder.fromRegisters(data_Value, byteorder=Endian.Big, wordorder=Endian.Big)

        try:
            row = self.reactDB.df["MODBUS"].query(f'ADDRESS == "{address}" and MB_POINT == "hr"')
            if row.empty:
                print(f"[WARN] Endereço {address} não encontrado.")
                return

            data: ReactVar = row.iloc[0, 5]
            data_type = data.type()

            if data_type == "REAL" and len(data_Value) >= 2:
                valor_float = decoder.decode_32bit_float()
                data.setValue(valor_float)

            elif data_type == "INTEGER" and len(data_Value) >= 2:
                valor_int = decoder.decode_32bit_int()
                data.setValue(valor_int)

            elif data_type == "STRING" and len(data_Value) >= 4:
                valor_str = decoder.decode_string(8).decode('ascii').strip()
                data.setValue(valor_str)

            elif data_type == "UNSIGNED" and len(data_Value) >= 2:
                valor_uint = decoder.decode_32bit_uint()
                data.setValue(valor_uint)

            else:
                print(f"[WARN] Tipo desconhecido ou dados insuficientes para o endereço {address}.")

        except Exception as e:
            print(f"[ERRO] Erro ao definir valor no endereço {address}: {e}")

# --- Classe para rodar o servidor em thread ---
class ModbusServerThread(QThread):
    def __init__(self, reactDB: ReactDB, num_slaves=3, address="0.0.0.0", port=5020):
        super().__init__()
        self.reactDB = reactDB
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
                hr=DynamicDataBlock(slave_id, self.reactDB), # MV
                ir=DynamicDataBlock(slave_id, self.reactDB) # PV
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
