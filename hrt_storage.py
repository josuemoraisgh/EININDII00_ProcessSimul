import pandas as pd
from functools import reduce
import operator

class HrtStorage:
    def __init__(self, caminho_excel: str):
        self.caminho_excel = caminho_excel
        self.df = pd.read_excel(self.caminho_excel)

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
        self.df.to_excel(self.caminho_excel, index=False)
        

# Exemplo de uso
if __name__ == '__main__':
    storage = HrtStorage('dados.xlsx')

    # Definir variável para o instrumento LD301
    storage.set_variable('response_code', 'TI100', '4.0')

    # Obter variável do instrumento LD301
    valor = storage.get_variable('tag', 'PI100')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")
