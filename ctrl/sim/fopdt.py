
from collections import deque

class FOPDTSimulator:
    """First-Order Plus Dead-Time simulator.
    y' = (-y + Kp * u_delay)/tau
    with delay buffer of length N = round(L/dt)
    """
    def __init__(self):
        self.Kp = 1.0
        self.tau = 1.0
        self.L = 0.0
        self.dt = 0.05
        self.t = 0.0
        self.y = 0.0
        self.u = 0.0
        self._buf = deque([0.0], maxlen=1)
        self.running = False

    def configure(self, Kp: float, tau: float, L: float, dt: float, y0: float = 0.0):
        self.Kp = float(Kp); self.tau = float(tau); self.L = float(L); self.dt = float(dt)
        self.t = 0.0; self.y = float(y0); self.u = 0.0
        self._init_buf()

    def _init_buf(self):
        N = max(1, int(round(self.L / self.dt))) if self.dt > 0 else 1
        self._buf = deque([self.u]*N, maxlen=N)

    def set_u(self, u: float):
        self.u = float(u)

    def step(self):
        if not self.running: return None
        if len(self._buf) == 0:
            u_delay = self.u
        else:
            u_delay = self._buf[0]
            self._buf.append(self.u)
            self._buf.popleft()
        dydt = (-self.y + self.Kp * u_delay) / self.tau if self.tau > 0 else 0.0
        self.y += dydt * self.dt
        self.t += self.dt
        return self.t, self.y, self.u
