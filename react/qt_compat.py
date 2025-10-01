# qt_compat.py — Minimal compatibility layer replacing small parts of PySide6.QtCore
# Provides: QObject, Signal, Slot
# - Signal has an anti-reentrancy guard to avoid recursive emits (common pitfall when porting from Qt).

from typing import Callable, List, Any
import threading

__all__ = ["QObject", "Signal", "Slot"]

class QObject:
    def __init__(self, *args, **kwargs):
        super().__init__()

class Signal:
    def __init__(self, *types):
        self._subs: List[Callable[..., Any]] = []
        self._lock = threading.RLock()
        self._emitting_local = threading.local()  # per-thread reentrancy flag

    def connect(self, func: Callable[..., Any]):
        with self._lock:
            if func not in self._subs:
                self._subs.append(func)

    def disconnect(self, func: Callable[..., Any]):
        with self._lock:
            try:
                self._subs.remove(func)
            except ValueError:
                pass

    def emit(self, *args, **kwargs):
        # prevent re-entrant emit on the same thread to avoid recursion loops
        if getattr(self._emitting_local, "emitting", False):
            return
        setattr(self._emitting_local, "emitting", True)
        try:
            with self._lock:
                subs = list(self._subs)
            for f in subs:
                try:
                    f(*args, **kwargs)
                except Exception:
                    # swallow handler exceptions to mimic Qt's behavior in many apps
                    pass
        finally:
            setattr(self._emitting_local, "emitting", False)

def Slot(*types, **kw):
    # Decorator no-op to keep signatures compatible
    def deco(fn):
        return fn
    return deco
