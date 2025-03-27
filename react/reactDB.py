from inter.ireactvar import DBReactiveVariable
from mb.mb_reactvar import MBReactiveVariable
from hrt.hrt_reactvar import HrtReactiveVariable
from mb.mb_storage import MBStorage
from hrt.hrt_storage import HrtStorage
from PySide6.QtCore import QObject
from functools import partial
import pandas as pd
import numpy as np
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):  # Se for executável compilado com PyInstaller
        # base_path = sys._MEIPASS  # PyInstaller move arquivos para esta pasta temporária
        return os.path.join(os.path.abspath("."), "banco.db")
    else:
        return os.path.join(os.path.abspath("."), "db", "banco.db") # Caminho normal em execução direta
        
class ReactDataBase(QObject):
    storage = {}
    df = {}
    tf_dict = {}
    autoCompleteList = {}
    
    def __init__(self, sources: str):
        self.sources = sources  
        for source in self.sources:       
            self._creatStorage(source)
            self._createDataFrame(source)          
            self._creatAutoCompleteList(source)
            self._createTfDict(source)      

    def _creatStorage(self, source:str):
        if source.find("HART") != -1:   
            self.storage[source] = HrtStorage(get_db_path(), f'{source}_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite
        elif source.find("MODBUS") != -1:   
            self.storage[source] = MBStorage(get_db_path(), f'{source}_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite        
        # else:
        #     self.storage[source] = CFStorage(get_db_path(), f'{source}_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite 

    def _createTfDict(self, source:str):        
        mask = np.char.startswith(self.df[source].values.astype(str), "$")
        # Obtendo os índices das células que satisfazem a condição
        rows, cols = np.where(mask)
        # Mapeando para os nomes reais de linhas e colunas
        self.rowTfNames = self.df[source].index[rows].tolist()
        self.colTfNames = self.df[source].columns[cols].tolist()
        # Inicializando o dicionario com os resultados das tf
        self.tf_dict[source] = {(row, col): 0.01 for row in self.rowTfNames for col in self.colTfNames}

    def _createDataFrame(self, source:str):
        # Criando o DataFrame com valores None        
        self.df[source] = pd.DataFrame(index=self.storage[source].df.index, columns=self.storage[source].df.columns, dtype=object) 
        for row in self.df[source].index.to_list():
            for col in self.df[source].columns.to_list():
                if source.find("HART") != -1:   
                    data = HrtReactiveVariable(row, col, self.storage[source])
                elif source.find("MODBUS") != -1:   
                    data = MBReactiveVariable(row, col, self.storage[source])
                # else:
                #   data = DBReactiveVariable(row, col, self.storage[source])
                data.expressionToken.connect(partial(self._trataTokens, data))
                self.df[source].loc[row, col] = data               
    
    def _trataTokens(self, data: DBReactiveVariable, tokens: list[str], isConnect: bool):
        for token in tokens:
            source, col, row = token.split(".")
            otherData: DBReactiveVariable = self.df[source].loc[row, col]
            data.bind_to(otherData.valueChanged,isConnect)  

    def _creatAutoCompleteList(self, source:str):
        lista = {chave: {} for chave in self.df[source].index}
        self.autoCompleteList[source] = {chave: lista for chave in self.df[source].columns}

    def connectUpdateState(self, updateFunc):
        for source in self.sources:
            self.storage[source].updateState.connect(updateFunc)    

    def disconnectUpdateState(self, updateFunc):
        for source in self.sources:        
            self.storage[source].updateState.disconnect(updateFunc)                 
        

       
    