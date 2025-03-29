from PySide6.QtCore import Signal, QObject
from functools import reduce
import pandas as pd
import operator
import sqlite3

class DBStorage(QObject):
    data_updated = Signal()  # Sinal emitido ao atualizar dados
        
    def __init__(self, db_name: str):
        super().__init__()
        self.db_name = db_name

    def rowKeys(self, tableName: str) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT NAME FROM {tableName}_tabela;')
            return [linha[0] for linha in cursor.fetchall()]

    def colKeys(self, tableName: str) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Executa PRAGMA para obter informações da estrutura da tabela
            cursor.execute(f"PRAGMA table_info({tableName}_tabela)")
            colunas = cursor.fetchall()    
            return [coluna[1] for coluna in colunas[1:]]

    def getData(self, tableName: str, rowName: str, colName: str) -> str:
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
                cursor.execute(f"SELECT {colName} FROM {tableName}_tabela WHERE NAME = ?", (var,))
                result = cursor.fetchone()
                values.append(result[0] if result else None)
        if any(x in values for x in [None, "ERROR"]):
            return None
        if operation:
            return str(reduce(operation, map(int, values)))
        return str(values[0])

    def setData(self, tableName: str, rowName: str, colName: str, value: str):
        try:
            # Conectar ao banco de dados SQLite
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Verificar se o registro já existe
                cursor.execute(f"SELECT 1 FROM {tableName}_tabela WHERE NAME = ?", (rowName,))
                if cursor.fetchone():
                    # Atualizar o valor da coluna para o rowName
                    cursor.execute(f"UPDATE {tableName}_tabela SET {colName} = ? WHERE NAME = ?", (value, rowName))
                else:
                    # Inserir um novo registro com o rowName e o valor na coluna
                    cursor.execute(f"INSERT INTO {tableName}_tabela (NAME, {colName}) VALUES (?, ?)", (rowName, value))
            # Emitir o sinal de dados atualizados após a alteração
            self.data_updated.emit()
        except Exception as e:
            print(f"❌ Erro ao atualizar ou inserir no SQLite: {e}")
            
    def dataFrame(self, tableName: str):
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tableName}_tabela", conn, index_col='NAME')
        return df
                                
# Exemplo de uso
if __name__ == '__main__':
    storage = DBStorage('banco.db', 'HART_tabela')
    print(storage.colKeys())
    print(storage.rowKeys())