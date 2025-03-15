import pandas as pd
import sqlite3

def excel_to_sqlite(excel_file, db_name, table_name):
    # Ler o arquivo Excel
    df = pd.read_excel(excel_file)
    
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Criar a tabela dinamicamente com base nas colunas do DataFrame
    columns = ", ".join([f"{col} TEXT" for col in df.columns])  # Define colunas como TEXT por padrão
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns}
    )
    """
    cursor.execute(create_table_query)
    
    # Salvar os dados no banco
    df.to_sql(table_name, conn, if_exists='append', index=False)
    
    # Fechar conexão
    conn.commit()
    conn.close()
    print(f"Dados salvos na tabela '{table_name}' do banco '{db_name}'.")

# Exemplo de uso
excel_to_sqlite('db/dados.xlsx', 'db/banco.db', 'hrt_tabela')