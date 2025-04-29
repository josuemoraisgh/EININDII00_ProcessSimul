from react.repeatFunction import RepeatFunction
from PySide6.QtCore import QObject, Slot
from react.react_var import ReactVar
import control as ctrl
import numpy as np
import json
import ast

class SimulTf(QObject):
    def __init__(self, stepTime):
        super().__init__()
        self.stepTime = stepTime  # em milisegundos
        self.dictDB = {}
        self.systems = {}
        self.states = {}
        self.delay = {}
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)

    @Slot(object, bool)
    def tfConnect(self, data: ReactVar, isConnect: bool):
        key = (data.tableName, data.rowName, data.colName)
        if isConnect:
            self.dictDB[key] = data
            # Extrai parâmetros de tFunc, suportando separador espaço ou vírgula
            tfunc = data.getTFunc() or ''
            parts = tfunc.strip(',').split(',', maxsplit=3)
            if len(parts) < 3:
                return
            num_str, den_str, delay_str = parts[0], parts[1], parts[2]
            # Normaliza separadores e formata listas
            num_content = num_str.strip('[]').replace(' ', ',')
            den_content = den_str.strip('[]').replace(' ', ',')
            try:
                num = ast.literal_eval(f'[{num_content}]')
                den = ast.literal_eval(f'[{den_content}]')
                delay = float(delay_str)
            except Exception as e:
                print(f"Erro ao parsear tFunc '{tfunc}': {e}")
                return
            self.delay[key] = delay
            # Monta a função de transferência com ou sem atraso
            if delay != 0.0:
                G = ctrl.TransferFunction(num, den)
                num_d, den_d = ctrl.pade(delay, 1)
                sys_tf = G * ctrl.TransferFunction(num_d, den_d)
            else:
                sys_tf = ctrl.TransferFunction(num, den)
            # Converte para espaço de estados e discretiza
            sys_ss = ctrl.tf2ss(sys_tf)
            sysd = ctrl.c2d(sys_ss, self.stepTime / 1000.0, method='tustin')
            A, B, C, D = map(lambda x: np.array(x), (sysd.A, sysd.B, sysd.C, sysd.D))
            self.systems[key] = {'A': A, 'B': B, 'C': C, 'D': D}
            self.states[key] = np.zeros((A.shape[0], 1))
        else:
            self.dictDB.pop(key, None)
            self.delay.pop(key, None)
            self.systems.pop(key, None)
            self.states.pop(key, None)

    def start(self, state: bool):
        if state:
            self.load_states()
            self._repeated_function.start()
        else:
            self._repeated_function.stop()
            self.save_states()

    def reset(self):
        self._repeated_function.stop()
        for key in list(self.states.keys()):
            self.states[key] = np.zeros_like(self.states[key])

    def _simulation_step(self):
        for key, sys in self.systems.items():
            var = self.dictDB.get(key)
            if var is None:
                continue
            u = var.inputValue if var.inputValue is not None else 0.0
            # Calcula saída e atualiza estado
            y = sys['C'].dot(self.states[key]) + sys['D'] * u
            self.states[key] = sys['A'].dot(self.states[key]) + sys['B'] * u
            new_val = float(np.clip(y, 0.0001, 1.0))
            var._value = new_val
            var.valueChangedSignal.emit(var)

    def save_states(self):
        for key, state in self.states.items():
            var = self.dictDB.get(key)
            if not var:
                continue
            row = "|".join(key[:-1])
            col = key[-1]
            try:
                s = json.dumps(state.tolist())
                var.reactFactory.storage.setRawData("TFSTATES", row, col, s)
            except Exception as e:
                print(f"Erro ao salvar estado {key}: {e}")

    def load_states(self):
        for key, var in list(self.dictDB.items()):
            row = "|".join(key[:-1])
            col = key[-1]
            try:
                raw = var.reactFactory.storage.getRawData("TFSTATES", row, col)
                if raw:
                    self.states[key] = np.array(json.loads(raw))
            except Exception as e:
                print(f"Erro ao carregar estado {key}: {e}")

    def clean_orphan_states(self):
        for key in list(self.states.keys()):
            if key not in self.systems:
                var = self.dictDB.get(key)
                if not var:
                    continue
                row = "|".join(key[:-1])
                col = key[-1]
                try:
                    var.reactFactory.storage.setData("TFSTATES", row, col, None)
                except Exception as e:
                    print(f"Erro ao limpar órfão {key}: {e}")