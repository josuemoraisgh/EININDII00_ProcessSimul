from dataclasses import dataclass, field
from collections import deque
from typing import Dict, Tuple, Optional, Iterable, List
import numpy as np

from PySide6.QtCore import QObject, Slot
from react.react_var import ReactVar
from react.repeatFunction import RepeatFunction
import control as ctrl
import json
import ast


def _as_col(x: np.ndarray, n: Optional[int] = None) -> np.ndarray:
    arr = np.array(x, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1, 1)
    elif arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if n is not None:
        if arr.shape[0] > n:
            arr = arr[:n, :]
        elif arr.shape[0] < n:
            pad = np.zeros((n - arr.shape[0], 1), dtype=float)
            arr = np.vstack([arr, pad])
    return arr


def _as_row(x: np.ndarray, n: Optional[int] = None) -> np.ndarray:
    arr = np.array(x, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1, 1)
    elif arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if n is not None:
        if arr.shape[1] > n:
            arr = arr[:, :n]
        elif arr.shape[1] < n:
            pad = np.zeros((1, n - arr.shape[1]), dtype=float)
            arr = np.hstack([arr, pad])
    return arr


def _scalar(x) -> float:
    arr = np.array(x, dtype=float)
    return float(arr.squeeze())


@dataclass
class DiscreteSS:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: float
    x: np.ndarray  # (n,1)

    delay_steps: int = 0
    delay_buf: deque = field(default_factory=lambda: deque([0.0], maxlen=1))

    @classmethod
    def from_tf(cls, num: Iterable[float], den: Iterable[float], Ts: float, x0: Optional[np.ndarray] = None):
        sys_ss = ctrl.tf2ss(ctrl.TransferFunction(num, den))
        sysd = ctrl.c2d(sys_ss, Ts, method='tustin')
        A = np.array(sysd.A, dtype=float)
        n = A.shape[0]
        B = _as_col(sysd.B, n)
        C = _as_row(sysd.C, n)
        D = _scalar(sysd.D)
        x = _as_col(np.zeros((n, 1), dtype=float) if x0 is None else np.array(x0, dtype=float), n)
        return cls(A=A, B=B, C=C, D=D, x=x, delay_steps=0, delay_buf=deque([0.0], maxlen=1))

    def set_delay(self, seconds: float, Ts: float, seed_u: float = 0.0):
        steps = int(round(max(0.0, float(seconds)) / float(Ts))) if Ts > 0 else 0
        self.delay_steps = steps
        maxlen = max(1, steps)  # nunca 0
        seed = float(seed_u)
        self.delay_buf = deque([seed] * maxlen, maxlen=maxlen)

    def ensure_delay_buf(self, fallback_u: float = 0.0):
        """Garante que delay_buf sempre tenha pelo menos 1 elemento e maxlen válido."""
        if self.delay_steps <= 0:
            # mesmo sem atraso, garantimos um elemento para acesso seguro
            if (self.delay_buf is None) or (self.delay_buf.maxlen is None) or (self.delay_buf.maxlen < 1):
                self.delay_buf = deque([float(fallback_u)], maxlen=1)
            if len(self.delay_buf) == 0:
                self.delay_buf.append(float(fallback_u))
            return
        # atraso > 0
        needed = max(1, self.delay_steps)
        if (self.delay_buf is None) or (self.delay_buf.maxlen is None) or (self.delay_buf.maxlen < 1):
            self.delay_buf = deque([float(fallback_u)] * needed, maxlen=needed)
        elif self.delay_buf.maxlen != needed:
            # reconstroi preservando os mais recentes
            buf = list(self.delay_buf)[-needed:] if len(self.delay_buf) else [float(fallback_u)] * needed
            self.delay_buf = deque(buf, maxlen=needed)
        if len(self.delay_buf) == 0:
            self.delay_buf.append(float(fallback_u))

    def step(self, u: float) -> float:
        u = float(u)
        self.ensure_delay_buf(fallback_u=u)

        if self.delay_steps > 0:
            # acesso seguro
            u_delay = self.delay_buf[0] if len(self.delay_buf) else u
            self.delay_buf.append(u)
            if len(self.delay_buf) > 0:
                self.delay_buf.popleft()
        else:
            u_delay = u

        y = float(self.C @ self.x + self.D * u_delay)
        self.x = self.A @ self.x + self.B * u_delay
        return y


def _parse_tfunc(tfunc: str):
    if not tfunc:
        raise ValueError("tFunc vazio.")
    parts = [p.strip() for p in tfunc.strip().strip(',').split(',', maxsplit=3)]
    if len(parts) < 2:
        raise ValueError(f"tFunc inválido: '{tfunc}'")
    delay_str = parts[2] if len(parts) >= 3 else "0.0"

    def _to_list(s: str) -> List[float]:
        content = s.strip().strip('[]').replace(' ', ',')
        return ast.literal_eval(f"[{content}]")

    num = _to_list(parts[0])
    den = _to_list(parts[1])
    delay = float(delay_str)
    return num, den, delay


