
from dataclasses import dataclass, field
from collections import deque
from typing import Dict, Tuple, Optional, Iterable, List
import numpy as np
import time
import json
import ast
import os

<<<<<<< HEAD
from react.qt_compat import QObject, Slot
=======
from PySide6.QtCore import QObject, Slot
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775
from react.react_var import ReactVar
from react.repeatFunction import RepeatFunction
import control as ctrl


__VERSION__ = "SimulTf 2025-08-22 r4 (input-normalization + safer clip)"


# ------------------------- utilidades de forma -------------------------

def _as_col(x: np.ndarray, n: Optional[int] = None) -> np.ndarray:
    arr = np.array(x, dtype=float)
    if arr.ndim == 0: arr = arr.reshape(1, 1)
    elif arr.ndim == 1: arr = arr.reshape(-1, 1)
    if n is not None:
        if arr.shape[0] > n: arr = arr[:n, :]
        elif arr.shape[0] < n: arr = np.vstack([arr, np.zeros((n - arr.shape[0], 1))])
    return arr

def _as_row(x: np.ndarray, n: Optional[int] = None) -> np.ndarray:
    arr = np.array(x, dtype=float)
    if arr.ndim == 0: arr = arr.reshape(1, 1)
    elif arr.ndim == 1: arr = arr.reshape(1, -1)
    if n is not None:
        if arr.shape[1] > n: arr = arr[:, :n]
        elif arr.shape[1] < n: arr = np.hstack([arr, np.zeros((1, n - arr.shape[1]))])
    return arr

def _scalar(x) -> float:
    return float(np.array(x, dtype=float).squeeze())


# ------------------------- sistema discreto + atraso puro contínuo -------------------------

@dataclass
class DiscreteSS:
    """
    Sistema discreto (c2d Tustin) com **atraso puro contínuo L** implementado por
    histórico (t,u) + **interpolação** de u(t-L). Robusto a jitter e a L fracionário.
    """
    A: np.ndarray; B: np.ndarray; C: np.ndarray; D: float
    x: np.ndarray  # (n,1)

    Ts: float
    delay_L: float = 0.0
    hist: deque = field(default_factory=lambda: deque(maxlen=4096))  # deque[(t,u)]
    last_u: float = 0.0

    @classmethod
    def from_tf(cls, num: Iterable[float], den: Iterable[float], Ts: float, x0: Optional[np.ndarray] = None):
        sys_ss = ctrl.tf2ss(ctrl.TransferFunction(num, den))
        sysd = ctrl.c2d(sys_ss, Ts, method='tustin')
        A = np.array(sysd.A, dtype=float); n = A.shape[0]
        B = _as_col(sysd.B, n); C = _as_row(sysd.C, n); D = _scalar(sysd.D)
        x = _as_col(np.zeros((n, 1)) if x0 is None else np.array(x0, dtype=float), n)
        return cls(A=A, B=B, C=C, D=D, x=x, Ts=float(Ts))

    def set_delay(self, seconds: float, seed_u: float = 0.0):
        self.delay_L = max(0.0, float(seconds))
        self.last_u = float(seed_u)
        self.hist.clear()
        self.hist.append((0.0, self.last_u))

    def _u_at(self, t_query: float) -> float:
        """Interpolação linear de u(t_query) no histórico com timestamps."""
        if not self.hist:
            return self.last_u
        keep_after = t_query - 2.0 * max(self.Ts, 1e-6)
        while len(self.hist) >= 3 and self.hist[1][0] < keep_after:
            self.hist.popleft()
        if t_query <= self.hist[0][0]:
            return float(self.hist[0][1])
        if t_query >= self.hist[-1][0]:
            return float(self.hist[-1][1])
        for i in range(len(self.hist) - 1):
            t0, u0 = self.hist[i]; t1, u1 = self.hist[i + 1]
            if t0 <= t_query <= t1:
                if t1 == t0: return float(u1)
                a = (t_query - t0) / (t1 - t0)
                return float((1 - a) * u0 + a * u1)
        return float(self.hist[-1][1])

    def step(self, u: float, t_now: float) -> float:
        u = float(u)
        self.last_u = u
        if not self.hist or t_now >= self.hist[-1][0]:
            self.hist.append((t_now, u))
        else:
            self.hist.append((self.hist[-1][0] + 1e-12, u))

        u_eff = self._u_at(t_now - self.delay_L) if self.delay_L > 0 else u
        y = float(self.C @ self.x + self.D * u_eff)
        self.x = self.A @ self.x + self.B * u_eff
        return y


