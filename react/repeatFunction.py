from PySide6.QtCore import QObject, QThread, QTimer, Slot

class RepeatFunction(QObject):
    def __init__(self, function, interval_ms):
        super().__init__()
        self._function = function
        self._interval_ms = interval_ms

        self._thread = QThread()
        self._timer = QTimer()
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._function)
        self.moveToThread(self._thread)
        self._thread.started.connect(self._timer.start)

    def start(self):
        """Inicia a thread e o timer."""
        if not self._thread.isRunning():
            self._thread.start()

    def stop(self):
        """Para o timer e a thread."""
        self._timer.stop()
        self._thread.quit()
        self._thread.wait()

    def changeFunction(self, function):
        self._timer.timeout.disconnect()
        self._function = function
        self._timer.timeout.connect(self._function)

    def changeInterval(self, interval_ms):
        self._interval_ms = interval_ms
        self._timer.setInterval(self._interval_ms)