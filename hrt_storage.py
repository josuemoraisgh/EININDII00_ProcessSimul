import re
from asteval import Interpreter
from typing import Union
import pandas as pd

class HrtStorage:
    def __init__(self, caminho_excel: str):
        self.caminho_excel = caminho_excel
        self.df = pd.read_excel(self.caminho_excel)

    def keys(self):
        return self.df['Variavel'].tolist()

    def get_variable(self, id_variable: str, column: str) -> Union[str, float]:
        row = self.df.loc[self.df['Variavel'] == id_variable]
        if not row.empty and column in row.columns:
            if row.iloc[0][column][1] == '@' :
                return self._evaluate_expression(row.iloc[0][column], column)
            else: 
                return row.iloc[0][column]
        return "ERROR"

    def set_variable(self, id_variable: str, column: str, value: str):
        if id_variable in self.df['Variavel'].values:
            self.df.loc[self.df['Variavel'] == id_variable, column] = value
        else:
            new_row = pd.DataFrame({'Variavel': [id_variable], column: [value]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_excel(self.caminho_excel, index=False)
        
    def _evaluate_expression(self, func: str, column: str) -> float:
        evaluator = Interpreter()
        expr_str = func[1:]  # Remove o caractere '@' inicial
        tokens = re.findall(r'[A-Za-z_]\w*', expr_str)
        context = {}
        for token in tokens:
            var_val = self.get_variable(token, column)
            if var_val is not None:
                evaluator.symtable[token] = float(var_val)
        try:
            result = evaluator(expr_str)
            return float(result)
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            return 0.0


# Exemplo de uso
if __name__ == '__main__':
    storage = HrtStorage('dados.xlsx')

    # Definir variável para o instrumento LD301
    storage.set_variable('response_code', 'TI100', '4.0')

    # Obter variável do instrumento LD301
    valor = storage.get_variable('tag', 'PI100')
    print(f"Valor obtido para 'input_value' em LD301: {valor}")