# ------------------------- parsing do tFunc -------------------------

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

    num = _to_list(parts[0]); den = _to_list(parts[1]); delay = float(delay_str)
    return num, den, delay


# ------------------------- util: normalização de entrada -------------------------

def _normalize_input(u_raw: float) -> float:
    """
    Converte u para [0,1] a partir de heurística:
    - u > 1000 → assume 0..65535  → u/65535
    - 1 < u <= 1000 → assume 0..100 → u/100
    - caso contrário → já em 0..1
    Clipa em [0, 1] por segurança.
    """
    try:
        u = float(u_raw)
    except Exception:
        return 0.0
    if u > 1000.0:
        u = u / 65535.0
    elif u > 1.0:
        u = u / 100.0
    # já [0..1] ou negativo → clip
    if not np.isfinite(u):
        u = 0.0
    return float(np.clip(u, 0.0, 1.0))


# ------------------------- motor de simulação -------------------------

class SimulTf(QObject):
    """
    Simulador de TF(s) com **atraso puro contínuo** (sem Padé):
    • discretização por Tustin (c2d)
    • atraso via histórico (t,u) + interpolação linear (independente de jitter)
    """
    def __init__(self, stepTime_ms: int):
        super().__init__()
        self.stepTime = int(stepTime_ms)
        self.Ts = max(1e-6, self.stepTime / 1000.0)

        self.dictDB: Dict[Tuple[str, str, str], ReactVar] = {}
        self.systems: Dict[Tuple[str, str, str], DiscreteSS] = {}
        self._system_models: Dict[Tuple[str, str, str], Tuple[list, list, float]] = {}

        self._repeated_function = RepeatFunction(self._simulation_step, self.stepTime)
        self._t0_wall: Optional[float] = None  # base do relógio monotônico

        # DEBUG opcional (setar env SIMUL_TF_DEBUG=1)
        self._debug = os.environ.get("SIMUL_TF_DEBUG", "0") == "1"
        self._dbg_tick = 0

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
                # Usa heurística também para o seed
                seed_u_raw = float(data.inputValue) if data.inputValue is not None else 0.0
                seed_u = _normalize_input(seed_u_raw)
                dsys.set_delay(seconds=delay, seed_u=seed_u)
            except Exception as e:
                print(f"[SimulTf] Erro ao montar sistema: {e}")
                return
            self.systems[key] = dsys
            self._system_models[key] = (list(num), list(den), float(delay))
        else:
            self.dictDB.pop(key, None)
            self.systems.pop(key, None)
            self._system_models.pop(key, None)

    def start(self, state: bool):
        if state:
            # defensivo: se a versão antiga estiver carregada, não quebrar
            if hasattr(self, "load_states"):
                try: self.load_states()
                except Exception as e: print("[SimulTf] load_states falhou:", e)
            self._t0_wall = time.monotonic()
            self._repeated_function.start()
        else:
            self._repeated_function.stop()
            if hasattr(self, "save_states"):
                try: self.save_states()
                except Exception as e: print("[SimulTf] save_states falhou:", e)
            self._t0_wall = None

    def reset(self):
        self._repeated_function.stop()
        base = time.monotonic()
        self._t0_wall = base
        for dsys in self.systems.values():
            dsys.x[:] = 0.0
            dsys.set_delay(seconds=dsys.delay_L, seed_u=dsys.last_u)

    def _now(self) -> float:
        if self._t0_wall is None:
            self._t0_wall = time.monotonic()
        return time.monotonic() - self._t0_wall

    def _simulation_step(self):
        t_now = self._now()
        self._dbg_tick += 1
        for key, dsys in self.systems.items():
            var = self.dictDB.get(key)
            if var is None:
                continue
            u_raw = float(var.inputValue) if var.inputValue is not None else 0.0
            u = _normalize_input(u_raw)   # <<< normalização robusta
            y = dsys.step(u, t_now)

            # Clipa a saída em [0,1] (sem piso 0.0001 para não "travar" visualmente)
            new_val = float(np.clip(y, 0.0, 1.0))

            # DEBUG opcional a cada ~20 ticks
            if self._debug and (self._dbg_tick % 20 == 0):
                print(f"[SimulTf][{key}] t={t_now:.3f}  u_raw={u_raw:.2f} -> u={u:.3f}  y={new_val:.3f}")

            # Emite alteração
            var._value = new_val
            var.valueChangedSignal.emit(var)

    # ------------------------- sincronismo de StepTimer -------------------------
    def set_step_time_ms(self, step_ms: int):
        """Atualiza o passo do simulador e re‑discretiza os sistemas (preservando estado)."""
        try:
            step_ms = int(step_ms)
        except Exception:
            return
        if step_ms < 1: step_ms = 1
        was_running = False
        try:
            was_running = getattr(self._repeated_function, "running", False) or getattr(self._repeated_function, "_running", False)
        except Exception:
            pass
        try:
            self._repeated_function.stop()
        except Exception:
            pass
        self.stepTime = step_ms
        self.Ts = max(1e-6, self.stepTime / 1000.0)
        try:
            self._repeated_function = RepeatFunction(self._simulation_step, self.stepTime)
        except Exception as e:
            print(f"[SimulTf] Falha ao recriar RepeatFunction: {e}")

        for key, old_dsys in list(self.systems.items()):
            model = getattr(self, "_system_models", {}).get(key)
            if not model:
                old_dsys.Ts = self.Ts
                continue
            num, den, delay = model
            try:
                new_dsys = DiscreteSS.from_tf(num, den, Ts=self.Ts, x0=old_dsys.x)
                new_dsys.set_delay(seconds=old_dsys.delay_L, seed_u=old_dsys.last_u)
                self.systems[key] = new_dsys
            except Exception as e:
                print(f"[SimulTf] Falha ao re-discretizar {key}: {e}")
        self._t0_wall = time.monotonic()
        if was_running:
            try: self._repeated_function.start()
            except Exception as e: print(f"[SimulTf] Falha ao reiniciar RepeatFunction: {e}")

    # ------------------------- persistência -------------------------

    def save_states(self):
        for key, dsys in self.systems.items():
            var = self.dictDB.get(key)
            if not var:
                continue
            row = "|".join(key[:-1]); col = key[-1]
            try:
                payload = {
                    "A": dsys.A.tolist(), "B": dsys.B.tolist(), "C": dsys.C.tolist(),
                    "D": dsys.D, "x": dsys.x.tolist(),
                    "delay_L": dsys.delay_L, "last_u": dsys.last_u,
                    "hist": list(dsys.hist)[-64:],
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
            row = "|".join(key[:-1]); col = key[-1]
            try:
                raw = var.reactFactory.storage.getRawData("TFSTATES", row, col)
                if not raw:
                    continue
                data = json.loads(raw)

                if isinstance(data, list):
                    dsys.x = _as_col(np.array(data, dtype=float), dsys.A.shape[0])
                    continue

                if isinstance(data, dict):
                    if "x" in data:
                        dsys.x = _as_col(np.array(data["x"], dtype=float), dsys.A.shape[0])
                    if "delay_L" in data:
                        dsys.delay_L = float(data["delay_L"])
                    if "last_u" in data:
                        dsys.last_u = float(data["last_u"])
                    dsys.hist.clear()
                    hist = data.get("hist", [])
                    if isinstance(hist, list) and hist:
                        for item in hist:
                            try:
                                t_i, u_i = float(item[0]), float(item[1])
                                dsys.hist.append((t_i, u_i))
                            except Exception:
                                pass
                    else:
                        dsys.hist.append((0.0, dsys.last_u))
            except Exception as e:
                print(f"[SimulTf] Erro ao carregar estado {key}: {e}")
