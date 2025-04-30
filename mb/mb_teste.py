from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

# Configurações
SERVER_IP = "127.0.0.1"
SERVER_PORT = 502
SLAVE_ID = 1

# Mapas válidos informados
HR_ADDRS = range(1, 4)   # HR: 1 a 3
IR_ADDRS = range(1, 9)   # IR: 1 a 8

def test_read(client, address, count, ir=False):
    try:
        if ir:
            response = client.read_input_registers(address=address, count=count, slave=SLAVE_ID)
        else:
            response = client.read_holding_registers(address=address, count=count, slave=SLAVE_ID)
        
        if not response.isError():
            return response.registers
        else:
            print(f"[❌] Erro ao ler {'IR' if ir else 'HR'} addr={address}: {response}")
            return None
    except ModbusIOException as e:
        print(f"[❌] IOEX ao ler {'IR' if ir else 'HR'} addr={address}: {e}")
        return None

def test_write(client, address, value):
    try:
        result = client.write_register(address=address, value=value, slave=SLAVE_ID)
        if result.isError():
            print(f"[❌] Falha ao escrever HR addr={address}: {result}")
            return False
        return True
    except Exception as e:
        print(f"[❌] Exceção ao escrever addr={address}: {e}")
        return False

def main():
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)
    if not client.connect():
        print("[❌] Falha ao conectar ao servidor Modbus.")
        return

    print(f"[ℹ️] Testando leitura de Holding Registers (HR): {list(HR_ADDRS)}")
    for addr in HR_ADDRS:
        values = test_read(client, addr, 1, ir=False)
        if values is not None:
            print(f"[✅] HR[{addr}] = {values[0]}")
    
    print(f"\n[ℹ️] Testando leitura de Input Registers (IR): {list(IR_ADDRS)}")
    for addr in IR_ADDRS:
        values = test_read(client, addr, 1, ir=True)
        if values is not None:
            print(f"[✅] IR[{addr}] = {values[0]}")

    print(f"\n[🛠] Testando escrita em Holding Registers (HR)")
    for addr in HR_ADDRS:
        test_val = addr * 10
        if test_write(client, addr, test_val):
            read_back = test_read(client, addr, 1, ir=False)
            if read_back and read_back[0] != test_val:
                print(f"[⚠️] Divergência HR[{addr}]: escrito={test_val} lido={read_back[0]}")
            else:
                print(f"[✅] Escrita HR[{addr}] = {test_val} confirmada")

    client.close()
    print("\n[✔️] Testes concluídos.")

if __name__ == "__main__":
    main()