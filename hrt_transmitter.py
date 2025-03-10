from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists

class HrtTransmitter:
    def __init__(self, caminho_excel: str):
        self.HrtStorage = HrtStorage(caminho_excel)
    
    def keys(self):
        return self.HrtStorage.keys()

    def get_variable(self, id_variable: str, instrument: str, isHex: bool = False):
        if isHex:
            return hrt_type_hex_from(self.get_variable(id_variable, instrument), self.get_variable(id_variable, "Tipo"))
        else:
            return self.get_variable(id_variable, instrument)

    def set_variable(self, id_variable: str, instrument: str, value: str ,valueIsHex: bool = False):
        if valueIsHex:
            return self.set_variable(id_variable, instrument, hrt_type_hex_to(value, self.get_variable(id_variable, "Tipo")))
        else:
            return self.set_variable(id_variable, instrument, value)


# Exemplo de uso
if __name__ == '__main__':
    transmitter = HrtTransmitter('dados.xlsx')

    # Definir variável para o instrumento LD301
    transmitter.set_variable('device_id', 'TI100', '001E66', valueIsHex=True),

    # Obter variável do instrumento LD301
    valor = transmitter.get_variable('tag', 'PI100')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")