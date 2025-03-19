class Referencia:
    def __init__(self, valor):
        self._valor = valor

    @property
    def value(self):
        return self._valor

    @value.setter
    def value(self, novo_valor):
        self._valor = novo_valor

