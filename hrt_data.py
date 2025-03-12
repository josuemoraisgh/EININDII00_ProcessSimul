from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import hrt_settings
import re
from asteval import Interpreter
from typing import Union
class HrtData(HrtStorage):
    def __init__(self, caminho_excel: str, instrument: str):
        super().__init__(caminho_excel)  # 🔥 Chama o construtor da classe Pai
        self._instrument = instrument
        
    def setInstrument(self, instrument: str):
        self._instrument = instrument
        
    def keys(self):
        return super().keys()
    
    def get_dataframe(self, machineValue: bool = True):
        return super().df

    def set_pos_datframe(self, row, col, value, machineValue: bool = True):
        """Atualiza o DataFrame quando a célula for alterada."""
        return 0.0
   
    def get_variable(self, id_variable: str, machineValue: Union[bool, str] = True):
        if type(machineValue) == str:
            return super().get_variable(id_variable, machineValue) 
        else: 
            value = super().get_variable(id_variable, self._instrument) 
        if value.startswith('@'):
            return self._evaluate_expression(value, machineValue)
        else:    
            if machineValue:
                return value
            else:
                return hrt_type_hex_to(self.HrtStorage.get_variable(id_variable, self._instrument), self.HrtStorage.get_variable(id_variable, "Tipo"))

    def set_variable(self, value: str , id_variable: str, machineValue: Union[bool, str] = True):
        if type(machineValue) == str:
            return super().set_variable(id_variable, machineValue, value)
        else:
            if machineValue:
                return super().set_variable(id_variable, self._instrument, value)
            else:
                return super().set_variable(id_variable, self._instrument, hrt_type_hex_from(value, super().get_variable(id_variable, "Tipo")))
        
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
                return hrt_type_hex_from(result, super().get_variable(id_variable, "Tipo")).zfill(super().get_variable(id_variable, "Tamanho"))
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if not machineValue:
                return 0.0
            else:
                return "0.0"


# Exemplo de uso
if __name__ == '__main__':
    hrtData = HrtData('dados.xlsx','TIT100')

    # Definir variável para o instrumento TIT100
    for key in hrtData.keys():
        try:
            hrtData.set_variable(hrt_settings[key][1], key, "Tipo")
            hrtData.set_variable(hrt_settings[key][2], key, machineValue=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = hrtData.get_variable('tag')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")