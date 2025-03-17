from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt.old.hrt_settings import hrt_settings
from asteval import Interpreter
from react.reactiveVariable import ReactiveVariable 
from ctrl.simul_tf import SimulTf
from typing import Union
import numpy as np
import pandas as pd
import re
class HrtData(Storage):
    def __init__(self):
        super().__init__('db/banco.db', 'hrt_tabela')  # 🔥 Chama o construtor da classe Pai quando sqlite
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        mask = np.char.startswith(self.df.values.astype(str), "$")
        # Obtendo os índices das células que satisfazem a condição
        rows, cols = np.where(mask)
        # Mapeando para os nomes reais de linhas e colunas
        row_names = self.df.index[rows].tolist()
        col_names = self.df.columns[cols].tolist()
        # Inicializando o dicionario com os resultados das tf
        self.tf_dict = {(row, col): 0 for row in row_names for col in col_names}
    
    def getModel(self, value: str) -> str:   
        if value.startswith('@'):
            return "Func"
        elif value.startswith('$'):
            return "tFunc"
        else:
            return "Value"
               
    def getDataModel(self, rowName: str, colName: str) -> str:
        value = super().get_variable(rowName,colName)
        return self.getModel(self, value)
    
    def getShape(self):
        return self.df.shape
        
    def get_variable(self, id_variable: str, instrument: str, machineValue: bool = True):
        if id_variable == instrument or instrument == 'NAME':
            return id_variable
        else: 
            value = super().get_variable(id_variable, instrument)
            dataModel = self.getDataModel(id_variable, instrument)
            if not instrument in ["NAME", "TYPE", "BYTE_SIZE"]:
                if dataModel == "Func":
                    return self._evaluate_expression(value, id_variable, instrument, machineValue)
                elif dataModel == "tFunc": 
                    if not machineValue:
                        return hrt_type_hex_to(self.tf_dict[id_variable, instrument], super().get_variable(id_variable, "TYPE"))
                    else:
                        return self.tf_dict[id_variable, instrument]
                elif not machineValue:
                    return hrt_type_hex_to(super().get_variable(id_variable, instrument), super().get_variable(id_variable, "TYPE"))
            return value

    def set_variable(self, value, id_variable: str, instrument: str, machineValue:bool = True):
        if id_variable == instrument or instrument == 'NAME':
            self.df.loc[id_variable,0] = value
        else:
            modelAntes = self.getDataModel(id_variable, instrument).find("tFunc") != -1 # Se antes era tf
            modelAgora = self.getModel(value).find("tFunc") != -1 # Se agora é tf
            if not modelAntes and modelAgora: self.tf_dict[id_variable, instrument] = 0
            if modelAntes and not modelAgora: self.tf_dict.pop((id_variable, instrument), None)
            if machineValue or self.getDataModel(id_variable, instrument).find("Func") != -1:
                return super().set_variable(id_variable, instrument, str(value))
            else:
                return super().set_variable(id_variable, instrument, hrt_type_hex_from(value, super().get_variable(id_variable, "TYPE"), int(super().get_variable(id_variable, "BYTE_SIZE"))))
    
    def _evaluate_expression(self, func: str, id_variable: str, instrument: str, machineValue: bool = True) -> Union[float, str]:
        evaluator = Interpreter()
        func = func[1:]  # Remove o caractere '@' inicial
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