from react.react_var import ReactVar
from react.referencia import RefVar
from db.db_storage import DBStorage
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
        
class ReactDB(QObject):
    df = {}
    tf_ref = RefVar({})
    autoCompleteList = {}
    rowTfNames = {} 
    colTfNames = {}
    
    def __init__(self, tableNames: str):
        self.tableNames = tableNames 
        self.storage = DBStorage(get_db_path()) # 🔥 Chama o construtor da classe Pai quando sqlite         
        for tableName in self.tableNames:       
            self._createDataFrame(tableName)          
            self._creatAutoCompleteList(tableName)
            self._createTfDict(tableName)      

    def _createTfDict(self, tableName:str):        
        mask = np.char.startswith(self.storage.dataFrame(tableName).values.astype(str), "$")
        # Obtendo os índices das células que satisfazem a condição
        rows, cols = np.where(mask)
        # Mapeando para os nomes reais de linhas e colunas
        self.rowTfNames[tableName] = [self.storage.rowKeys(tableName)[i] for i in rows]  
        self.colTfNames[tableName] = [self.storage.colKeys(tableName)[i] for i in cols]
        # Inicializando o dicionario com os resultados das tf
        self.tf_ref.value[tableName] = {(row, col): 0.01 for row in self.rowTfNames[tableName] for col in self.colTfNames[tableName]}

    def _createDataFrame(self, tableName:str):
        # Criando o DataFrame com valores None        
        self.df[tableName] = pd.DataFrame(index=self.storage.rowKeys(tableName), columns=self.storage.colKeys(tableName), dtype=object) 
        for row in self.df[tableName].index.to_list():
            for col in self.df[tableName].columns.to_list():
                data = ReactVar(tableName, row, col, self.storage, self.tf_ref)
                data.expressionToken.connect(partial(self._trataTokens, data))
                self.df[tableName].loc[row, col] = data               
    
    def _trataTokens(self, data: ReactVar, tokens: list[str], isConnect: bool):
        for token in tokens:
            tableName, col, row = token.split(".")
            otherData: ReactVar = self.df[tableName].loc[row, col]
            data.bind_to(otherData.valueChanged,isConnect)  

    def _creatAutoCompleteList(self, tableName:str):
        lista = {chave: {} for chave in self.df[tableName].index}
        self.autoCompleteList[tableName] = {chave: lista for chave in self.df[tableName].columns}

    def connectUpdateState(self, updateFunc):
        self.storage.updateState.connect(updateFunc)    

    def disconnectUpdateState(self, updateFunc):      
        self.storage.updateState.disconnect(updateFunc)                 
        

       
    