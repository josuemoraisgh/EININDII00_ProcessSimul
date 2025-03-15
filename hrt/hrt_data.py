from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt.old.hrt_settings import hrt_settings
from asteval import Interpreter
from ctrl.simul_tf import TransferFunction as tf
from typing import Union
import re
class HrtData(Storage):
    def __init__(self):
        super().__init__('db/banco.db', 'hrt_tabela')  # 🔥 Chama o construtor da classe Pai quando sqlite
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        
    def keys(self):
        return super().keys()

    def get_variable_with_pos(self, row: int, col: int, machineValue: bool = True):
        """Atualiza o DataFrame quando a célula for alterada."""
        return self.get_variable(self.get_dataframe().iloc[row, 0], self.keys()[col], machineValue)
   
    def set_variable_with_pos(self, value, row: int, col: int, machineValue: bool = True):
        """Atualiza o DataFrame quando a célula for alterada."""
        return self.set_variable(value, self.get_dataframe().iloc[row, 0], self.keys()[col], machineValue)

    def get_variable(self, id_variable: str, instrument: str, machineValue: bool = True):
        if id_variable == instrument or instrument == 'NAME':
            return id_variable
        else: 
            value = super().get_variable(id_variable, instrument)
            type = super().get_variable(id_variable, "TYPE")
            if not instrument in ["NAME", "TYPE", "BYTE_SIZE"]:
                if str(type).startswith('@'):
                    return self._evaluate_expression(value, id_variable, instrument, machineValue)
                elif str(type).startswith('$'):   
                    return self._evaluate_expression(value, id_variable, instrument, machineValue)
                elif not machineValue:
                    return hrt_type_hex_to(super().get_variable(id_variable, instrument), type)
            return value

    def set_variable(self, value, id_variable: str, instrument: str, machineValue:bool = True):
        if id_variable == instrument or instrument == 'NAME':
            self.df.loc[id_variable,0] = value
        else:
            if machineValue:
                return super().set_variable(id_variable, instrument, str(value))
            else:
                return super().set_variable(id_variable, instrument, hrt_type_hex_from(value, super().get_variable(id_variable, "TYPE"), int(super().get_variable(id_variable, "BYTE_SIZE"))))
        
    def _evaluate_expression(self, func: str, id_variable: str, instrument: str, machineValue: bool = True) -> Union[float, str]:
        evaluator = Interpreter()
        # expr_str = func[1:]  # Remove o caractere '@' inicial
        tokens = re.findall(r'[A-Za-z_]\w*', func)
        for token in tokens:
            # Fazer no futuro: Checar se todas as variaves são do mesmo tipo ?
            var_val = self.get_variable(token, instrument, False)
            if var_val is not None:
                evaluator.symtable[token] = var_val
        try:
            result = evaluator(func)
            if not machineValue:
                return result
            else:
                return hrt_type_hex_from(result, super().get_variable(id_variable, "TYPE"), int(super().get_variable(id_variable, "BYTE_SIZE")))
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if not machineValue:
                return 0.0
            else:
                return "0.0"


# Exemplo de uso
if __name__ == '__main__':
    hrtData = HrtData()
    hrtData.data_updated.connect(lambda: print("Dados foram atualizados!"))
    # Definir variável para o instrumento TIT100
    # for key in hrtData.keys():
    #     try:
    #         hrtData.set_variable(hrt_settings[key][1], key, "TYPE", machineValue=True)
    #         hrtData.set_variable(hrt_settings[key][2], key, "TIT100", machineValue=True)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
        # Definir variável para o instrumento LD301
    hrtData.set_variable('4.0', 'PROCESS_VARIABLE', 'TIT100', machineValue=False)
    # Definir variável para o instrumento TIT100
    valor = hrtData.get_variable('PROCESS_VARIABLE', "TIT100", machineValue=False)
    print(f"Valor obtido para 'PROCESS_VARIABLE' em LD301: {valor}")