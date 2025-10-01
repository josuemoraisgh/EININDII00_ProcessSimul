
from typing import List, Optional

class DataBuffers:
    def __init__(self, maxlen: int = 200_000):
        self.maxlen = maxlen
        self.t: List[float] = []
        self.y: List[float] = []
        self.u: List[float] = []

    def clear(self):
        self.t.clear(); self.y.clear(); self.u.clear()

    def append(self, t: float, y: Optional[float], u: Optional[float]):
        if self.t and t < self.t[-1]:  # ignore out of order
            return
        self.t.append(t)
        if len(self.t) > self.maxlen:
            self.t.pop(0)
            if self.y: self.y.pop(0)
            if self.u: self.u.pop(0)
        y_last = self.y[-1] if self.y else 0.0
        u_last = self.u[-1] if self.u else 0.0
        self.y.append(y if y is not None else y_last)
        self.u.append(u if u is not None else u_last)
