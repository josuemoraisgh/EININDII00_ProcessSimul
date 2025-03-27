from hrt_banco import hrt_banco
import pandas as pd
import sqlite3

def crateDB(db_name: str,table_name: str):
    # Colunas adicionais
    extra_columns = ['LI100', 'FI100V', 'FI100A', 'FV100A', 'PI100V', 'TI100']
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
    
# Exemplo de uso
if __name__ == '__main__':
    crateDB('db/banco.db','HART_tabela')
    crateDB('db/banco.db','MODBUS_tabela')    