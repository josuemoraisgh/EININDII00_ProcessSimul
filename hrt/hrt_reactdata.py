from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from asteval import Interpreter
from typing import Union
import numpy as np
import pandas as pd
import re
class HrtData(Storage):
    def __init__(self):
        super().__init__('banco.db', 'hrt_tabela')  # 🔥 Chama o construtor da classe Pai quando sqlite
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        mask = np.char.startswith(self.df.values.astype(str), "$")
        # Obtendo os índices das células que satisfazem a condição
        rows, cols = np.where(mask)
        # Mapeando para os nomes reais de linhas e colunas
        self.rowTfNames = self.df.index[rows].tolist()
        self.colTfNames = self.df.columns[cols].tolist()
        # Inicializando o dicionario com os resultados das tf
        self.tf_dict = {(row, col): 0.0 for row in self.rowTfNames for col in self.colTfNames}
    
    def getShape(self):
        return self.df.shape
       
    