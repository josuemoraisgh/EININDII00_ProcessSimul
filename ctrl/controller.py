
import time, inspect, asyncio
from typing import Optional
from PySide6.QtCore import QObject, QTimer, Signal
from .buffers import DataBuffers
from .utils import u_human_to_percent, u_percent_to_human
from .sim.fopdt import FOPDTSimulator

class PlantController(QObject):
    simStartStop = Signal(bool)
    simReset = Signal()

    def __init__(self, model, canvas, parent=None):
        super().__init__(parent)
        self.model = model
        self.canvas = canvas
        self.buff = DataBuffers(200_000)
        self._last_u_percent: Optional[float] = None
        self._last_y: Optional[float] = None
        self.t0: Optional[float] = None
        self.running = False

        # real-timer
        self.real_timer = QTimer(self)
        self.real_timer.timeout.connect(self._on_real_tick)

        # simulator
        self.sim = FOPDTSimulator()
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_tick)

    # ---------- RV helpers ----------
    def _read_sync(self, rv):
        if rv is None: return None
        for m in ("read_sync", "read", "value", "getValue"):
            f = getattr(rv, m, None)
            if not callable(f): continue
            if inspect.iscoroutinefunction(f):  # não criar coroutine
                continue
            try:
                if m == "getValue":
                    try: val = f(None)
                    except TypeError: val = f()
                else:
                    val = f()
            except Exception:
                continue
            if inspect.isawaitable(val):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running(): return None
                    return float(loop.run_until_complete(val))
                except Exception:
                    return None
            try: return float(val)
            except Exception: pass
        for attr in ("humanValue", "value", "_value"):
            try:
                val = getattr(rv, attr)
                return float(val)
            except Exception: pass
        return None

    def _write_sync(self, rv, value: float) -> bool:
        if rv is None: return False
        candidates = [
            ("setValue", (value, True)),
            ("setValue", (value,)),
            ("write", (value,)),
            ("write_sync", (value,)),
            ("set", (value,)),
            ("update", (value,)),
            ("setHumanValue", (value,)),
            ("set_value", (value,)),
            ("put", (value,)),
        ]
        for name, args in candidates:
            f = getattr(rv, name, None)
            if callable(f) and not inspect.iscoroutinefunction(f):
                try: f(*args); return True
                except Exception: continue
        for attr in ("humanValue", "value", "_value"):
            try: setattr(rv, attr, float(value)); return True
            except Exception: pass
        return False

    # ---------- Real loop ----------
    def start_real(self, interval_ms: int, rv_u, rv_y):
        cur_h_u = self._read_sync(rv_u); cur_y = self._read_sync(rv_y)
        if cur_h_u is None: cur_h_u = 0.0
        if cur_y   is None: cur_y   = 0.0
        self._last_u_percent = u_human_to_percent(cur_h_u)
        self._last_y = float(cur_y)
        self.t0 = time.monotonic(); self.buff.clear()
        self.buff.append(0.0, y=self._last_y, u=self._last_u_percent)
        self._auto_axes(); self._redraw()
        self.running = True
        self.simStartStop.emit(True)
        self.real_timer.start(int(max(1, interval_ms)))

    def stop_real(self):
        self.running = False
        self.simStartStop.emit(False)
        try: self.real_timer.stop()
        except Exception: pass

    def reset(self):
        self.stop_real()
        y0 = 0.0 if self._last_y is None else float(self._last_y)
        u0 = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        self.t0 = time.monotonic(); self.buff.clear(); self.buff.append(0.0, y=y0, u=u0)
        self._auto_axes(); self._redraw()
        self.simReset.emit()

    def _on_real_tick(self):
        if not self.running or self.t0 is None: return
        # valores mais recentes cacheados via sinais externos (se existirem)
        u_val = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        y_val = 0.0 if self._last_y is None else float(self._last_y)
        t = time.monotonic() - self.t0
        self.buff.append(t, y=y_val, u=u_val)
        self._auto_axes(); self._redraw()

    def cache_external_u(self, val_human: float):
        self._last_u_percent = u_human_to_percent(val_human)

    def cache_external_y(self, val: float):
        self._last_y = float(val)

    # ---------- Simulator ----------
    def sim_start(self, Kp: float, tau: float, L: float, dt_s: float, interval_ms: int, y0: float):
        self.sim.configure(Kp, tau, L, dt_s, y0=y0)
        self.sim.running = True
        self.buff.clear()
        self.t0 = time.monotonic()
        self._auto_axes(); self._redraw()
        self.sim_timer.start(int(max(1, interval_ms)))

    def sim_stop(self):
        self.sim.running = False
        try: self.sim_timer.stop()
        except Exception: pass

    def sim_plus_minus_A(self, delta: float, rv_u=None, is_sim_tab=False):
        if is_sim_tab:
            self.sim.set_u(self.sim.u + float(delta))
        else:
            if rv_u is None: return
            cur_h = self._read_sync(rv_u) or 0.0
            new_h = u_percent_to_human(u_human_to_percent(cur_h) + float(delta))
            self._write_sync(rv_u, new_h)

    def _on_sim_tick(self):
        if not self.sim.running: return
        out = self.sim.step()
        if out is None: return
        t, y, u = out
        self.buff.append(t, y=y, u=u)
        self._auto_axes(); self._redraw()

    # ---------- Drawing helpers ----------
    def _compute_padded_limits(self, vmin: float, vmax: float, min_span: float = 1.0, pad_ratio: float = 0.05):
        if vmax < vmin: vmin, vmax = vmax, vmin
        span = vmax - vmin
        if span < 1e-9:
            span = max(min_span, abs(vmax) if abs(vmax) > 0 else 1.0)
            vmin = vmin - span * 0.5; vmax = vmax + span * 0.5
        pad = max(1e-12, pad_ratio * (vmax - vmin))
        return vmin - pad, vmax + pad

    def _auto_axes(self):
        if len(self.buff.t) < 2: return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        xmin, xmax = self._compute_padded_limits(tmin, tmax, min_span=1.0, pad_ratio=0.05)
        if xmin < 0: xmin = 0.0
        self.canvas.ax_y.set_xlim(xmin, xmax)

        y_min, y_max = min(self.buff.y), max(self.buff.y)
        y_lo, y_hi = self._compute_padded_limits(y_min, y_max, min_span=1.0, pad_ratio=0.05)
        self.canvas.ax_y.set_ylim(y_lo, y_hi)

        u_min, u_max = min(self.buff.u), max(self.buff.u)
        u_lo, u_hi = self._compute_padded_limits(u_min, u_max, min_span=1.0, pad_ratio=0.05)
        self.canvas.ax_u.set_ylim(u_lo, u_hi)

    def _redraw(self):
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        self.canvas.draw_idle()
