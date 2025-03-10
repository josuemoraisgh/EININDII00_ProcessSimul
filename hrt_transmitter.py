from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import hrt_settings

class HrtTransmitter:
    def __init__(self, instrument: str, caminho_excel: str):
        self._instrument = instrument
        self.HrtStorage = HrtStorage(caminho_excel)
    
    def setInstrument(self, instrument: str):
        self._instrument = instrument
    
    def keys(self):
        return self.HrtStorage.keys()

    def get_variable(self, id_variable: str, valueInHex: bool = False):
        if valueInHex:
            return hrt_type_hex_from(self.HrtStorage.get_variable(id_variable, self._instrument), self.HrtStorage.get_variable(id_variable, "Tipo"))
        else:
            return self.HrtStorage.get_variable(id_variable, self._instrument)

    def set_variable(self, id_variable: str, value: str ,valueIsHex: bool = False):
        if valueIsHex:
            return self.HrtStorage.set_variable(id_variable, self._instrument, hrt_type_hex_to(value, self.HrtStorage.get_variable(id_variable, "Tipo")))
        else:
            return self.HrtStorage.set_variable(id_variable, self._instrument, value)


# Exemplo de uso
if __name__ == '__main__':
    transmitter = HrtTransmitter('TIT100','dados.xlsx')

    # Definir variável para o instrumento TIT100
    for key in transmitter.keys():
        try:
            transmitter.HrtStorage.set_variable(key, "Tipo", hrt_settings[key][1])
            transmitter.set_variable(key, hrt_settings[key][2], valueIsHex=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = transmitter.get_variable('tag')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")