from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_reactvar import HrtReactiveVariable
from PySide6.QtCore import QObject, Signal, Slot
from functools import partial
import pandas as pd
class HrtReactDataFrame():
    def __init__(self):
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        self._hrt_storage = Storage('banco.db', 'hrt_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite
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
    
    def _trataTokens(self, data: HrtReactiveVariable, tokens: list[str]):
        for token in tokens:
            col, row = token.split(".")
            otherData: HrtReactiveVariable = self.df.loc[row, col]
            data.bind_to(otherData.valueChanged) 
        

       
    