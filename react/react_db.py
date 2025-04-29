# react/react_db.py
from PySide6.QtCore import QObject, Signal
from react.react_factory import ReactFactory

class ReactDB(QObject):
    df               = {}
    autoCompleteList = {}
    isTFuncSignal    = Signal(object, bool)

    def __init__(self, tableNames: list[str]):
        super().__init__()
        self._factory = ReactFactory(tableNames)
        self.storage  = self._factory.storage
        self.df       = self._factory.df
        self._factory.isTFuncSignal.connect(self.isTFuncSignal)

        # reconstrói autoCompleteList como antes, se precisar
        for tbl, df in self.df.items():
            self.autoCompleteList[tbl] = {
                col: {row: {} for row in df.index}
                for col in df.columns
            }
