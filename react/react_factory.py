from PySide6.QtCore import QObject, Signal, Slot
from db.db_storage import DBStorage
import pandas as pd
from react.react_var import ReactVar

class ReactFactory(QObject):
    """
    Gerencia instâncias de ReactVar e mantém os DataFrames em 'df'.
    """
    isTFuncSignal = Signal(object, bool)

    def __init__(self, tableNames: list[str]):
        super().__init__()
        self.tableNames = tableNames
        self.storage    = DBStorage('db/banco.db')
        self.df         = {}
        self._build_all()

    def _build_all(self):
        for tbl in self.tableNames:
            self._build_table(tbl)

    def _build_table(self, tableName: str):
        df = pd.DataFrame(
            index=self.storage.rowKeys(tableName),
            columns=self.storage.colKeys(tableName),
            dtype=object
        )
        for row in df.index:
            for col in df.columns:
                var = ReactVar(tableName, row, col, reactDB=self)
                df.at[row, col] = var
                var.isTFuncSignal.connect(self._on_tfunc)
                # inicializa imediatamente, evitando None
                try:
                    var.getValue()
                except Exception:
                    pass
        self.df[tableName] = df

    @Slot(object, bool)
    def _on_tfunc(self, var, isConnect: bool):
        self.isTFuncSignal.emit(var, isConnect)