class SimulTf(QObject):
    def __init__(self, stepTime_ms: int):
        super().__init__()
        self.stepTime = int(stepTime_ms)
        self.Ts = max(1e-6, self.stepTime / 1000.0)

        self.dictDB: Dict[Tuple[str, str, str], ReactVar] = {}
        self.systems: Dict[Tuple[str, str, str], DiscreteSS] = {}

        self._repeated_function = RepeatFunction(self._simulation_step, self.stepTime)

    @Slot(object, bool)
    def tfConnect(self, data: ReactVar, isConnect: bool):
        key = (data.tableName, data.rowName, data.colName)
        if isConnect:
            self.dictDB[key] = data
            tfunc = data.getTFunc() or ""
            try:
                num, den, delay = _parse_tfunc(tfunc)
            except Exception as e:
                print(f"[SimulTf] Erro ao parsear tFunc '{tfunc}': {e}")
                return
            try:
                dsys = DiscreteSS.from_tf(num, den, Ts=self.Ts)
                seed_u = float(data.inputValue) if data.inputValue is not None else 0.0
                dsys.set_delay(seconds=delay, Ts=self.Ts, seed_u=seed_u)
            except Exception as e:
                print(f"[SimulTf] Erro ao montar sistema: {e}")
                return
            self.systems[key] = dsys
        else:
            self.dictDB.pop(key, None)
            self.systems.pop(key, None)

    def start(self, state: bool):
        if state:
            self.load_states()
            # confere buffers após carregar
            for dsys in self.systems.values():
                dsys.ensure_delay_buf()
            self._repeated_function.start()
        else:
            self._repeated_function.stop()
            self.save_states()

    def reset(self):
        self._repeated_function.stop()
        for dsys in self.systems.values():
            dsys.x[:] = 0.0
            # re-semeia o buffer com o último valor válido (ou 0)
            last = dsys.delay_buf[0] if len(dsys.delay_buf) else 0.0
            dsys.set_delay(seconds=dsys.delay_steps * self.Ts, Ts=self.Ts, seed_u=last)

    def _simulation_step(self):
        for key, dsys in self.systems.items():
            var = self.dictDB.get(key)
            if var is None:
                continue
            u = float(var.inputValue) if var.inputValue is not None else 0.0
            y = dsys.step(u)
            new_val = float(np.clip(y, 0.0001, 1.0))
            var._value = new_val
            var.valueChangedSignal.emit(var)

    def save_states(self):
        for key, dsys in self.systems.items():
            var = self.dictDB.get(key)
            if not var:
                continue
            row = "|".join(key[:-1])
            col = key[-1]
            try:
                payload = {
                    "A": dsys.A.tolist(),
                    "B": dsys.B.tolist(),
                    "C": dsys.C.tolist(),
                    "D": dsys.D,
                    "x": dsys.x.tolist(),
                    "delay_steps": dsys.delay_steps,
                    "delay_buf": list(dsys.delay_buf),
                }
                s = json.dumps(payload)
                var.reactFactory.storage.setRawData("TFSTATES", row, col, s)
            except Exception as e:
                print(f"[SimulTf] Erro ao salvar estado {key}: {e}")

    def load_states(self):
        for key, var in list(self.dictDB.items()):
            dsys = self.systems.get(key)
            if not dsys:
                continue
            row = "|".join(key[:-1])
            col = key[-1]
            try:
                raw = var.reactFactory.storage.getRawData("TFSTATES", row, col)
                if not raw:
                    continue
                data = json.loads(raw)
                # compat antigo: lista simples = apenas x
                if isinstance(data, list):
                    dsys.x = _as_col(np.array(data, dtype=float), dsys.A.shape[0])
                elif isinstance(data, dict):
                    if "x" in data:
                        dsys.x = _as_col(np.array(data["x"], dtype=float), dsys.A.shape[0])
                    if "delay_steps" in data:
                        dsys.delay_steps = int(data["delay_steps"])
                    # reconstrói delay_buf com tamanho correto; se vier vazio, semeia com 0
                    if "delay_buf" in data:
                        buf = [float(v) for v in data["delay_buf"]]
                    else:
                        buf = []
                    needed = max(1, dsys.delay_steps)
                    if not buf:
                        buf = [0.0] * needed
                    else:
                        buf = buf[-needed:]
                    dsys.delay_buf = deque(buf, maxlen=needed)
            except Exception as e:
                print(f"[SimulTf] Erro ao carregar estado {key}: {e}")
