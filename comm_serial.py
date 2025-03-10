import serial
import serial.tools.list_ports
import threading
import time

class CommSerial:
    def __init__(self):
        self._sp = None
        self._reader_thread = None
        self._reader_callback = None
        self._stop_reader = threading.Event()

    @property
    def available_ports(self):
        """Retorna a lista de portas seriais disponíveis."""
        return [port.device for port in serial.tools.list_ports.comports()]

    @property
    def is_open(self):
        """Retorna True se a porta serial estiver aberta."""
        return self._sp is not None and self._sp.is_open

    def listen_reader(self, data_func):
        """Configura o callback para receber dados e inicia uma thread para leitura."""
        self._reader_callback = data_func
        if self._reader_thread is None or not self._reader_thread.is_alive():
            self._stop_reader.clear()
            self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self._reader_thread.start()

    def _reader_loop(self):
        """Loop interno que verifica e lê dados da porta serial, chamando o callback."""
        while not self._stop_reader.is_set():
            if self.is_open:
                # Lê os bytes disponíveis; se nenhum byte estiver disponível, lê 1 (timeout curto)
                bytes_available = self._sp.in_waiting
                if bytes_available:
                    data = self._sp.read(bytes_available)
                    if data and self._reader_callback:
                        self._reader_callback(data)
            time.sleep(0.01)  # Aguarda 10ms para evitar consumo excessivo de CPU

    def open_serial(self, port, baudrate=9600, bytesize=8, parity='N', stopbits=1, func_read=None):
        """
        Abre a porta serial especificada com os parâmetros de configuração.
        
        :param port: Nome da porta (ex.: "COM3" ou "/dev/ttyUSB0").
        :param baudrate: Baud rate desejado.
        :param bytesize: Número de bits de dados (normalmente 8).
        :param parity: Paridade ('N' = None, 'E' = Even, 'O' = Odd).
        :param stopbits: Número de stop bits (1 ou 2).
        :param func_read: Função callback que receberá os dados lidos (tipo bytes).
        :return: True se a porta for aberta com sucesso, False caso contrário.
        """
        try:
            # Se já houver uma porta aberta, fecha-a
            if self._sp is not None and self._sp.is_open:
                self._sp.close()
            self._sp = serial.Serial(port,
                                     baudrate=baudrate,
                                     bytesize=bytesize,
                                     parity=parity,
                                     stopbits=stopbits,
                                     timeout=0)
            if func_read is not None:
                self.listen_reader(func_read)
            return True
        except serial.SerialException as e:
            print("Erro ao abrir porta serial:", e)
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
        """
        Lê os dados disponíveis na porta serial.
        
        :return: Dados lidos (bytes) ou uma sequência vazia se não houver dados.
        """
        if self._sp is not None and self._sp.is_open:
            bytes_available = self._sp.in_waiting
            if bytes_available:
                return self._sp.read(bytes_available)
        return b''

    def write_serial(self, write_data):
        """
        Escreve os dados fornecidos na porta serial.
        
        :param write_data: Dados a serem enviados (do tipo bytes).
        :return: True se a quantidade de bytes escritos for igual ao tamanho de write_data, False caso contrário.
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
    def callback(data):
        print("Recebido:", data)

    comm = CommSerial()
    print("Portas disponíveis:", comm.available_ports)
    
    # Altere "COM3" para a porta desejada (ex.: "/dev/ttyUSB0" em sistemas Unix)
    if comm.open_serial(port="COM6", baudrate=9600, bytesize=8, parity='N', stopbits=1, func_read=callback):
        print("Porta serial aberta com sucesso.")
        time.sleep(2)
        
        # Exemplo: escrever dados
        if comm.write_serial(b'Hello, Serial!'):
            print("Dados enviados com sucesso.")
        else:
            print("Falha ao enviar dados.")
        
        # Aguarda alguns segundos para receber dados
        time.sleep(5)
        comm.close_serial()
        print("Porta serial fechada.")
    else:
        print("Falha ao abrir a porta serial.")
