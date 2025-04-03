
from react.expression_worker import ExpressionWorker
from PySide6.QtCore import QObject, Signal, Slot
from react.repeatFunction import RepeatFunction
from PySide6.QtCore import QTimer, QThreadPool
from react.react_var import ReactVar
from react.react_db import ReactDB
from db.db_types import DBState
import control as ctrl
import numpy as np
import ast
import re
import time

class SimulTf(QObject):
    
    dictDB = {}
    systems = {}
    states = {}
    v_max = {}
    v_min = {}  
      
    def __init__(self, stepTime):
        super().__init__()
        self.stepTime = stepTime  # em milisegundos
        # Inicializa a função repetida para rodar a simulação de forma contínua
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)        

    @Slot()
    def tfConnect(self, data: ReactVar,  isConnect: bool):
        if isConnect == True:
            self.dictDB[(data.tableName, data.rowName, data.colName)] = data
            num_str, den_str, _, v_max, v_min = data.getTFunc().split(",")
            num = ast.literal_eval(num_str.replace(" ", ","))
            den = ast.literal_eval(den_str.replace(" ", ","))

            self.v_max[(data.tableName, data.rowName, data.colName)] = float(v_max)
            self.v_min[(data.tableName, data.rowName, data.colName)] = float(v_min)

            sys_tf = ctrl.TransferFunction(num, den)
            sys_ss = ctrl.tf2ss(sys_tf)
            sysd = ctrl.c2d(sys_ss, self.stepTime / 1000.0, method='tustin')

            self.systems[(data.tableName, data.rowName, data.colName)] = {
                "A": np.array(sysd.A),
                "B": np.array(sysd.B),
                "C": np.array(sysd.C),
                "D": np.array(sysd.D)
            }  
            self.states[(data.tableName, data.rowName, data.colName)] = np.zeros((sysd.A.shape[0], 1))          
        else:
            self.dictDB.pop((data.tableName, data.rowName, data.colName), None)
            self.v_max.pop((data.tableName, data.rowName, data.colName), None)
            self.v_min.pop((data.tableName, data.rowName, data.colName), None)
            self.systems.pop((data.tableName, data.rowName, data.colName), None)
            self.states.pop((data.tableName, data.rowName, data.colName), None)
            
    def start(self, state: bool):
        """Inicia a execução da simulação."""
        if state:
            self._repeated_function.start()
        else:
            self._repeated_function.stop()

    def reset(self):
        """Finaliza a execução e reseta os estados."""      
        self._repeated_function.stop() 
        for key in self.states:
            self.states[key] = np.zeros_like(self.states[key])

    def _simulation_step(self):
        """Calcula o próximo passo para todas as funções de transferência."""
        for key, system in self.systems.items():
            input_Value = self.dictDB[key].inputValue            
            # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
            next_state = system["A"].dot(self.states[key]) + system["B"] * input_Value
            # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
            output = system["C"].dot(next_state) + system["D"] * input_Value
            self.states[key] = next_state
            self.dictDB[key]._value = float(output)  # Armazena a saída da função de transferência 
            self.dictDB[key].valueChangedSignal.emit(self.dictDB[key]) # Atualiza as variáveis de saída (reaja conforme necessário) 