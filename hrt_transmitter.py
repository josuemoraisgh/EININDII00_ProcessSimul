from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import instrument_type, hrt_settings

class HrtTransmitter:
    def __init__(self, caminho_excel: str):
        self.HrtStorage = HrtStorage(caminho_excel)
    
    def keys(self):
        return self.HrtStorage.keys()

    def get_variable(self, id_variable: str, instrument: str, isHex: bool = False):
        if isHex:
            return hrt_type_hex_from(self.HrtStorage.get_variable(id_variable, instrument), self.HrtStorage.get_variable(id_variable, "Tipo"))
        else:
            return self.HrtStorage.get_variable(id_variable, instrument)

    def set_variable(self, id_variable: str, instrument: str, value: str ,valueIsHex: bool = False):
        if valueIsHex:
            return self.HrtStorage.set_variable(id_variable, instrument, hrt_type_hex_to(value, self.HrtStorage.get_variable(id_variable, "Tipo")))
        else:
            return self.HrtStorage.set_variable(id_variable, instrument, value)


# Exemplo de uso
if __name__ == '__main__':
    transmitter = HrtTransmitter('dados.xlsx')

    # Definir variável para o instrumento TIT100
    for key in transmitter.keys():
        try:
            transmitter.set_variable(key, "Tipo", hrt_settings[key][1], valueIsHex=False)
            transmitter.set_variable(key, 'TIT100', hrt_settings[key][2], valueIsHex=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = transmitter.get_variable('tag', 'TI100')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")