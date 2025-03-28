from hrt_banco import hrt_banco
import pandas as pd
import sqlite3

def hrt_crateDB(db_name: str,table_name: str):
    # Colunas adicionais
    extra_columns = ['FI100CA', 'FV100CA', 'FV100AR', 'FV100AR', 'FI100V', 'PI100V', 'FI100A', 'FV100A', 'PI100A', 'LI100', 'TI100']
    # Converter o dicionário em DataFrame com colunas repetidas
    rows = []
    for key, val in hrt_banco.items():
        row = [key, val[0], val[1]] + [val[2]] * len(extra_columns)
        rows.append(row)
    columns = ['NAME', 'BYTE_SIZE', 'TYPE'] + extra_columns
    df = pd.DataFrame(rows, columns=columns)
    with sqlite3.connect(db_name) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    print('Banco de dados criado:') 

def mb_crateDB(db_name: str,table_name: str):
    rows = []    
    for key, val in hrt_banco.items():
        row = [key, val[0], val[1], val[2] + val[3]]
        rows.append(row)        
    columns = ['NAME', 'BYTE_SIZE', 'TYPE', 'ADDRESS', 'CLP100']
    df = pd.DataFrame(rows, columns=columns)
    with sqlite3.connect(db_name) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    print('Banco de dados criado:') 

# Exemplo de uso
if __name__ == '__main__':
    # hrt_crateDB('db/banco.db','HART_tabela')
    mb_crateDB('db/banco.db','MODBUS_tabela')    