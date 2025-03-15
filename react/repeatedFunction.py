from PySide6.QtCore import QTimer, QObject

class RepeatedFunction(QObject):
    def __init__(self, function, interval_ms):
        super().__init__()
        self._function = function
        self._interval_ms = interval_ms
        self._timer = QTimer(self)
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._function)
        self._is_running = False

    def changeFunction(self, interval_ms):
        """Muda a função informada."""
        self.stop()
        self._interval_ms = interval_ms
        self._timer.setInterval(self._interval_ms)

    def changeInterval(self, function):
        """Muda a função informada."""
        self.stop()
        self._timer.timeout.disconnect(self._function)
        self._function = function
        self._timer.timeout.connect(self._function)

    def start(self):
        """Inicia a execução repetida da função."""
        if not self._is_running:
            self._timer.start()
            self._is_running = True

    def stop(self):
        """Para a execução da função e reseta o timer."""
        self._timer.stop()
        self._is_running = False


