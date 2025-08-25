
from typing import Any, Optional, Tuple, List
from .react_adapter import ReactVarAdapter
from .utils import u_human_to_percent, u_percent_to_human

class PlantModel:
    """Responsável por acessar ReactVars, storage e mapas df (MODEL)."""
    def __init__(self, factory=None):
        self.factory = factory
        self._last_u_percent: Optional[float] = None
        self._last_y: Optional[float] = None

    # -------- persistência --------
    def restore_selection(self, cb_u, cb_y):
        try:
            st = getattr(self.factory, "storage", None)
            if st is None: return
            u_saved = st.getRawData("PV_CFG", "SELECTION", "u_row") or ""
            y_saved = st.getRawData("PV_CFG", "SELECTION", "y_col") or ""
            if u_saved:
                i = cb_u.findText(str(u_saved))
                if i >= 0: cb_u.setCurrentIndex(i)
            if y_saved:
                j = cb_y.findText(str(y_saved))
                if j >= 0: cb_y.setCurrentIndex(j)
        except Exception:
            pass

    def persist_selection(self, u_name: str, y_name: str):
        try:
            st = getattr(self.factory, "storage", None)
            if st is not None:
                st.setRawData("PV_CFG", "SELECTION", "u_row", u_name)
                st.setRawData("PV_CFG", "SELECTION", "y_col", y_name)
        except Exception:
            pass

    # -------- df maps / lookup --------
    def _get_df_maps(self):
        try:
            df = getattr(self.factory, "df", None)
            if isinstance(df, dict):
                mod = None; hart = None
                for k, v in df.items():
                    ku = str(k).upper()
                    if ("MODBUS" in ku) and (mod is None): mod = v
                    if ("HART" in ku) and (hart is None): hart = v
                return mod, hart
        except Exception:
            pass
        return None, None

    def list_candidates(self) -> Tuple[List[str], List[str]]:
        u_items: List[str] = []; y_items: List[str] = []
        mod, hart = self._get_df_maps()
        try:
            if mod is not None:
                rows = [str(r) for r in list(mod.index)]
                u_items = [r for r in rows if r.upper().startswith("W_")] or rows
        except Exception:
            pass
        try:
            if hart is not None:
                cols = [str(c) for c in list(hart.columns)]
                y_items = [c for c in cols if c.upper() not in ("BYTE_SIZE", "TYPE")]
        except Exception:
            pass
        if not (u_items or y_items):
            names: List[str] = []
            for attr in ("reactVars", "_vars", "vars"):
                try:
                    d = getattr(self.factory, attr)
                    if isinstance(d, dict):
                        names = list(d.keys()); break
                except Exception:
                    pass
            if names:
                u_items = sorted([n for n in names if n.upper().startswith("W_")]) or names
                y_items = sorted([n for n in names if not n.upper().startswith("W_")]) or names
        if not u_items: u_items = ["W_AUX"]
        if not y_items: y_items = ["FV100CA"]
        return (sorted(u_items), sorted(y_items))

    def get_rv_from_df(self, u_name: str, y_name: str):
        rv_u = rv_y = None
        mod, hart = self._get_df_maps()
        try:
            if mod is not None:
                col = "CLP100"
                if col not in getattr(mod, "columns", []):
                    clps = [c for c in getattr(mod, "columns", []) if "CLP" in str(c).upper()]
                    col = clps[0] if clps else (list(mod.columns)[0] if getattr(mod, "columns", []) else None)
                if col is not None:
                    rv_u = mod.at[u_name, col]
        except Exception:
            rv_u = None
        try:
            if hart is not None:
                row_key = "PROCESS_VARIABLE"
                if row_key not in getattr(hart, "index", []):
                    for r in getattr(hart, "index", []):
                        if str(r).upper() in ("PV", "PROCESS_VARIABLE"):
                            row_key = r; break
                rv_y = hart.at[row_key, y_name]
        except Exception:
            rv_y = None
        return rv_u, rv_y

    def _get_react_var(self, name: str):
        fac = self.factory
        if fac is None or not name: return None
        for attr in ("get_react_var", "reactVar", "var", "getVar"):
            f = getattr(fac, attr, None)
            if callable(f):
                try:
                    rv = f(name)
                    if rv is not None: return rv
                except Exception:
                    pass
        for attr in ("reactVars", "_vars", "vars"):
            try:
                d = getattr(fac, attr)
                if isinstance(d, dict) and name in d: return d[name]
            except Exception:
                pass
        return None

    def connect_vars(self, u_name: str, y_name: str):
        rv_u_df, rv_y_df = self.get_rv_from_df(u_name, y_name)
        rv_u = ReactVarAdapter(rv_u_df) if rv_u_df is not None else self._get_react_var(u_name)
        rv_y = ReactVarAdapter(rv_y_df) if rv_y_df is not None else self._get_react_var(y_name)
        return rv_u, rv_y

    # last values cache (used by controller)
    def cache_external_u(self, val_human: float):
        self._last_u_percent = u_human_to_percent(val_human)

    def cache_external_y(self, val: float):
        self._last_y = float(val)

    def get_cached(self):
        return self._last_u_percent, self._last_y

    def set_cached(self, u_percent: float, y: float):
        self._last_u_percent, self._last_y = float(u_percent), float(y)

    def human_to_percent(self, h: float) -> float:
        return u_human_to_percent(h)

    def percent_to_human(self, p: float) -> float:
        return u_percent_to_human(p)
