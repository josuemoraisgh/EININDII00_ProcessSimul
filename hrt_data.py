from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import hrt_settings
import re
from asteval import Interpreter
from typing import Union


class HrtData:
    def __init__(self, instrument: str, caminho_excel: str):
        self._instrument = instrument
        self.HrtStorage = HrtStorage(caminho_excel)
        
    def setInstrument(self, instrument: str):
        self._instrument = instrument
        
    def keys(self):
        return self.HrtStorage.keys()
    
    def get_variable(self, id_variable: str, machineValue: bool = True):
        value = self.HrtStorage.get_variable(id_variable, self._instrument)    
        if value.startswith('@'):
            return self._evaluate_expression(value, machineValue)
        else:    
            if machineValue:
                return value
            else:
                return hrt_type_hex_to(self.HrtStorage.get_variable(id_variable, self._instrument), self.HrtStorage.get_variable(id_variable, "Tipo"))

    def set_variable(self, id_variable: str, value: str ,machineValue: bool = True):
        if machineValue:
            return self.HrtStorage.set_variable(id_variable, self._instrument, value)
        else:
            return self.HrtStorage.set_variable(id_variable, self._instrument, hrt_type_hex_from(value, self.HrtStorage.get_variable(id_variable, "Tipo")))
    
    def _evaluate_expression(self, id_variable: str, func: str, machineValue: bool = True) -> Union[float, str]:
        evaluator = Interpreter()
        expr_str = func[1:]  # Remove o caractere '@' inicial
        tokens = re.findall(r'[A-Za-z_]\w*', expr_str)
        context = {}
        for token in tokens:
            var_val = self.get_variable(token, False)
            if var_val is not None:
                evaluator.symtable[token] = var_val
        try:
            result = evaluator(expr_str)
            if not machineValue:
                return result
            else:
                return hrt_type_hex_from(result, self.HrtStorage.get_variable(id_variable, "Tipo")).zfill(self.HrtStorage.get_variable(id_variable, "Tamanho"))
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if not machineValue:
                return 0.0
            else:
                return "0.0"


# Exemplo de uso
if __name__ == '__main__':
    hrtData = HrtData('TIT100','dados.xlsx')

    # Definir variável para o instrumento TIT100
    for key in hrtData.keys():
        try:
            hrtData.HrtStorage.set_variable(key, "Tipo", hrt_settings[key][1])
            hrtData.set_variable(key, hrt_settings[key][2], machineValue=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = hrtData.get_variable('tag')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")