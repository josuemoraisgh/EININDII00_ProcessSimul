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
    delay = {} 
      
    def __init__(self, stepTime):
        super().__init__()
        self.stepTime = stepTime  # em milisegundos
        # Inicializa a função repetida para rodar a simulação de forma contínua
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)        

    @Slot()
    def tfConnect(self, data: ReactVar,  isConnect: bool):
        if isConnect == True:
            self.dictDB[(data.tableName, data.rowName, data.colName)] = data
            num_str, den_str, _, delay = data.getTFunc().split(",")
            num = ast.literal_eval(num_str.replace(" ", ","))
            den = ast.literal_eval(den_str.replace(" ", ","))

            self.delay[(data.tableName, data.rowName, data.colName)] = float(delay)

            G = ctrl.TransferFunction(num, den)
            # Aproximação de Padé para o atraso de self.delay segundos (ordem 1)
            num_delay, den_delay = ctrl.pade(self.delay, 1)  # atraso = 2s, ordem = 1
            # Função de transferência do atraso
            delay_tf = ctrl.TransferFunction(num_delay, den_delay)
            # Sistema completo com atraso
            sys_tf = G * delay_tf
            
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

            # Calcula a saída com o estado atual
            output = system["C"].dot(self.states[key]) + system["D"] * input_Value

            # Atualiza o estado
            self.states[key] = system["A"].dot(self.states[key]) + system["B"] * input_Value

            # Armazena a saída e emite sinal
            self.dictDB[key]._value = float(output)
            self.dictDB[key].valueChangedSignal.emit(self.dictDB[key])
 