import numpy as np
import control as ctrl
import matplotlib.pyplot as plt

# Parâmetros do sistema contínuo
num = [0.0227]
den = [2.5, 1]

# Parâmetros de simulação
step_time_ms = 500         # passo de 500 ms
total_time_s = 10           # até 4 segundos
input_value = 1.0          # degrau unitário
Ts = step_time_ms / 1000.0 # tempo de amostragem

# Discretização via Tustin (bilinear)
sys_tf = ctrl.TransferFunction(num, den)
sys_ss = ctrl.tf2ss(sys_tf)
sysd = ctrl.c2d(sys_ss, Ts, method='tustin')

# Extrair matrizes
A = np.array(sysd.A)
B = np.array(sysd.B)
C = np.array(sysd.C)
D = np.array(sysd.D)

# Estado inicial
x = np.zeros((A.shape[0], 1))

# Vetores para registrar tempo e saída
outputs = []
times = np.arange(0, total_time_s + Ts, Ts)

# Simulação
for t in times:
    # Saída no instante atual
    y = C.dot(x) + D * input_value
    outputs.append(float(y))

    # Atualiza estado
    x = A.dot(x) + B * input_value

# Plot
plt.plot(times, outputs, marker='o')
plt.title("Resposta ao Degrau - Discretização (Tustin)")
plt.xlabel("Tempo (s)")
plt.ylabel("Saída")
plt.grid(True)
plt.tight_layout()
plt.show()
