from PySide6.QtCore import QObject, Signal, Slot
from react.react_var import ReactVar
from db.db_storage import DBStorage
import pandas as pd
import os
import sys

class ReactDB(QObject):
    df                      = {}
    autoCompleteList        = {}
    isTFuncSignal           = Signal(ReactVar,bool)
    
    def __init__(self, tableNames: str):
        super().__init__()
        self.tableNames = tableNames 
        self.storage = DBStorage('db/banco.db')
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
                data.isTFuncSignal.connect(self._tFDataSlot)                  

    def _creatAutoCompleteList(self, tableName:str):
        lista = {chave: {} for chave in self.df[tableName].index}
        self.autoCompleteList[tableName] = {chave: lista for chave in self.df[tableName].columns}                 
         
    @Slot()            
    def _tFDataSlot(self, data:ReactVar,  isConnect: bool):      
        self.isTFuncSignal.emit(data,isConnect) 
       
    