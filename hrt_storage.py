import pandas as pd
from functools import reduce
from PySide6.QtCore import Signal, QObject
import operator

class HrtStorage(QObject):
    data_updated = Signal()  # 🔥 Declarando o sinal corretamente
    
    def __init__(self, caminho_excel: str):
        super().__init__()  # 🔥 Inicializa QObject explicitamente        
        self.caminho_excel = caminho_excel
        try:
            self.df = pd.read_excel(self.caminho_excel)
        except FileNotFoundError:
            # Se o arquivo não existir, cria uma tabela vazia
            self.df = pd.DataFrame(columns=["Variavel", "Tipo", "Tamanho", "TIT100"])
            self.save_data()
    
    def get_dataframe(self):
        return self.df
    
    def save_data(self):
        """Escreve os dados de volta ao arquivo Excel."""
        self.df.to_excel(self.caminho_excel, index=False)
        self.data_updated.emit()  # Emite o sinal de atualização 
        
    def set_pos_datframe(self, row, col, value):
        """Atualiza o DataFrame quando a célula for alterada."""
        self.df.iloc[row, col] = value
        self.save_data()  # Salva automaticamente no Excel               
        
    def keys(self):
        return self.df['Variavel'].tolist()
    
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
            row = self.df.loc[self.df['Variavel'] == var]
            if not row.empty and column in row.columns:
                value = row.iloc[0][column]
                if not value.startswith('@'):
                    return int(value,base=16)
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
        if id_variable in self.df['Variavel'].values:
            self.df.loc[self.df['Variavel'] == id_variable, column] = value
        else:
            new_row = pd.DataFrame({'Variavel': [id_variable], column: [value]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_data()    
        

# Exemplo de uso
if __name__ == '__main__':
    storage = HrtStorage('dados.xlsx')

    # Definir variável para o instrumento LD301
    storage.set_variable('response_code', 'TI100', '4.0')

    # Obter variável do instrumento LD301
    valor = storage.get_variable('tag', 'PI100')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")
