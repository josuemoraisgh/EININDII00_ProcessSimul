import sqlite3

def ler_coluna_name(db_path: str, tabela: str) -> list:
    """
    Retorna todos os valores da coluna 'NAME' de uma tabela no banco SQLite.

    Args:
        db_path (str): Caminho para o banco de dados.
        tabela (str): Nome da tabela.

    Returns:
        list: Lista com os valores da coluna NAME.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT NAME FROM {tabela};')
        return [linha[0] for linha in cursor.fetchall()]

def obter_nomes_colunas(db_path: str, tabela: str) -> list:
    """
    Retorna os nomes das colunas de uma tabela SQLite.

    Args:
        db_path (str): Caminho para o banco de dados.
        tabela (str): Nome da tabela.

    Returns:
        list: Lista com os nomes das colunas.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Executa PRAGMA para obter informações da estrutura da tabela
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = cursor.fetchall()    
        return [coluna[1] for coluna in colunas]

indices = ler_coluna_name('db/banco.db', 'HART_tabela')
column = obter_nomes_colunas('db/banco.db', 'HART_tabela')
print(column)