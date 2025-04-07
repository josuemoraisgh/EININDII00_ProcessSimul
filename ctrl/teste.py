import numpy as np
import control as ctrl
import matplotlib.pyplot as plt

# Parâmetros do sistema contínuo
num = [0.0227]
den = [2.5, 1]
delay = 1

# Parâmetros de simulação
step_time_ms = 500         # passo de 500 ms
total_time_s = 10
input_value = 1.0
Ts = step_time_ms / 1000.0

# Discretização
G = ctrl.TransferFunction(num, den)
num_delay, den_delay = ctrl.pade(delay, 1)
delay_tf = ctrl.TransferFunction(num_delay, den_delay)
sys_tf = G * delay_tf
sys_ss = ctrl.tf2ss(sys_tf)
sysd = ctrl.c2d(sys_ss, Ts, method='tustin')

# Matrizes
A = np.array(sysd.A)
B = np.array(sysd.B)
C = np.array(sysd.C)
D = np.array(sysd.D)
x = np.zeros((A.shape[0], 1))

# Tempo e resposta
outputs = []
times = []

# 1ª metade: entrada = 1
t1 = np.arange(0, total_time_s/2, Ts)
for t in t1:
    y = C.dot(x) + D * input_value
    outputs.append(float(y))
    times.append(t)
    x = A.dot(x) + B * input_value

# 2ª metade: entrada = 0
t2 = np.arange(total_time_s/2, total_time_s, Ts)
for t in t2:
    y = C.dot(x) + D * 0
    outputs.append(float(y))
    times.append(t)
    x = A.dot(x) + B * 0

# Plot
plt.plot(times, outputs, marker='o')
plt.title("Resposta ao Degrau com Atraso de Padé")
plt.xlabel("Tempo (s)")
plt.ylabel("Saída")
plt.grid(True)
plt.tight_layout()
plt.show()