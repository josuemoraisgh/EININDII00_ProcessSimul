from PySide6.QtCore import QObject, Signal, QRunnable, Slot
from asteval import Interpreter
import re, math, random, numpy as np

class ExpressionWorkerSignals(QObject):
    finished = Signal(str, float)  # key_str, resultado

class ExpressionWorker(QRunnable):
    def __init__(self, func: str, key: tuple, symtable: dict):
        super().__init__()
        self.func = func
        self.key = key
        self.symtable = symtable
        self.signals = ExpressionWorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self):
        # print(f"[Worker] Iniciando execucao de: {self.func} com key: {self.key}")
        evaluator = Interpreter()
        evaluator.symtable.update({
            "math": math,
            "np": np,
            "random": random,
            **self.symtable
        })
        try:
            expression = re.sub(
                r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)',
                r'\1_\2_\3',
                self.func
            )
            result = evaluator(expression)
            # print(f"[Worker] Resultado avaliado: {result}")
            if isinstance(result, (int, float)):
                # print(f"[Worker] Emitido: ({self.key}, {result}) -> Slot deve receber em breve")
                self.signals.finished.emit(str(self.key), float(result))
            else:
                # print(f"[Worker] Resultado invalido para {self.key}, emitindo 0.0")
                self.signals.finished.emit(str(self.key), 0.0)
        except Exception as e:
            # print(f"[Worker] Erro ao avaliar '{self.func}' para {self.key}: {e}")
            self.signals.finished.emit(str(self.key), 0.0)

        # print(f"[Worker] Finalizado para key: {self.key}")

