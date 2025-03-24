from mb.mb_reactvar import MBReactiveVariable
from hrt.hrt_reactvar import HrtReactiveVariable
from mb.mb_storage import MBStorage
from hrt.hrt_storage import HrtStorage
from PySide6.QtCore import QObject
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
        
class ReactDataBase(QObject):
    def __init__(self):
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        self.mb_storage = MBStorage(get_db_path(), 'hrt_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite
        self.hrt_storage = HrtStorage(get_db_path(), 'hrt_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite        
        self.setAutoCompleteList()        
        self._createDataFrame()

    def setAutoCompleteList(self):
        self.autoCompleteList = {
            "HART" : self.hrt_storage.autoCompleteList,
            "MODBUS": self.mb_storage.autoCompleteList,
            "SETUP": {}
        }

    def connectUpdateState(self, updateFunc):
        self.hrt_storage.updateState.connect(updateFunc)
        self.mb_storage.updateState.connect(updateFunc)        

    def disconnectUpdateState(self, updateFunc):
        self.hrt_storage.updateState.disconnect(updateFunc)        
        self.mb_storage.updateState.disconnect(updateFunc)

    def _createDataFrame(self):
        # Criando o DataFrame com valores None
        self.dfmb = pd.DataFrame(index=self.mb_storage.df.index, columns=self.mb_storage.df.columns, dtype=object) 
        for row in self.dfmb.index.to_list():
            for col in self.dfmb.columns.to_list():
                data = MBReactiveVariable(row, col, self.mb_storage)
                data.expressionToken.connect(partial(self._trataMBTokens,data))
                self.dfmb.loc[row, col] = data
        self.dfhrt = pd.DataFrame(index=self.hrt_storage.df.index, columns=self.hrt_storage.df.columns, dtype=object) 
        for row in self.dfhrt.index.to_list():
            for col in self.dfhrt.columns.to_list():
                data = HrtReactiveVariable(row, col, self.hrt_storage)
                data.expressionToken.connect(partial(self._trataHrtTokens,data))
                self.dfhrt.loc[row, col] = data               
    
    def _trataMBTokens(self, data: MBReactiveVariable, tokens: list[str], isConnect: bool):
        for token in tokens:
            col, row = token.split(".")
            otherData: MBReactiveVariable = self.dfmb.loc[row, col]
            data.bind_to(otherData.valueChanged,isConnect)
            
    def _trataHrtTokens(self, data: HrtReactiveVariable, tokens: list[str], isConnect: bool):
        for token in tokens:
            col, row = token.split(".")
            otherData: HrtReactiveVariable = self.dfhrt.loc[row, col]
            data.bind_to(otherData.valueChanged,isConnect)            
        

       
    