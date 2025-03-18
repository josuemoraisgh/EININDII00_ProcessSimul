import pandas as pd
import sqlite3
from functools import reduce
import operator
from PySide6.QtCore import Signal, QObject
from hrt.hrt_banco import hrt_banco
import os

class Storage(QObject):
    data_updated = Signal()  # Sinal emitido ao atualizar dados

    def __init__(self, db_name: str, table_name: str):
        super().__init__()
        self.db_name = db_name
        self.table_name = table_name
        # Verificar se o banco existe
        if os.path.exists(self.db_name):
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Verificar se a tabela existe (aspas corrigidas)
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
                if cursor.fetchone():
                    # Ler os dados da tabela para um DataFrame, usando a coluna 'NAME' como índice
                    self.df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn, index_col='NAME')
                else:
                    self.creatBanco()
                    print(f'Tabela {self.table_name} não encontrada. Operação alternativa realizada.')                    
        else:           
            self.creatBanco()
            print('Banco de dados não encontrado. Operação alternativa realizada.')             
    
    def creatBanco(self):
        # Colunas adicionais
        extra_columns = ['LI100', 'FI100V', 'FI100A', 'FV100A', 'PI100', 'TI100']
        # Converter o dicionário em DataFrame com colunas repetidas
        rows = []
        for key, val in hrt_banco.items():
            row = [key, val[0], val[1]] + [val[2]] * len(extra_columns)
            rows.append(row)
        columns = ['NAME', 'BYTE_SIZE', 'TYPE'] + extra_columns
        self.df = pd.DataFrame(rows, columns=columns)
        self.saveAllData()
        print('Dados salvos com sucesso na tabela hrt_settings.')   

    def saveAllData(self):
        with sqlite3.connect(self.db_name) as conn:
            self.df.to_sql(self.table_name, conn, if_exists='replace', index=True)
        self.data_updated.emit()  # Emite sinal após salvar
    
    def rowKeys(self):
        return self.df.index

    def colKeys(self):
        return self.df.columns
    
    def getStrData(self, id_variable: str, column: str) -> str:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if '|' in id_variable:
                variables = id_variable.split(' | ')
                operation = operator.or_
            elif '&' in id_variable:
                variables = id_variable.split(' & ')
                operation = operator.and_
            else:
                variables = [id_variable]
                operation = None
            values = []
            for var in variables:
                cursor.execute(f"SELECT {column} FROM {self.table_name} WHERE NAME = ?", (var,))
                result = cursor.fetchone()
                values.append(result[0] if result else None)
        if any(x in values for x in [None, "ERROR"]):
            return None
        if operation:
            return str(reduce(operation, map(int, values)))
        return str(values[0])

    def setStrData(self, id_variable: str, column: str, value: str):
        try:
            # Conectar ao banco de dados SQLite
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Verificar se o registro já existe
                cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE NAME = ?", (id_variable,))
                if cursor.fetchone():
                    # Atualizar o valor da coluna para o id_variable
                    cursor.execute(f"UPDATE {self.table_name} SET {column} = ? WHERE NAME = ?", (value, id_variable))
                else:
                    # Inserir um novo registro com o id_variable e o valor na coluna
                    cursor.execute(f"INSERT INTO {self.table_name} (NAME, {column}) VALUES (?, ?)", (id_variable, value))
            # Emitir o sinal de dados atualizados após a alteração
            self.data_updated.emit()
        except Exception as e:
            print(f"❌ Erro ao atualizar ou inserir no SQLite: {e}")

# Exemplo de uso
if __name__ == '__main__':
    storage = Storage('banco.db', 'minha_tabela')
    storage.data_updated.connect(lambda: print("Dados foram atualizados!"))
    storage.set_variable('PROCESS_VARIABLE', 'TIT100', '42480000')
    valor = storage.get_variable('PROCESS_VARIABLE', 'TIT100')
    print(f"Valor obtido para 'PROCESS_VARIABLE' em TIT100: {valor}")