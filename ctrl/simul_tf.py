from react.repeatFunction import RepeatFunction
from react.reactDB import ReactDataBase
from inter.istate import DBState
import control as ctrl
import numpy as np
import ast  # Para converter strings de listas em listas reais
import re
class SimulTf:
    def __init__(self, reactDataBase: ReactDataBase, stepTime):
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

        self.systems = {"HART":{},"MODBUS":{}}  # Armazena os sistemas no espaço de estado
        self.states = {"HART":{},"MODBUS":{}}   # Armazena os estados de cada sistema
        self.inputs = {"HART":{},"MODBUS":{}}   # Armazena os inputs de cada sistema

        # Converte todas as funções de transferência do dicionário
        for rowTfName, colTfName in zip(self.reactDataBase.hrt_storage.rowTfNames, self.reactDataBase.hrt_storage.colTfNames):
            num_str, den_str, input_str = self.reactDataBase.hrt_storage.getStrData(rowTfName,colTfName).split(",")  # Divide
            num = ast.literal_eval(num_str[1:].replace(" ",","))  # Converte string de lista para lista real
            den = ast.literal_eval(den_str.replace(" ",","))
            if re.search(r'([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', input_str):
                input_value = self.reactDataBase.dfhrt.iloc[rowTfName,colTfName].evaluate_expression(self, input_str)  # Converte para número real
            else:
                input_value = float(input_str)
                
            sys_tf = ctrl.TransferFunction(num, den)
            sys_ss = ctrl.tf2ss(sys_tf)
            sysd = ctrl.c2d(sys_ss, stepTime, method='tustin')

            self.systems["HART"][rowTfName, colTfName] = {
                "A": np.array(sysd.A),
                "B": np.array(sysd.B),
                "C": np.array(sysd.C),
                "D": np.array(sysd.D)
            }
            self.states["HART"][rowTfName, colTfName] = np.zeros((sysd.A.shape[0], 1))  # Estado inicial zerado
            self.inputs["HART"][rowTfName, colTfName] = input_value

        # Converte todas as funções de transferência do dicionário
        for rowTfName, colTfName in zip(self.reactDataBase.mb_storage.rowTfNames, self.reactDataBase.mb_storage.colTfNames):
            num_str, den_str, input_str = self.reactDataBase.mb_storage.getStrData(rowTfName,colTfName).split(",")  # Divide
            num = ast.literal_eval(num_str[1:].replace(" ",","))  # Converte string de lista para lista real
            den = ast.literal_eval(den_str.replace(" ",","))
            if re.search(r'([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', input_str):
                input_value = self.reactDataBase.dfmb.iloc[rowTfName,colTfName].evaluate_expression(self, input_str)  # Converte para número real
            else:
                input_value = float(input_str)
                
            sys_tf = ctrl.TransferFunction(num, den)
            sys_ss = ctrl.tf2ss(sys_tf)
            sysd = ctrl.c2d(sys_ss, stepTime, method='tustin')

            self.systems["MODBUS"][rowTfName, colTfName] = {
                "A": np.array(sysd.A),
                "B": np.array(sysd.B),
                "C": np.array(sysd.C),
                "D": np.array(sysd.D)
            }
            self.states["MODBUS"][rowTfName, colTfName] = np.zeros((sysd.A.shape[0], 1))  # Estado inicial zerado
            self.inputs["MODBUS"][rowTfName, colTfName] = input_value
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
            for key in self.states["HART"]:
                self.states["HART"][key] = np.zeros_like(self.states[key])
            for key in self.states["MODBUS"]:
                self.states["MODBUS"][key] = np.zeros_like(self.states[key])

    def changeInputValues(self, source, rowTfName, colTfName, input_str):
        """Define os valores de entrada de controle. input_dict deve ter o formato {'tf_name': valor}."""
        if source == "HART":
            self.inputs["HART"][rowTfName, colTfName] = self.reactDataBase.dfhrt.loc(input_str,colTfName,DBState.humanValue)  # Converte para número real
        else: 
            self.inputs["MODBUS"][rowTfName, colTfName] = self.reactDataBase.dfmb.loc(input_str,colTfName,DBState.humanValue)  # Converte para número real            
            
    def _simulation_step(self):
        """Calcula o próximo passo para todas as funções de transferência."""
        for key, system in self.systems["HART"].items():
            # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
            next_state = system["A"].dot(self.states["HART"][key]) + system["B"] * self.inputs["HART"][key]
            # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
            output = system["C"].dot(next_state) + system["D"] * self.inputs["HART"][key]
            self.states["HART"][key] = next_state
            self.reactDataBase.hrt_storage.tf_dict[key] = float(output)  # Armazena a saída da função de transferência 
            self.reactDataBase.dfhrt.loc[key].valueChanged.emit() # Atualiza as variáveis de saída (reaja conforme necessário) 
        for key, system in self.systems["MODBUS"].items():
            # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
            next_state = system["A"].dot(self.states["MODBUS"][key]) + system["B"] * self.inputs["MODBUS"][key]
            # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
            output = system["C"].dot(next_state) + system["D"] * self.inputs["MODBUS"][key]
            self.states[key] = next_state
            self.reactDataBase.mb_storage.tf_dict[key] = float(output)  # Armazena a saída da função de transferência 
            self.reactDataBase.dfmb.loc[key].valueChanged.emit() # Atualiza as variáveis de saída (reaja conforme necessário)            
