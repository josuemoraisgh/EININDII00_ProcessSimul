
from typing import Optional
from react.qt_compat import Slot
from react.qt_compat import QObject, Signal, Slot

# Try to import ReactVar from different locations (keeps backward compat)
ReactVarClass = None
try:
    from react.react_var import ReactVar as _RV
    ReactVarClass = _RV
except Exception:
    try:
        from react_var import ReactVar as _RV
        ReactVarClass = _RV
    except Exception:
        ReactVarClass = None

class ReactVarAdapter(QObject):
    changed = Signal(float)

    def __init__(self, rv_obj):
        super().__init__()
        self._rv = rv_obj
        sig = getattr(self._rv, "valueChangedSignal", None)
        if sig is not None:
            try: sig.connect(self._on_raw)
            except Exception: pass

    @Slot(object)
    def _on_raw(self, payload):
        try:
            v = float(getattr(payload, "_value"))
            self.changed.emit(v)
        except Exception:
            pass

    def write(self, v: float):
        try:
            self._rv.setValue(float(v), isWidgetValueChanged=True)
        except Exception:
            pass

    def read_sync(self) -> Optional[float]:
        try:
            return float(self._rv._value)
        except Exception:
            return None
