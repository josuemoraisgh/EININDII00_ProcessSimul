from PySide6.QtCore import QTimer, QThreadPool
from react.expression_worker import ExpressionWorker
from react.react_db import ReactDB
from db.db_types import DBState
import control as ctrl
import numpy as np
import ast
import re
import time

class SimulTf:
    def __init__(self, reactDataBase: ReactDB, stepTime):
        self.reactDataBase = reactDataBase
        self.threadPool = QThreadPool()
        self.stepTime = stepTime  # em milisegundos

        self.systems = {}
        self.states = {}
        self.inputs = {}
        self.v_max = {}
        self.v_min = {}

        self._last_input_values = {}     # Cache de tokens e valores por chave
        self._last_outputs = {}          # Último output calculado por chave
        self._dependencies = {}          # Dependências: (tbl, row, col) -> [tokens]
        self._dirty_inputs = set()       # Entradas que precisam ser recalculadas

        for tableName in self.reactDataBase.tableNames:
            self.systems[tableName] = {}
            self.states[tableName] = {}
            self.inputs[tableName] = {}
            self.v_max[tableName] = {}
            self.v_min[tableName] = {}

            for rowTfName, colTfName in zip(self.reactDataBase.rowTfNames[tableName], self.reactDataBase.colTfNames[tableName]):
                num_str, den_str, input_str, v_max, v_min = self.reactDataBase.storage.getData(tableName, rowTfName, colTfName).split(",")
                num = ast.literal_eval(num_str[1:].replace(" ", ","))
                den = ast.literal_eval(den_str.replace(" ", ","))

                if re.search(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', input_str):
                    self.inputs[tableName][(rowTfName, colTfName)] = input_str
                    tokens = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', input_str)
                    self._dependencies[(tableName, rowTfName, colTfName)] = tokens
                else:
                    self.inputs[tableName][(rowTfName, colTfName)] = float(input_str)

                self.v_max[tableName][(rowTfName, colTfName)] = float(v_max)
                self.v_min[tableName][(rowTfName, colTfName)] = float(v_min)

                sys_tf = ctrl.TransferFunction(num, den)
                sys_ss = ctrl.tf2ss(sys_tf)
                sysd = ctrl.c2d(sys_ss, stepTime / 1000.0, method='tustin')

                self.systems[tableName][(rowTfName, colTfName)] = {
                    "A": np.array(sysd.A),
                    "B": np.array(sysd.B),
                    "C": np.array(sysd.C),
                    "D": np.array(sysd.D)
                }
                self.states[tableName][(rowTfName, colTfName)] = np.zeros((sysd.A.shape[0], 1))

        self.timer = QTimer()
        self.timer.timeout.connect(self._simulation_step)
        self.timer.setInterval(self.stepTime)

    def start(self, state: bool):
        if state:
            self.timer.start()
        else:
            self.timer.stop()

    def reset(self):
        self.timer.stop()
        for tableName in self.reactDataBase.tableNames:
            for key in self.states[tableName]:
                self.states[tableName][key] = np.zeros_like(self.states[tableName][key])

    def changeInputValues(self, tableName, rowTfName, colTfName, input_str):
        if not re.search(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', input_str):
            input_str = float(input_str)
        self.inputs[tableName][(rowTfName, colTfName)] = input_str

    def _simulation_step(self):
        t0 = time.time()
        print("[SimulTf] Iniciando tick...")

        for tableName in self.reactDataBase.tableNames:
            for key, system in self.systems[tableName].items():
                input_val = self.inputs[tableName][key]
                key_full = (tableName, *key)

                if isinstance(input_val, str):
                    tokens = self._dependencies.get(key_full, [])
                    symtable = {}
                    input_changed = False
                    last_token_values = self._last_input_values.get(key_full, {})

                    for token in tokens:
                        try:
                            tbl, col, row = token.split(".")
                            val = self.reactDataBase.df[tbl].loc[(row, col)].getVariable(tbl, row, col, DBState.humanValue)
                            symtable[token.replace(".", "_")] = val

                            if last_token_values.get(token) != val:
                                input_changed = True
                        except Exception as e:
                            print(f"[SimulTf] Erro ao obter {token}: {e}")

                    if not input_changed and key_full not in self._dirty_inputs:
                        continue

                    self._last_input_values[key_full] = {t: symtable[t.replace('.', '_')] for t in tokens}
                    self._dirty_inputs.discard(key_full)

                    print(f"[SimulTf] Avaliando expressao para {key_full}: {input_val}")
                    worker = ExpressionWorker(input_val, key_full, symtable)
                    worker.signals.finished.connect(self._handle_worker_result)
                    self.threadPool.start(worker)

                else:
                    print(f"[SimulTf] Executando TF direta para {tableName}, {key}: entrada = {input_val}")
                    self._compute_output(tableName, key, input_val)

        print(f"[SimulTf] Tick levou {round((time.time() - t0)*1000)} ms")

    # SimulTf.py (exemplo do slot para debug)
    def _handle_worker_result(self, key_str: str, input_val: float):
        from PySide6.QtCore import QMetaObject, Qt
        print(f"[SimulTf] Slot recebeu: {key_str}, {input_val}")
        try:
            tableName, row, col = eval(key_str)
            key = (row, col)
            self._compute_output(tableName, key, input_val)
            # Força atualização visual (caso QObjects estejam conectados)
            try:
                cell = self.reactDataBase.df[tableName].loc[key]
                QMetaObject.invokeMethod(cell, "valueChanged", Qt.QueuedConnection)
            except Exception as emit_err:
                print(f"[SimulTf] Falha ao emitir valueChanged para {key}: {emit_err}")
        except Exception as e:
            print(f"[SimulTf] Erro ao processar resultado de expressao: {e}")

    def _compute_output(self, tableName, key, input_val):
        system = self.systems[tableName][key]
        next_state = system["A"].dot(self.states[tableName][key]) + system["B"] * input_val
        output = float(system["C"].dot(next_state) + system["D"] * input_val)
        self.states[tableName][key] = next_state

        output_clamped = min(max(output, self.v_min[tableName][key]), self.v_max[tableName][key])
        self.reactDataBase.tf_ref.value[tableName][key] = output_clamped
        self.reactDataBase.df[tableName].loc[key].valueChanged.emit()

        print(f"[SimulTf] TF {tableName}, {key} -> output = {output_clamped}")

        # Marca Tfs que dependem deste como "sujas"
        current_token = f"{tableName}.{key[1]}.{key[0]}"
        for other_key, token_list in self._dependencies.items():
            if current_token in token_list:
                self._dirty_inputs.add(other_key)