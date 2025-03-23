from abc import ABC, abstractmethod

class IReactDataFrame(ABC):
    @abstractmethod
    def connectUpdateState(self, updateFunc):
        """ Conecta a função ao sinal de atualização do estado. """
        pass

    @abstractmethod
    def disconnectUpdateState(self, updateFunc):
        """ Desconecta a função do sinal de atualização do estado. """
        pass

    @abstractmethod
    def _createDataFrame(self):
        """ Cria um DataFrame interno com objetos reativos. """
        pass

    @abstractmethod
    def _trataTokens(self, data, tokens: list[str], isConnect: bool):
        """ Trata os tokens de expressões e gerencia conexões entre variáveis. """
        pass