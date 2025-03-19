from react.repeatFunction import RepeatFunction
from hrt.hrt_data import HrtData
import control as ctrl
import numpy as np
import ast  # Para converter strings de listas em listas reais
class SimulTf:
    def __init__(self, hrt_data: HrtData, stepTime):
        """
        tf_dict: dicionário onde:
            - chave: nome da função de transferência (str).
            - valor: string no formato "num, den, input", onde:
                * num e den são listas representadas como strings.
                * input é um número como string.
        stepTime: tempo de integração em segundos.
        """
        self.hrt_data = hrt_data
        self.stepTime = stepTime  # em segundos

        self.systems = {}  # Armazena os sistemas no espaço de estado
        self.states = {}   # Armazena os estados de cada sistema
        self.inputs = {}   # Armazena os inputs de cada sistema

        # Converte todas as funções de transferência do dicionário
        for rowTfName, colTfName in zip(self.hrt_data.rowTfNames, self.hrt_data.colTfNames):
            num_str, den_str, input_str = self.hrt_data.getStrData(rowTfName,colTfName).split(",")  # Divide
            num = ast.literal_eval(num_str[1:].replace(" ",","))  # Converte string de lista para lista real
            den = ast.literal_eval(den_str.replace(" ",","))
            input_value = float(input_str) # self.hrt_data.get_variable(input_str,colTfName,False)  # Converte para número real
            
            sys_tf = ctrl.TransferFunction(num, den)
            sys_ss = ctrl.tf2ss(sys_tf)
            sysd = ctrl.c2d(sys_ss, stepTime, method='tustin')

            self.systems[rowTfName, colTfName] = {
                "A": np.array(sysd.A),
                "B": np.array(sysd.B),
                "C": np.array(sysd.C),
                "D": np.array(sysd.D)
            }
            self.states[rowTfName, colTfName] = np.zeros((sysd.A.shape[0], 1))  # Estado inicial zerado
            self.inputs[rowTfName, colTfName] = input_value

        # Inicializa a função repetida para rodar a simulação de forma contínua
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)

    def changeData(self):
        """Atualiza os sistemas com novos parâmetros."""
        self.stop()
        self.__init__(self.hrt_data, self.stepTime)

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
            for key in self.states:
                self.states[key] = np.zeros_like(self.states[key])

    def changeInputValues(self, rowTfName, colTfName, input_str):
        """Define os valores de entrada de controle. input_dict deve ter o formato {'tf_name': valor}."""
        self.inputs[rowTfName, colTfName] = self.hrt_data.get_variable(input_str,colTfName,False)  # Converte para número real
            
    def _simulation_step(self):
        """Calcula o próximo passo para todas as funções de transferência."""
        outputs = {}
        for key, system in self.systems.items():
            # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
            next_state = system["A"].dot(self.states[key]) + system["B"] * self.inputs[key]
            # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
            output = system["C"].dot(next_state) + system["D"] * self.inputs[key]
            self.states[key] = next_state
            outputs[key] = float(output)  # Armazena a saída da função de transferência
        # Atualiza as variáveis de saída (reaja conforme necessário)
        self.hrt_data.tf_dict[key] = outputs         
