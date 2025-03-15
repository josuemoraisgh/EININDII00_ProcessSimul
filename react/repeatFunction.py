from PySide6.QtCore import QThread

class RepeatFunction(QThread):
    def __init__(self, function, interval_ms):
        super().__init__()
        self._function = function
        self._interval_ms = interval_ms
        self._is_running = False

    def run(self):
        """Executa a função repetidamente a cada intervalo."""
        while self._is_running:
            self._function()  # Chama a função repetida
            self.msleep(self._interval_ms)  # Aguarda pelo intervalo configurado

    def start(self):
        """Inicia a execução repetida da função em outra thread."""
        if not self._is_running:
            self._is_running = True
            super().start()

    def stop(self):
        """Para a execução da função e reseta o estado."""
        self._is_running = False
        self.wait()  # Espera a thread terminar antes de continuar

    def changeFunction(self, function):
        """Muda a função informada."""
        self.stop()
        self._function = function

    def changeInterval(self, interval_ms):
        """Muda a função informada."""
        self.stop()
        self._interval_ms = interval_ms


