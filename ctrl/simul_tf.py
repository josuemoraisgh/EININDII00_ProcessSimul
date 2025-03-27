from react.repeatFunction import RepeatFunction
from react.react_db import ReactDB
from db.db_state import DBState
import control as ctrl
import numpy as np
import ast  # Para converter strings de listas em listas reais
import re
class SimulTf:
    def __init__(self, reactDataBase: ReactDB, stepTime):
        """
        tf_dict: dicionário onde:
            - chave: nome da função de transferência (str).
            - valor: string no formato "num, den, input", onde:
                * num e den são listas representadas como strings.
                * input é um número como string.
        stepTime: tempo de integração em segundos.
        """
        self.reactDataBase = reactDataBase
        self.stepTime = stepTime  # em segundos
            
        self.systems = {}  # Armazena os sistemas no espaço de estado
        self.states = {}   # Armazena os estados de cada sistema
        self.inputs = {}   # Armazena os inputs de cada sistema
            
        # Converte todas as funções de transferência do dicionário
        for tableName in self.reactDataBase.tableNames:
            self.systems[tableName] = {}  # Armazena os sistemas no espaço de estado
            self.states[tableName] = {}   # Armazena os estados de cada sistema
            self.inputs[tableName] = {}   # Armazena os inputs de cada sistema            
            for rowTfName, colTfName in zip(self.reactDataBase.rowTfNames, self.reactDataBase.colTfNames):
                num_str, den_str, input_str = self.reactDataBase.storage[tableName].getData(rowTfName,colTfName).split(",")  # Divide
                num = ast.literal_eval(num_str[1:].replace(" ",","))  # Converte string de lista para lista real
                den = ast.literal_eval(den_str.replace(" ",","))
                if re.search(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', input_str):
                    input_value = input_str
                else:
                    input_value = float(input_str)
                    
                sys_tf = ctrl.TransferFunction(num, den)
                sys_ss = ctrl.tf2ss(sys_tf)
                sysd = ctrl.c2d(sys_ss, stepTime, method='tustin')

                self.systems[tableName][rowTfName, colTfName] = {
                    "A": np.array(sysd.A),
                    "B": np.array(sysd.B),
                    "C": np.array(sysd.C),
                    "D": np.array(sysd.D)
                }
                self.states[tableName][rowTfName, colTfName] = np.zeros((sysd.A.shape[0], 1))  # Estado inicial zerado
                self.inputs[tableName][rowTfName, colTfName] = input_value
                
        # Inicializa a função repetida para rodar a simulação de forma contínua
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)


    def start(self, state:bool):
        """Inicia a execução da simulação."""
        if state:
            self._repeated_function.start()
        else:
            self._repeated_function.stop()
   
    def reset(self, state:bool):
        """Finaliza a execução e reseta os estados."""
        if state:        
            self.stop() 
            for tableName in self.reactDataBase.tableNames:                   
                for key in self.states[tableName]:
                    self.states[tableName][key] = np.zeros_like(self.states[tableName][key])

    def changeInputValues(self, tableName, rowTfName, colTfName, input_str):
        """Define os valores de entrada de controle. input_dict deve ter o formato {'tf_name': valor}."""
        if not re.search(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', input_str):
            input_str = float(input_str)
        self.inputs[tableName][rowTfName, colTfName] = input_str
            
    def _simulation_step(self):
        """Calcula o próximo passo para todas as funções de transferência."""
        for tableName in self.reactDataBase.tableNames:
            for key, system in self.systems[tableName].items():
                input_Value = self.inputs[tableName][key]
                if isinstance(input_Value, str):
                    input_Value = self.reactDataBase.df[tableName].iloc[key].evaluate_expression(self, input_Value)  # Converte para número real            
                # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
                next_state = system["A"].dot(self.states[tableName][key]) + system["B"] * input_Value
                # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
                output = system["C"].dot(next_state) + system["D"] * input_Value
                self.states[tableName][key] = next_state
                self.reactDataBase.tf_ref.value[tableName][key] = float(output)  # Armazena a saída da função de transferência 
                self.reactDataBase.df[tableName].loc[key].valueChanged.emit() # Atualiza as variáveis de saída (reaja conforme necessário) 