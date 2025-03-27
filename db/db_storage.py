from functools import reduce
from db.db_state import DBState
from PySide6.QtCore import Signal
import pandas as pd
import operator
import sqlite3

class DBStorage:
    data_updated = Signal()  # Sinal emitido ao atualizar dados
        
    def __init__(self, db_name: str, table_name: str):
        super().__init__()
        # self._state = DBState.humanValue
        self.db_name = db_name
        self.table_name = table_name

    def rowKeys(self) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT NAME FROM {self.table_name};')
            return [linha[0] for linha in cursor.fetchall()]

    def colKeys(self) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Executa PRAGMA para obter informações da estrutura da tabela
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            colunas = cursor.fetchall()    
            return [coluna[1] for coluna in colunas[1:]]

    def getData(self, rowName: str, colName: str) -> str:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if '|' in rowName:
                variables = rowName.split(' | ')
                operation = operator.or_
            elif '&' in rowName:
                variables = rowName.split(' & ')
                operation = operator.and_
            else:
                variables = [rowName]
                operation = None
            values = []
            for var in variables:
                cursor.execute(f"SELECT {colName} FROM {self.table_name} WHERE NAME = ?", (var,))
                result = cursor.fetchone()
                values.append(result[0] if result else None)
        if any(x in values for x in [None, "ERROR"]):
            return None
        if operation:
            return str(reduce(operation, map(int, values)))
        return str(values[0])

    def setData(self, rowName: str, colName: str, value: str):
        try:
            # Conectar ao banco de dados SQLite
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Verificar se o registro já existe
                cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE NAME = ?", (rowName,))
                if cursor.fetchone():
                    # Atualizar o valor da coluna para o rowName
                    cursor.execute(f"UPDATE {self.table_name} SET {colName} = ? WHERE NAME = ?", (value, rowName))
                else:
                    # Inserir um novo registro com o rowName e o valor na coluna
                    cursor.execute(f"INSERT INTO {self.table_name} (NAME, {colName}) VALUES (?, ?)", (rowName, value))
            # Emitir o sinal de dados atualizados após a alteração
            self.data_updated.emit()
        except Exception as e:
            print(f"❌ Erro ao atualizar ou inserir no SQLite: {e}")
            
    def dataFrame(self):
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn, index_col='NAME')
        return df
                                
# Exemplo de uso
if __name__ == '__main__':
    storage = DBStorage('banco.db', 'HART_tabela')
    print(storage.colKeys())
    print(storage.rowKeys())