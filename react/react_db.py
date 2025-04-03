from PySide6.QtCore import QObject, Signal, Slot
from react.react_var import ReactVar
from db.db_storage import DBStorage
from functools import partial
import pandas as pd
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):  # Se for executável compilado com PyInstaller
        # base_path = sys._MEIPASS  # PyInstaller move arquivos para esta pasta temporária
        return os.path.join(os.path.abspath("."), "banco.db")
    else:
        return os.path.join(os.path.abspath("."), "db", "banco.db") # Caminho normal em execução direta
       
class ReactDB(QObject):
    df                      = {}
    autoCompleteList        = {}
    isTFuncSignal           = Signal(ReactVar,bool)
    
    def __init__(self, tableNames: str):
        super().__init__()
        self.tableNames = tableNames 
        self.storage = DBStorage(get_db_path())
        for tableName in self.tableNames:       
            self._createDataFrame(tableName)          
            self._creatAutoCompleteList(tableName)      
            
    def _createDataFrame(self, tableName:str):
        # Criando o DataFrame com valores None        
        self.df[tableName] = pd.DataFrame(index=self.storage.rowKeys(tableName), columns=self.storage.colKeys(tableName), dtype=object) 
        for row in self.df[tableName].index.to_list():
            for col in self.df[tableName].columns.to_list():
                data = ReactVar(tableName, row, col, self)
                self.df[tableName].loc[row, col] = data   
                data.funcTokenSignal.connect(partial(self._trataTokensSlot, data))
                data.isTFuncSignal.connect(self._tFDataSlot)                  

    def _creatAutoCompleteList(self, tableName:str):
        lista = {chave: {} for chave in self.df[tableName].index}
        self.autoCompleteList[tableName] = {chave: lista for chave in self.df[tableName].columns}      
                
    @Slot()        
    def _trataTokensSlot(self, data: ReactVar, tokens: list[str], isConnect: bool):
        for token in tokens:
            tableName, col, row = token.split(".")
            otherData: ReactVar = self.df[tableName].loc[row, col]
            data.bindToSlot(otherData,isConnect)          
         
    @Slot()            
    def _tFDataSlot(self, data:ReactVar,  isConnect: bool):      
        self.isTFuncSignal.emit(data,isConnect) 
       
    