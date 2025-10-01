import re
from typing import Optional


class HrtFrame:
    def __init__(self, frame: Optional[str] = None):
        self.log: str = ""
        self.posIniFrame: int = 0
        self.preamble: str = "FFFFFFFFFF"
        self.addressType: bool = False # False - Frame Curto ou True - Frame Longo  
        self.frameType: str = "02"
        self.masterAddress: bool = True  # 1 - primary master; 0 - secondary master -> Pra quem ele esta mandando
        self.burstMode: bool = False  # 1 - in Burst Mode; 0 - not Burst Mode or Slave
        self._manufacterId: str = "00"
        self._deviceType: str = "00"
        self._deviceId: str = "00"
        self._pollingAddress: str = "00"
        self.command: str = "00"
        self._nBBody: int = 0
        self._body: str = ""
        self.checkSum: str = "00"

        if frame is not None:
            self.extractFrame(frame)

    def calcCheckSum(self, ck: str) -> str:
        """Calculates the checksum of a given string."""
        hex_values = [int(ck[i:i + 2], 16) for i in range(0, len(ck), 2)]
        checksum = 0
        for value in hex_values:
            checksum ^= value
        return hex(checksum)[2:].upper().zfill(2)

    @property
    def frame(self) -> str:
        """Returns the complete HART frame as a hexadecimal string."""
        self.log = ""
        aux = self._pacialFrame()
        ck = self.calcCheckSum(aux)
        return f'{self.preamble}{aux}{ck}'.upper()


    def _pacialFrame(self) -> str:
        """Returns the partial frame (delimiter, address, command, nBBody, body) as a hexadecimal string."""
        return f"{self.delimiter}{self.address}{self.command}{self._nBBody:02X}{self._body}"

    @frame.setter
    def frame(self, hrtFrame: str):
        """Sets the frame by extracting data from a hexadecimal string."""
        self.log = ""
        self.extractFrame(hrtFrame)

    def extractFrame(self, strFrame: str):
        """Extracts frame data from a hexadecimal string."""
        try:
            # Calcula a posIniFrame
            listFrame = " ".join([strFrame[i:i + 2] for i in range(0, len(strFrame), 2)])
            match = re.search(r'FF ([^F][A-F0-9]|[A-F0-9][^F])', listFrame)
            if match is None:
                self.log = "Don't find Preamble in Frame"
                return
            else:
                iniFrameAux = match.start()
                self.posIniFrame = (2 * iniFrameAux + 6) // 3

            ################## Preamble #######################
            self.preamble = strFrame[:self.posIniFrame]
            ################## Delimiter #######################
            self.delimiter = strFrame[self.posIniFrame:self.posIniFrame + 2]

            if not self.addressType:
                ################## Address #######################
                self.address = strFrame[self.posIniFrame + 2:self.posIniFrame + 4]
                ################## Command #######################
                self.command = strFrame[self.posIniFrame + 4:self.posIniFrame + 6]
                ################## Nbbody e o Body #######################
                # Extrai o numero de bytes do body [nbbody] e o body
                self._nBBody = int(strFrame[self.posIniFrame + 6:self.posIniFrame + 8], 16)
                self._body = strFrame[self.posIniFrame + 8:self.posIniFrame + 8 + 2 * self._nBBody]
            else:
                ################## Address #######################
                self.address = strFrame[self.posIniFrame + 2:self.posIniFrame + 12]
                ################## Command #######################
                self.command = strFrame[self.posIniFrame + 12:self.posIniFrame + 14]
                ################## Nbbody e o Body #######################
                # Extrai o numero de bytes do body [nbbody] e o body
                self._nBBody = int(strFrame[self.posIniFrame + 14:self.posIniFrame + 16], 16)
                self._body = strFrame[self.posIniFrame + 16:self.posIniFrame + 16 + 2 * self._nBBody]

            ################## CheckSum #######################
            # Extrai o CheckSum e checa se ele esta correto.
            self.checkSum = strFrame[-2:]
            if self.calcCheckSum(self._pacialFrame()) != self.checkSum:
                self.log = "Incorrect CheckSum"

        except Exception as e:
            self.log = "Incorrect hart Frame size"

    @property
    def nBBody(self) -> int:
        """Returns the number of body bytes."""
        return self._nBBody

    @property
    def body(self) -> str:
        """Returns the body of the frame."""
        return self._body

    @body.setter
    def body(self, newBody: str):
        """Sets the body of the frame and updates the number of body bytes."""
        self._nBBody = len(newBody) // 2
        self._body = newBody

    @property
    def delimiter(self) -> str:
        """Returns the delimiter of the frame."""
        value_aux = 0
        if self.addressType:
            value_aux = bit_field_set(value_aux, 7, 1)
        value_aux = bit_field_set(value_aux, 0, 3, int(self.frameType, 16))
        return f'{value_aux:02X}'

    @delimiter.setter
    def delimiter(self, newDelimiter: str):
        """Sets the delimiter of the frame and updates the address type and frame type."""
        valueAux = int(newDelimiter, 16)
        # Extrai o address type
        self.addressType = bit_field_get(valueAux, 7, 1) == 1 # False curto ou True Longo
        # Extrai o frame type
        self.frameType = f'{bit_field_get(valueAux, 0, 3):02X}' # 02 Request ou 06 Response

    @property
    def address(self) -> str:
        """Returns the address of the frame."""
        value_aux: int = 0
        if self.masterAddress:
            value_aux = bit_field_set(value_aux, 7, 1) # Master (True primário, False secundário)
        if self.burstMode:
            value_aux = bit_field_set(value_aux, 6, 1)
        if not self.addressType:
            value_aux = bit_field_set(value_aux, 0, 6, int(self.pollingAddress, 16))
            address_str = f'{value_aux:02X}'
        else:
            value_aux = bit_field_set(value_aux, 0, 6, int(self.manufacterId, 16))            
            address_str = f'{value_aux:02X}{self._deviceType}{self._deviceId}'
        return address_str

    @address.setter
    def address(self, newAddress: str):
        """Sets the address of the frame and updates the master address, burst mode, polling address, manufacturer ID, device type, and device ID."""
        id_str = newAddress[:2]
        valueAux = int(id_str, 16)
        # Extrai o master_slave
        self.masterAddress = bit_field_get(valueAux, 7, 1) == 1 # Master (True primário, False secundário)
        # Extrai o Burst Mode
        self.burstMode = bit_field_get(valueAux, 6, 1) == 1
            
        if not self.addressType:
            # Extrai o polling_address            
            self._pollingAddress = f'{bit_field_get(valueAux, 0, 6):02X}'
            self._manufacterId = ""
            self._deviceType = ""
            self._deviceId = ""
        else:
            # Extrai o manufacter_id
            self._pollingAddress = ""
            self._manufacterId = f'{bit_field_get(valueAux, 0, 6):02X}'
            self._deviceType = newAddress[2:4]
            self._deviceId = newAddress[4:10]

    @property
    def pollingAddress(self) -> str:
        """Returns the polling address."""
        return self._pollingAddress

    @pollingAddress.setter
    def pollingAddress(self, newPollingAddress: str):
        """Sets the polling address, ensuring it is coherent with the address type."""
        if not self.addressType and len(newPollingAddress) == 2:
            self._pollingAddress = newPollingAddress
        else:
            self.log = "pollingAddress incoerent with addressType"

    @property
    def manufacterId(self) -> str:
        """Returns the manufacturer ID."""
        return self._manufacterId

    @manufacterId.setter
    def manufacterId(self, newManufacterId: str):
        """Sets the manufacturer ID, ensuring it is coherent with the address type."""
        if self.addressType and len(newManufacterId) == 2:
            self._manufacterId = newManufacterId
        else:
            self.log = "manufacterId incoerent with addressType"

    @property
    def deviceType(self) -> str:
        """Returns the device type."""
        return self._deviceType

    @deviceType.setter
    def deviceType(self, newDeviceType: str):
        """Sets the device type, ensuring it is coherent with the address type."""
        if self.addressType and len(newDeviceType) == 2:
            self._deviceType = newDeviceType
        else:
            self.log = "deviceType incoerent with addressType"

    @property
    def deviceId(self) -> str:
        """Returns the device ID."""
        return self._deviceId

    @deviceId.setter
    def deviceId(self, newDeviceId: str):
        """Sets the device ID, ensuring it is coherent with the address type."""
        if self.addressType and len(newDeviceId) == 6:
            self._deviceId = newDeviceId
        else:
            self.log = "deviceId incoerent with addressType"


def bit_field_get(value: int, start_bit: int, length: int) -> int:
    """Extracts a bit field from an integer value."""
    mask = ((1 << length) - 1) << start_bit
    return (value & mask) >> start_bit


def bit_field_set(value: int, start_bit: int, length: int, new_value: int = 1) -> int:
    """Sets a bit field in an integer value."""
    mask = ((1 << length) - 1) << start_bit
    value &= ~mask  
    value |= (new_value << start_bit) & mask  # Set the bits
    return value


# Example usage:
if __name__ == '__main__':
    # Create a new HrtFrame object
    frame = HrtFrame()

    # Set some properties
    frame.addressType = False
    frame.pollingAddress = "1A"
    frame.command = "01"
    frame.body = "00"

    # Print the generated frame
    print("Generated frame:", frame.frame)

    # Create a HrtFrame object from an existing frame string
    existing_frame = "FFFFFFFFFF021A0102003D"
    frame2 = HrtFrame(existing_frame)

    # Print the extracted properties
    print("Extracted address:", frame2.address)
    print("Extracted command:", frame2.command)
    print("Extracted body:", frame2.body)
    print("Log:", frame2.log)
