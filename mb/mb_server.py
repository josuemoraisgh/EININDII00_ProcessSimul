from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from pymodbus.transaction import ModbusSocketFramer
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore.context import ModbusServerContext
import random

class DynamicModbusServer:
    def __init__(self, address="0.0.0.0", port=5020):
        self.address = address
        self.port = port

    def get_context(self):
        # Criando valores dinâmicos para os registros de Holding
        dynamic_values = {i: random.randint(1000, 9999) for i in range(10)}
        
        store = ModbusSlaveContext(
            di=None,  # Discrete Inputs (não usado)
            co=None,  # Coils (não usado)
            hr=dynamic_values,  # Registros de Holding dinâmicos
            ir=None   # Input Registers (não usado)
        )
        return ModbusServerContext(slaves={0x00: store}, single=False)

    def start(self):
        identity = ModbusDeviceIdentification()
        self.identity.VendorName = 'Laboratório de Automação Sistemas Eletrônicos e Controle'
        self.identity.ProductCode = 'LASEC'
        self.identity.VendorUrl = 'http://www.lasec.feelt.ufu.br/'
        self.identity.ProductName = 'Process Simulater'
        self.identity.ModelName = 'Modelo X'
        self.identity.MajorMinorRevision = '0.1'

        # Inicia o servidor sem um contexto fixo
        StartTcpServer(context=None, identity=identity, address=(self.address, self.port),
                       framer=ModbusSocketFramer, custom_functions=None,
                       server_context_factory=self.get_context)

if __name__ == "__main__":
    server = DynamicModbusServer()
    server.start()
    
    
# from pymodbus.server import StartTcpServer
# from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
# from pymodbus.datastore.store import BaseModbusDataBlock
# from pymodbus.device import ModbusDeviceIdentification
# import random

# class DynamicDataBlock(BaseModbusDataBlock):
#     def getValues(self, address, count=1):
#         # Valores dinâmicos gerados em tempo real
#         print(f"Solicitação recebida no endereço: {address}")
#         return [random.randint(1000, 9999) for _ in range(count)]

#     def setValues(self, address, values):
#         print(f"Escrita solicitada no endereço: {address} com valores: {values}")

# class DynamicModbusServer:
#     def __init__(self, address="0.0.0.0", port=5020):
#         self.address = address
#         self.port = port

#         store = ModbusSlaveContext(
#             di=DynamicDataBlock(),  # Discrete Inputs (não usado)
#             co=DynamicDataBlock(),  # Coils (não usado)
#             hr=DynamicDataBlock(),  # Registradores Holding dinâmicos
#             ir=DynamicDataBlock()   # Input Registers (não usado)
#         )
#         self.context = ModbusServerContext(slaves=store, single=True)

#     def start(self):
#         identity = ModbusDeviceIdentification()
#         identity.VendorName = 'Laboratório de Automação Sistemas Eletrônicos e Controle'
#         identity.ProductCode = 'LASEC'
#         identity.VendorUrl = 'http://www.lasec.feelt.ufu.br/'
#         identity.ProductName = 'Process Simulator'
#         identity.ModelName = 'Modelo X'
#         identity.MajorMinorRevision = '0.1'

#         print(f"Iniciando servidor Modbus TCP em {self.address}:{self.port}...")
#         StartTcpServer(context=self.context, identity=identity, address=(self.address, self.port))

# if __name__ == "__main__":
#     server = DynamicModbusServer()
#     server.start()
