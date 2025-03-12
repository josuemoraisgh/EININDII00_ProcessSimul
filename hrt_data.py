from hrt_storage import HrtStorage  # Assuming hrt_storage.py exists
from hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt_settings import hrt_settings
from asteval import Interpreter
from typing import Union
import re
class HrtData(HrtStorage):
    def __init__(self, caminho_excel: str):
        super().__init__(caminho_excel)  # 🔥 Chama o construtor da classe Pai
        
    def keys(self):
        return super().keys()

    def get_variable_with_pos(self, row: int, col: int, machineValue: bool = True):
        """Atualiza o DataFrame quando a célula for alterada."""
        return self.get_variable(self.df.iloc[row, 0], self.df.keys()[col], machineValue)
   
    def set_variable_with_pos(self, value, row: int, col: int, machineValue: bool = True):
        """Atualiza o DataFrame quando a célula for alterada."""
        return self.set_variable(value, self.df.iloc[row, 0], self.df.keys()[col], machineValue)

    def get_variable(self, id_variable: str, instrument: str, machineValue: bool = True):
        if id_variable == instrument or instrument == 'NAME':
            return id_variable
        else: 
            value = super().get_variable(id_variable, instrument) 
            if str(value).startswith('@'):
                return self._evaluate_expression(value, id_variable, instrument, machineValue)
            else:    
                if machineValue:
                    return value
                else:
                    return hrt_type_hex_to(super().get_variable(id_variable, instrument), super().get_variable(id_variable, "TYPE"))

    def set_variable(self, value, id_variable: str, instrument: str, machineValue:bool = True):
        if id_variable == instrument or instrument == 'NAME':
            self.df.loc[id_variable,0] = value
        else:
            if machineValue:
                return super().set_variable(id_variable, instrument, str(value))
            else:
                return super().set_variable(id_variable, instrument, hrt_type_hex_from(value, super().get_variable(id_variable, "TYPE")))
        
    def _evaluate_expression(self, func: str, id_variable: str, instrument: str, machineValue: bool = True) -> Union[float, str]:
        evaluator = Interpreter()
        expr_str = func[1:]  # Remove o caractere '@' inicial
        tokens = re.findall(r'[A-Za-z_]\w*', expr_str)
        context = {}
        for token in tokens:
            var_val = self.get_variable(token, instrument, False)
            if var_val is not None:
                evaluator.symtable[token] = var_val
        try:
            result = evaluator(expr_str)
            if not machineValue:
                return result
            else:
                return hrt_type_hex_from(result, super().get_variable(id_variable, "TYPE")).zfill(super().get_variable(id_variable, "BYTE_SIZE"))
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if not machineValue:
                return 0.0
            else:
                return "0.0"


# Exemplo de uso
if __name__ == '__main__':
    hrtData = HrtData('dados.xlsx')

    # Definir variável para o instrumento TIT100
    for key in hrtData.keys():
        try:
            hrtData.set_variable(hrt_settings[key][1], key, "TYPE", machineValue=True)
            hrtData.set_variable(hrt_settings[key][2], key, "TIT100", machineValue=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    # Definir variável para o instrumento TIT100
    valor = hrtData.get_variable('tag', "TIT100")
    print(f"Valor obtido para 'input_value' em LD301: {valor}")