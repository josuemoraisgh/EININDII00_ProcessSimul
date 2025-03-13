import math
import threading
import time
import numpy as np
import control as ctrl

class TransferFunction:
    def __init__(self, numerator, denominator, sampling_time, plant_output_callback=None):
        """
        numerator: lista de coeficientes do numerador.
        denominator: lista de coeficientes do denominador.
        sampling_time: tempo de amostragem em segundos.
        plant_output_callback: função callback com a assinatura callback(output, state)
        """
        self.numerator = numerator
        self.denominator = denominator
        self.sampling_time = sampling_time  # em segundos
        self.plant_output_callback = plant_output_callback
        self.input_value = 0.0

        # Converte a função de transferência contínua para espaço de estado
        sys_tf = ctrl.TransferFunction(numerator, denominator)
        sys_ss = ctrl.tf2ss(sys_tf)
        # Converte o modelo contínuo para discreto usando Tustin (bilinear)
        sysd = ctrl.c2d(sys_ss, sampling_time, method='tustin')
        self.A = np.array(sysd.A)
        self.B = np.array(sysd.B)
        self.C = np.array(sysd.C)
        self.D = np.array(sysd.D)

        self.order = self.A.shape[0]
        self.state = np.zeros((self.order, 1))

        self._simulate = False
        self._lock = threading.Lock()
        self._thread = None

    def start(self):
        self._simulate = True
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._simulation_loop)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        self._simulate = False
        if self._thread is not None:
            self._thread.join(timeout=1)

    def close(self):
        self.stop()

    def reestart(self):
        with self._lock:
            self.state = np.zeros((self.order, 1))

    def set_input_value(self, input_value):
        with self._lock:
            self.input_value = input_value

    def _simulation_loop(self):
        next_time = time.time()
        while self._simulate:
            with self._lock:
                # Calcula o próximo estado: x[k+1] = A * x[k] + B * u[k]
                next_state = self.A.dot(self.state) + self.B * self.input_value
                # Calcula a saída: y[k] = C * x[k+1] + D * u[k]
                output = self.C.dot(next_state) + self.D * self.input_value
                self.state = next_state
                current_output = float(output)
                current_state = self.state.flatten().tolist()
            # Chama o callback, se definido
            if self.plant_output_callback is not None:
                self.plant_output_callback(current_output, current_state)
            # Aguarda até o próximo instante de amostragem
            next_time += self.sampling_time
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

# --- Exemplo de uso ---
if __name__ == "__main__":
    def update_output(output, state):
        print(f"Output: {output:.4f}   State: {state}")

    # Exemplo: função de transferência de primeira ordem: G(s) = 1/(s+1)
    num = [1.0]
    den = [1.0, 1.0]
    Ts = 0.1  # 100 ms de amostragem

    plant = TransferFunction(num, den, Ts, plant_output_callback=update_output)
    plant.start()

    try:
        t0 = time.time()
        while time.time() - t0 < 5:  # Simula por 5 segundos
            # Exemplo: entrada senoidal
            plant.set_input_value(math.sin(2 * math.pi * 0.5 * (time.time() - t0)))
            time.sleep(Ts)
    except KeyboardInterrupt:
        pass
    finally:
        plant.close()