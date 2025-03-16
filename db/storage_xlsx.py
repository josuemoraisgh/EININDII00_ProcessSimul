from functools import reduce
from PySide6.QtCore import Signal, QObject
import pandas as pd
import operator

class Storage(QObject):
    data_updated = Signal()  # 🔥 Declarando o sinal corretamente
    
    def __init__(self, caminho_excel: str):
        super().__init__()  # 🔥 Inicializa QObject explicitamente        
        self.caminho_excel = caminho_excel
        try:
            #self.df = pd.read_excel(self.caminho_excel, skiprows=2) # , usecols=lambda x: x not in ['A']
            #self.df = self.df.iloc[:, 1:]
            self.df = pd.read_excel(self.caminho_excel, index_col=0)
        except FileNotFoundError:
            # Se o arquivo não existir, cria uma tabela vazia
            self.df = pd.DataFrame(columns=["NAME", "BYTE_SIZE", "TYPE", "TIT100"])
            self.saveAllData()
    
    def get_dataframe(self):
        return self.df
    
    def saveAllData(self):
        """Escreve os dados de volta ao arquivo Excel."""
        self.df.to_excel(self.caminho_excel, index=False)
        self.data_updated.emit()  # Emite o sinal de atualização              
        
    def rowKeys(self):
        return self.df.iloc[0].tolist()

    def colKeys(self):
        return self.df.columns.tolist()
    
    def get_variable(self, id_variable: str, column: str) -> str:
        # Identifica o operador bitwise e separa as variáveis
        if '|' in id_variable:
            variables = id_variable.split(' | ')
            operation = operator.or_
        elif '&' in id_variable:
            variables = id_variable.split(' & ')
            operation = operator.and_
        else:
            variables = [id_variable]
            operation = None

        # Função para obter o valor de uma variável
        def get_value(var: str) -> str:
            row = self.df.loc[self.df['NAME'] == var]
            if not row.empty and column in row.columns:
                return row.iloc[0][column]
            return None

        # Obtém os valores das variáveis
        values = [get_value(var) for var in variables]

        # Verifica se houve algum erro na obtenção dos valores
        if any(x in values for x in ["ERROR", None]):
            return None

        # Aplica a operação bitwise, se houver mais de uma variável
        if operation:
            result = reduce(operation, values)
            return str(result)
        else:
            return str(values[0])
        
    def set_variable(self, id_variable: str, column: str, value: str):
        if id_variable in self.df['NAME'].values:
            self.df.loc[self.df['NAME'] == id_variable, column] = value
        else:
            new_row = pd.DataFrame({'NAME': [id_variable], column: [value]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.saveAllData()    
        

# Exemplo de uso
if __name__ == '__main__':
    storage = Storage('dados.xlsx')
    storage.data_updated.connect(lambda: print("Dados foram atualizados!"))
    
    storage.set_variable('PROCESS_VARIABLE', 'TIT100', '42480000')
    valor = storage.get_variable('PROCESS_VARIABLE', 'TIT100')
    print(f"Valor obtido para 'PROCESS_VARIABLE' em TIT100: {valor}")
