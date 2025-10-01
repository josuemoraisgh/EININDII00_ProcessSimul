from inter.qobjectabcmeta import QObjectABCMeta
from react.qt_compat import QObject, Signal, Slot
from abc import ABC, abstractmethod

class DBReactiveVariable(QObject, ABC, metaclass=QObjectABCMeta):
    valueChanged = Signal()  # Sinal emitido quando o valor muda
    expressionToken = Signal(list, bool)      

    @property
    @abstractmethod
    def rowName(self):
        """ Retorna o nome da linha. """
        pass

    @property
    @abstractmethod
    def colName(self):
        """ Retorna o nome da coluna. """
        pass

    @abstractmethod
    def type(self):
        """ Retorna o tipo da variável. """
        pass

    @abstractmethod
    def value(self, state):
        """ Obtém o valor da variável baseado no estado. """
        pass

    @abstractmethod
    def setValue(self, value, state):
        """ Define um novo valor para a variável. """
        pass

    @abstractmethod
    def bind_to(self, signalOtherVar: Signal, isConnect: bool):
        """ Conecta ou desconecta a variável de outro sinal. """
        pass

    @Slot()
    @abstractmethod
    def _update_from_other(self):
        """ Atualiza o valor com base em outra variável. """
        pass

    @abstractmethod
    def model(self, value: str = "") -> str:
        """ Retorna o modelo da variável. """
        pass

    @abstractmethod
    def getDataModel(self, rowName: str, colName: str) -> str:
        """ Obtém um modelo de dados com base nos nomes da linha e da coluna. """
        pass

    @abstractmethod
    def getVariable(self, rowName: str, colName: str, state):
        """ Retorna uma variável com base nos nomes da linha e coluna e no estado. """
        pass

    @abstractmethod
    def evaluate_expression(self, func: str):
        """ Avalia uma expressão matemática ou lógica baseada na variável. """
        pass