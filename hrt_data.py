from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import hrt_settings

class HrtData:
    def __init__(self, instrument: str, caminho_excel: str):
        self._instrument = instrument
        self.HrtStorage = HrtStorage(caminho_excel)
    
    def setInstrument(self, instrument: str):
        self._instrument = instrument
    
    def keys(self):
        return self.HrtStorage.keys()

    def get_variable(self, id_variable: str, valueInHex: bool = False):
        if valueInHex:
            return self.HrtStorage.get_variable(id_variable, self._instrument)
        else:
            return hrt_type_hex_to(self.HrtStorage.get_variable(id_variable, self._instrument), self.HrtStorage.get_variable(id_variable, "Tipo"))

    def set_variable(self, id_variable: str, value: str ,valueIsHex: bool = False):
        if valueIsHex:
            return self.HrtStorage.set_variable(id_variable, self._instrument, value)
        else:
            return self.HrtStorage.set_variable(id_variable, self._instrument, hrt_type_hex_from(value, self.HrtStorage.get_variable(id_variable, "Tipo")))

# Exemplo de uso
if __name__ == '__main__':
    hrtData = HrtData('TIT100','dados.xlsx')

    # Definir variável para o instrumento TIT100
    for key in hrtData.keys():
        try:
            hrtData.HrtStorage.set_variable(key, "Tipo", hrt_settings[key][1])
            hrtData.set_variable(key, hrt_settings[key][2], valueIsHex=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = hrtData.get_variable('tag')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")