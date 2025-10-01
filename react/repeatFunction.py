
# repeatFunction.py — Tk/threading version (compatible with SimulTf usage)
# Expected usage (from SimulTf):
#    RepeatFunction(self._simulation_step, self.stepTime)
# where:
#   - first arg is the function to call repeatedly
#   - second arg is either an integer/float interval in ms OR a callable returning that interval
#
# Thread-safe start/stop. Re-arms itself after each tick.

import threading
from .qt_compat import QObject, Slot

class RepeatFunction(QObject):
    def __init__(self, func, interval_ms_or_callable):
        super().__init__()
        self._func = func
        self._interval_src = interval_ms_or_callable  # int/float in ms OR callable -> ms
        self._timer = None
        self._running = False
        self._lock = threading.Lock()

    def _get_interval_seconds(self) -> float:
        try:
            ms = self._interval_src() if callable(self._interval_src) else self._interval_src
            return float(ms) / 1000.0
        except Exception:
            # fallback para 50ms se houver erro de conversão
            return 0.050

    def _tick(self):
        with self._lock:
            if not self._running:
                return
        try:
            self._func()
        finally:
            with self._lock:
                if self._running:
                    interval_s = self._get_interval_seconds()
                    self._timer = threading.Timer(interval_s, self._tick)
                    self._timer.daemon = True
                    self._timer.start()

    @Slot()
    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            interval_s = self._get_interval_seconds()
            self._timer = threading.Timer(interval_s, self._tick)
            self._timer.daemon = True
            self._timer.start()

    @Slot()
    def stop(self):
        with self._lock:
            self._running = False
            t = self._timer
            self._timer = None
        if t:
            try:
                t.cancel()
            except Exception:
                pass

    def setInterval(self, interval_ms_or_callable):
        # permite trocar a fonte do intervalo em tempo de execução
        with self._lock:
            self._interval_src = interval_ms_or_callable
