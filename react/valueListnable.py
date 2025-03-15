from PySide6.QtCore import QObject, Signal

class ReactiveVariable(QObject):
    valueChanged = Signal(object)  # Sinal emitido quando o valor muda

    def __init__(self, initial_value=None):
        super().__init__()
        self._value = initial_value

    def set(self, new_value):
        if self._value != new_value:
            self._value = new_value
            self.valueChanged.emit(new_value)

    def get(self):
        return self._value
    
    def connect(self, update_function):
        self.valueChanged.connect(update_function)
