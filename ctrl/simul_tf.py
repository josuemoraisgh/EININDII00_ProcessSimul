import numpy as np
import control as ctrl
from react.repeatFunction import RepeatFunction 
from react.reactiveVariable import ReactiveVariable 

class SimulTf:
    def __init__(self, numerator, denominator, stepTime, outputReactiveVariable: ReactiveVariable):
        """
        numerator: lista de coeficientes do numerador.
        denominator: lista de coeficientes do denominador.
        stepTime: tempo do passo de integração em segundos.
        plant_output_callback: função callback com a assinatura callback(output, state)
        """
        self.numerator = numerator
        self.denominator = denominator
        self.stepTime = stepTime  # em milisegundos
        self.outputReactiveVariable = outputReactiveVariable
        self.input_value = 0.0

        # Converte a função de transferência contínua para espaço de estado
        sys_tf = ctrl.TransferFunction(numerator, denominator)
        sys_ss = ctrl.tf2ss(sys_tf)
        sysd = ctrl.c2d(sys_ss, stepTime, method='tustin')
        self.A = np.array(sysd.A)
        self.B = np.array(sysd.B)
        self.C = np.array(sysd.C)
        self.D = np.array(sysd.D)

        self.state = np.zeros((self.A.shape[0], 1))

        # Usando RepeatedFunction para rodar em outra thread
        self._repeated_function = RepeatFunction(self._simulation_step, stepTime)

    def changeData(self, numerator, denominator, stepTime):
        self.stop()
        self.numerator = numerator
        self.denominator = denominator
        self.stepTime = stepTime  # em milisegundos
        self._repeated_function.changeInterval(stepTime)

    def start(self):
        """Inicia a execução da simulação."""
        self._repeated_function.start()

    def stop(self):
        """Para a execução da simulação."""
        self._repeated_function.stop()

    def close(self):
        """Finaliza a execução e zera o estado."""
        self.state = np.zeros((self.A.shape[0], 1))
        self.stop()

    def set_input_value(self, input_value):
        """Define o valor da entrada de controle."""
        self.input_value = input_value

    def _simulation_step(self):
        """Calcula o próximo passo da simulação e envia os dados para a thread principal."""
        # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
        next_state = self.A.dot(self.state) + self.B * self.input_value
        # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
        output = self.C.dot(next_state) + self.D * self.input_value
        self.state = next_state
        self.outputReactiveVariable.set(float(output))
