from hrt.hrt_reactvar import HrtReactiveVariable
from inter.ireactdf import DBReactDataFrame
from PySide6.QtCore import QObject, Signal, Slot
from hrt.hrt_storage import Storage
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
        
class HrtReactDataFrame(DBReactDataFrame, QObject):
    def __init__(self):
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        self._hrt_storage = Storage(get_db_path(), 'hrt_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite
        self._createDataFrame()

    def connectUpdateState(self, updateFunc):
        self._hrt_storage.updateState.connect(updateFunc)

    def disconnectUpdateState(self, updateFunc):
        self._hrt_storage.updateState.disconnect(updateFunc)

    def _createDataFrame(self):
        # Criando o DataFrame com valores None
        self.df = pd.DataFrame(index=self._hrt_storage.df.index, columns=self._hrt_storage.df.columns, dtype=object) 
        for row in self.df.index.to_list():
            for col in self.df.columns.to_list():
                data = HrtReactiveVariable(row, col, self._hrt_storage)
                data.expressionToken.connect(partial(self._trataTokens,data))
                self.df.loc[row, col] = data
    
    def _trataTokens(self, data: HrtReactiveVariable, tokens: list[str], isConnect: bool):
        for token in tokens:
            col, row = token.split(".")
            otherData: HrtReactiveVariable = self.df.loc[row, col]
            data.bind_to(otherData.valueChanged,isConnect)
        

       
    