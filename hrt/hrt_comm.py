import serial
from typing import List, Optional, Callable
from conn.comm_serial import CommSerial

class HrtComm:
    def __init__(self, port: Optional[str] = None, func_read: Optional[Callable[[str], None]] = None):
        self._port: Optional[str] = port
        self.func_read: Optional[Callable[[str], None]] = func_read
        self._comm_serial = CommSerial()
        self.connect(port, func_read)

    @property
    def port(self) -> str:
        return self._port if self._port is not None else ""

    @port.setter
    def port(self, value: str):
        self._port = value

    @property
    def available_ports(self) -> List[str]:
        return self._comm_serial.available_ports

    def read_frame(self) -> str:
        resp = self._comm_serial.read_serial()
        return "".join([format(e, '02x').upper() for e in resp])

    @property
    def is_connected(self) -> bool:
        return self._comm_serial.is_open

    def write_frame(self, data: str) -> bool:
        aux = [int(data[i:i + 2], 16) for i in range(0, len(data), 2)]
        resp = bytes(aux)
        return self._comm_serial.write_serial(resp)

    def connect(self, port: Optional[str] = None, func_read: Optional[Callable[[str], None]] = None) -> bool:
        func_read_aux = func_read if func_read is not None else self.func_read
        if (port or self._port) is not None:
            def serial_read_callback(data: List[int]):
                if func_read_aux:
                    func_read_aux(
                        "".join([format(e, '02x').upper() for e in data])
                    )
            return self._comm_serial.open_serial(
                port or self._port,
                baudrate=1200,
                bytesize=8,
                parity=serial.PARITY_ODD,  # Changed to serial.PARITY_ODD
                stopbits=serial.STOPBITS_ONE,  # Changed to serial.STOPBITS_ONE
                func_read=serial_read_callback
            )
        else:
            return False

    def disconnect(self) -> bool:
        return self._comm_serial.close_serial()

def handle_data(data):
    print(f"Received data: {data}")

# Example Usage:
if __name__ == '__main__':
    # Example usage of HrtComm (replace "COM1" with your actual serial port)
    hrt_comm = HrtComm(func_read=handle_data)

    if hrt_comm.available_ports:
        port = hrt_comm.available_ports[0]
        print(f"Trying to connect to {port}")
        if hrt_comm.connect(port=port):
            print("Connected to serial port")
            frame_to_write = "0102030405"  # Example frame data
            if hrt_comm.write_frame(frame_to_write):
                print(f"Wrote frame: {frame_to_write}")
            else:
                print("Failed to write frame")
            # Data will be printed in handle_data function when received
            import time
            time.sleep(2) # wait for data
            hrt_comm.disconnect()
            print("Disconnected from serial port")
        else:
            print("Failed to connect to serial port")
    else:
        print("No serial ports found.")
