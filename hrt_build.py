from hrt_transmitter import HrtTransmitter
from hrt_frame import HrtFrame

class HrtBuild:
    def __init__(self, hrt_transmitter, hrt_frame_read):
        self._hrt_frame_write = HrtFrame()
        self._hrt_frame_write.command = hrt_frame_read.command
        self._hrt_frame_write.address_type = hrt_frame_read.address_type
        hrt_transmitter.set_variable('address_type', ('00' if hrt_frame_read.address_type == False else '80'))
        self._hrt_frame_write.frame_type = hrt_transmitter.get_variable('frame_type')
        self._hrt_frame_write.master_address = (True if hrt_transmitter.get_variable('master_address') == "00" else False)

        if self._hrt_frame_write.address_type:
            self._hrt_frame_write.manufacter_id = hrt_transmitter.get_variable('manufacturer_id')
            self._hrt_frame_write.device_type = hrt_transmitter.get_variable('device_type')
            self._hrt_frame_write.device_id = hrt_transmitter.get_variable('device_id')
        else:
            self._hrt_frame_write.polling_address = hrt_transmitter.get_variable('polling_address')

            if self._hrt_frame_write.frame_type == "02":
                self._request(hrt_transmitter, hrt_frame_read)
            else:
                self._response(hrt_transmitter, hrt_frame_read)

    @property
    def frame(self):
        return self._hrt_frame_write.frame

    def _request(self, hrt_transmitter, hrt_frame_read):
        command = hrt_frame_read.command
        if command == '00':  # Identity Command
            self._hrt_frame_write.body = ""
        elif command == '01':  # Read Primary Variable
            self._hrt_frame_write.body = ""
        elif command == '02':  # Read Loop Current And Percent Of Range
            self._hrt_frame_write.body = ""
        elif command == '03':  # Read Dynamic Variables And Loop Current
            self._hrt_frame_write.body = ""
        elif command == '04':
            self._hrt_frame_write.body = ""
        elif command == '05':
            self._hrt_frame_write.body = ""
        elif command == '06':  # Write Polling Address
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('polling_address')}{hrt_transmitter.get_variable('loop_current_mode')}"
        elif command == '07':  # Read Loop Configuration
            self._hrt_frame_write.body = ""
        elif command == '08':  # Read Dynamic Variable Classifications
            self._hrt_frame_write.body = ""
        elif command == '09':  # Read Device Variables with Status
            self._hrt_frame_write.body = ""
        elif command == '10':  #
            self._hrt_frame_write.body = ""
        elif command == '11':  # Read Unique Identifier Associated With Tag
            self._hrt_frame_write.body = hrt_transmitter.get_variable('tag')
        elif command == '0C':  # Read Message (12)
            self._hrt_frame_write.body = ""
        elif command == '0D':  # Read Tag, Descriptor, Date (13)
            self._hrt_frame_write.body = ""
        elif command == '21':  # Read Device Variables (33)
            self._hrt_frame_write.body = ""

    def _response(self, hrt_transmitter, hrt_frame_read):
        command = hrt_frame_read.command
        if command == '00':  # Identity Command
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += "FE"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('master_address') | hrt_transmitter.get_variable('manufacturer_id')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_type')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('request_preambles')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('hart_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('software_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('transmitter_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('hardware_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_flags')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_id')}"
        elif command == '01':  # Read Primary Variable
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('unit_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('PROCESS_VARIABLE')}"
        elif command == '02':  # Read Loop Current And Percent Of Range
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('loop_current')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('percent_of_range')}"
        elif command == '03':  # Read Dynamic Variables And Loop Current
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('loop_current')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('unit_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('PROCESS_VARIABLE')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('unit_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('PROCESS_VARIABLE')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('unit_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('PROCESS_VARIABLE')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('unit_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('PROCESS_VARIABLE')}"
        elif command == '04':  #
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
        elif command == '05':  #
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
        elif command == '06':  # Write Polling Address
            polling_address = hrt_frame_read.body[:2]
            loop_current_mode = hrt_frame_read.body[2:]
            hrt_transmitter.set_variable('polling_address', polling_address)
            hrt_transmitter.set_variable('loop_current_mode', loop_current_mode)
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{polling_address}"
            self._hrt_frame_write.body += f"{loop_current_mode}"
        elif command == '07':  # Read Loop Configuration
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('polling_address')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('loop_current_mode')}"
        elif command == '08':  # Read Dynamic Variable Classifications
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('primary_variable_classification')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('secondary_variable_classification')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('tertiary_variable_classification')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('quaternary_variable_classification')}"
        elif command == '09':  # Read Device Variables with Status
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
        elif command == '0A':  # (10)
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
        elif command == '0B':  # Read Unique Identifier Associated With Tag (11)
            self._hrt_frame_write.body = "00" if (
                hrt_frame_read.body == hrt_transmitter.get_variable('tag')) else '01'
            self._hrt_frame_write.body += "FE"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('master_slave') | hrt_transmitter.get_variable('manufacturer_id')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_type')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('request_preambles')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('hart_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('software_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('transmitter_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('hardware_revision')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_flags')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('device_id')}"
        elif command == '0C':  # Read Message (12)
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('message')}"
        elif command == '0D':  # Read Tag, Descriptor, Date (13)
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('tag')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('descriptor')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('date')}"
        elif command == '0E':  # Read Primary Variable Transducer Information (14)
            self._hrt_frame_write.body = '00000000002044548000C348000041200000'
        elif command == '0F':  # Read Device Information (15)
            self._hrt_frame_write.body = '01002343BA933342924CCC3F800000013E'
        elif command == '10':  # Read Final Assembly Number (16)
            self._hrt_frame_write.body = f"{hrt_transmitter.get_variable('error_code')}"
            self._hrt_frame_write.body += f"{hrt_transmitter.get_variable('final_assembly_number')}"
        elif command == '11':  # Write Message (17)
            self._hrt_frame_write.body = ''
        elif command == '12':  # Write Tag, Descriptor, Date (18)
            self._hrt_frame_write.body = ''
        elif command == '13':  # Comand 13 - Write Final Assembly Number (19)
            self._hrt_frame_write.body = ''
        elif command == '21':  # Read Device Variables (33)
            body = hrt_frame_read.body
            if body == '00':
                self._hrt_frame_write.body = '0000002740EE2D42'
            elif body == '01':
                self._hrt_frame_write.body = '0000013941AC26AA'
            elif body == '02':
                self._hrt_frame_write.body = '0000022041CF9540'
            elif body == '03':
                self._hrt_frame_write.body = '0000032041C8D990'
            elif body == '04':
                self._hrt_frame_write.body = '0000043941AC2621'
            elif body == '05':
                self._hrt_frame_write.body = '0000053900000000'
            elif body == '0C':
                self._hrt_frame_write.body = '00000C333F800000'
            elif body == '19':
                self._hrt_frame_write.body = '0040190042DD261B'
            else:
                self._hrt_frame_write.body = '000000007FA00000'
        elif command == '26':  # Resetar as Flags de Erro (38)
            self._hrt_frame_write.body = '020000E63F3F'
        elif command == '28':  # Enter/Exit Fixed Current Mode (40)
            self._hrt_frame_write.body = '2806004000000000'
        elif command == '29':  # Perform Self Test (41)
            self._hrt_frame_write.body = '4020'
        elif command == '2A':  # Perform Device Reset (42)
            self._hrt_frame_write.body = '0000'
        elif command == '2D':  # Trim/Adjusting the 4 mA (45)
            self._hrt_frame_write.body = '0900'
        elif command == '2E':  # Trim/Adjusting the 20 mA (46)
            self._hrt_frame_write.body = '0900'
        elif command == '50':  # Read Dynamic Variable Assignments (80)
            self._hrt_frame_write.body = '5000'
        elif command == '82':  # Write Device Variable Trim Point (130)
            self._hrt_frame_write.body = '00000201020101'
        elif command == '84':  # Comando 132 -
            self._hrt_frame_write.body = '000002012543D2000040A99999'
        elif command == '87':  # Write I/O System Master Mode (135)
            self._hrt_frame_write.body = '00400201'
        elif command == '88':  # Comando 136 -
            self._hrt_frame_write.body = '700002FFFFFF'
        elif command == '8A':  # Comando 8A -
            self._hrt_frame_write.body = '000002FF'
        elif command == '8C':  # Comando 8C -
            self._hrt_frame_write.body = '7000023941AC33E939000000003942480000FFFF3900000000'
        elif command == '98':  # Comando 98 -
            self._hrt_frame_write.body = ''
        elif command == 'A2':  # Comando A2 -
            self._hrt_frame_write.body = '00000201'
        elif command == 'A4':  # Comando A4 -
            self._hrt_frame_write.body = '0000020200'
        elif command == 'A6':  # Comando A6 -
            self._hrt_frame_write.body = '00000222040000130A270000010B00'
        elif command == 'A8':  # Comando A8 -
            self._hrt_frame_write.body = '00000201FF'
        elif command == 'AD':  # Comando AD -
            self._hrt_frame_write.body = '0000025454333031313131302D425549314C335030543459'
        elif command == 'B9':  # Comando B9 -
            self._hrt_frame_write.body = '004002'
        elif command == 'BB':  # Comando BB -
            self._hrt_frame_write.body = '000002FF'
        elif command == 'C6':  # Comando C6 -
            self._hrt_frame_write.body = '00000242480000'
        elif command == 'DF':  # Comando DF -
            self._hrt_frame_write.body = '00000242C800003B801132B51B057FAC932D1D'

# Example usage (assuming you have instances of HrtTransmitter and HrtFrame)
hrt_transmitter = HrtTransmitter('TIT100','dados.xlsx')
hrt_frame_read = HrtFrame()
hrt_frame_read.command = '00'
hrt_frame_read.address_type = False

hrt_build = HrtBuild(hrt_transmitter, hrt_frame_read)
print(hrt_build.frame)