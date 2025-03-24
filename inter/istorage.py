from inter.qobjectabcmeta import QObjectABCMeta
from abc import ABC, abstractmethod
from typing import List
from PySide6.QtCore import QObject
from abc import ABC, abstractmethod

class DBStorage(QObject, ABC, metaclass=QObjectABCMeta):
    @abstractmethod
    def rowKeys(self) -> List[str]:
        """Retorna as chaves (nomes) das linhas."""
        pass

    @abstractmethod
    def colKeys(self) -> List[str]:
        """Retorna os nomes das colunas."""
        pass

    @abstractmethod
    def getStrData(self, id_variable: str, column: str) -> str:
        """Retorna o valor de uma célula como string."""
        pass

    @abstractmethod
    def setStrData(self, id_variable: str, column: str, value: str):
        """Define o valor de uma célula."""
        pass

    @abstractmethod
    def saveAllData(self):
        """Salva todos os dados no banco."""
        pass
