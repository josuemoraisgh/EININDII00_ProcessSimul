from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# =============================================================================
# Config
# =============================================================================

@dataclass
class UIConfig:
    CONTROL_PANEL_WIDTH: int = 340
    LEFT_MARGIN: float = 0.08   # margem esquerda (0..1)
    RIGHT_MARGIN: float = 0.94  # margem direita (0..1)
    LABELPAD: int = 3           # distância label-eixo
    TICK_PAD: int = 2           # distância ticks-eixo


# =============================================================================
# ReactVar adapter (sincroniza sinais/leituras)
# =============================================================================

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


class ReactVarAdapter(QtCore.QObject):
    """Adaptador mínimo para usar ReactVar com sinais Qt (float)."""
    changed = QtCore.Signal(float)

    def __init__(self, rv_obj):
        super().__init__()
        self._rv = rv_obj
        self._rv.valueChangedSignal.connect(self._on_raw)

    @Slot(object)
    def _on_raw(self, payload):
        """Extrai _value como float e emite 'changed'."""
        try:
            v = float(getattr(payload, "_value"))
            self.changed.emit(v)
        except Exception:
            pass

    def write(self, v: float):
        """Escreve valor no ReactVar (em float)."""
        try:
            self._rv.setValue(float(v), isWidgetValueChanged=True)
        except Exception:
            pass

    def read_sync(self) -> Optional[float]:
        """Leitura síncrona do valor atual (float), se disponível."""
        try:
            return float(self._rv._value)
        except Exception:
            return None


# =============================================================================
# Utilidades: buffers
# =============================================================================

class DataBuffers:
    """Buffers simples para t, y e u com descarte do início quando excede maxlen."""
    def __init__(self, maxlen: int = 200_000):
        self.maxlen = maxlen
        self.t: List[float] = []
        self.y: List[float] = []
        self.u: List[float] = []

    def clear(self):
        self.t.clear()
        self.y.clear()
        self.u.clear()

    def append(self, t: float, y: Optional[float], u: Optional[float]):
        # ignora tempos fora de ordem
        if self.t and t < self.t[-1]:
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


# =============================================================================
# Mpl Canvas + Toolbar
# =============================================================================

class PVToolbar(NavigationToolbar):
    """Toolbar do Matplotlib com botões extras funcionais."""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)

        # Ordem: V | H | Kp | Limpar | Reset
        self.addSeparator()
        self.act_v = self.addAction("📏 V")
        self.act_h = self.addAction("📐 H")
        self.act_kp = self.addAction("🧭 Kp")
        self.act_clear = self.addAction("❌ Limpar Cursores")
        self.act_reset = self.addAction("🧹 Limpar Tela")

        # Checkables
        self.act_v.setCheckable(True)
        self.act_h.setCheckable(True)
        self.act_kp.setCheckable(True)

        # Conexões
        self.act_v.triggered.connect(lambda checked: parent.set_cursor_mode('v' if checked else None))
        self.act_h.triggered.connect(lambda checked: parent.set_cursor_mode('h' if checked else None))
        self.act_kp.triggered.connect(lambda checked: parent.set_kp_mode(checked))
        self.act_clear.triggered.connect(parent.on_clear_cursors_clicked)
        self.act_reset.triggered.connect(parent.on_reset_toolbar)


class MplCanvas(FigureCanvas):
    """
    Canvas do Matplotlib com:
      • Eixos duplos (y à esquerda, u à direita)
      • Cursores V/H, Kp e overlays
    Desenho sempre agendado de forma segura (evita QPainter inválido).
    """
    def __init__(self, parent=None):
        fig = Figure(figsize=(7, 4), constrained_layout=False)
        fig.subplots_adjust(
            left=UIConfig.LEFT_MARGIN, right=UIConfig.RIGHT_MARGIN, bottom=0.12, top=0.95
        )
        self.fig = fig
        self.ax_y = fig.add_subplot(111)       # eixo principal (y) à ESQUERDA
        super().__init__(fig)
        self.setParent(parent)

        # Segundo eixo (u) como twin — mantém na DIREITA (padrão)
        self.ax_u = self.ax_y.twinx()

        # Estética & pads
        self.ax_y.tick_params(axis='y', pad=UIConfig.TICK_PAD, labelsize=9, colors='C0')
        self.ax_u.tick_params(axis='y', pad=UIConfig.TICK_PAD, labelsize=9, colors='C1')
        self.ax_y.tick_params(axis='x', labelsize=9)
        self.ax_y.set_ylabel("PV (y)", labelpad=UIConfig.LABELPAD, color='C0')
        self.ax_u.set_ylabel("Entrada (u)", labelpad=UIConfig.LABELPAD, color='C1')
        self.ax_y.set_xlabel("Tempo (s)")
        self.ax_y.grid(True, alpha=0.25)

        (self.line_y,) = self.ax_y.plot([], [], color='C0', label="PV (y)")
        (self.line_u,) = self.ax_u.plot([], [], color='C1', label="Entrada (u)")

        # Legenda combinada
        lines = [self.line_y, self.line_u]
        labels = [ln.get_label() for ln in lines]
        self.ax_y.legend(lines, labels, loc="upper right")

        # Cursor leve (cruz)
        self.hline = self.ax_y.axhline(0, lw=0.8, ls="--", alpha=0.4, visible=False)
        self.vline = self.ax_y.axvline(0, lw=0.8, ls="--", alpha=0.4, visible=False)

        # Eventos do mouse/teclado
        self.mpl_connect("motion_notify_event", self._on_move)
        self.mpl_connect("axes_leave_event", self._on_leave)
        self.mpl_connect("button_press_event", self._on_click)
        self.mpl_connect("button_release_event", self._on_release)
        self.mpl_connect("key_press_event", self._on_key)

        # Marcador fixo legado
        self.lock_vline = None
        self.annot = self.ax_y.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)

        # Cursores V/H
        self.cursor_mode: Optional[str] = None      # None | 'v' | 'h'
        self.cursor_points: List[Tuple[float, float]] = []  # cliques
        self.cursor_artists: List = []
        self.cursor_text_box_v = self.ax_y.text(
            0.01, 0.98, "", transform=self.ax_y.transAxes, va='top', ha='left',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False, zorder=5
        )
        self.cursor_text_box_h = self.ax_y.text(
            0.01, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='left',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False, zorder=5
        )

        # Kp (hipotenusa)
        self.kp_mode: bool = False
        self.kp_points: List[Tuple[float, float]] = []   # (x,y) em eixo y
        self.kp_line = None
        self.kp_text_box = self.ax_y.text(
            0.99, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='right',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False
        )
        self.kp_edit_idx: Optional[int] = None
        self.kp_creating: bool = False
        self.kp_backup_points: Optional[List[Tuple[float,float]]] = None

        # Overlays auxiliares
        self.overlays = []

    # ---------- desenho seguro ----------
    def _can_draw(self) -> bool:
        """Canvas pronto para desenhar? Evita QPainter em estados inválidos."""
        try:
            return self.isVisible() and self.width() > 0 and self.height() > 0
        except Exception:
            return False

    def _do_draw_idle(self):
        try:
            FigureCanvas.draw_idle(self)
        except Exception:
            pass

    def request_draw(self):
        """Agendamento de desenho assíncrono, somente quando seguro."""
        if not self._can_draw():
            return
        QtCore.QTimer.singleShot(0, self._do_draw_idle)

    # ---------- utilitários de mapeamento ----------
    def _to_ax_y_ydata(self, ev):
        """y (em dados do eixo esquerdo) a partir do evento, esteja o mouse sobre ax_y ou ax_u."""
        try:
            if ev.ydata is not None and ev.inaxes is self.ax_y:
                return float(ev.ydata)
            if ev.ydata is not None and ev.inaxes is self.ax_u:
                _, py = self.ax_u.transData.transform((0.0, float(ev.ydata)))
                return float(self.ax_y.transData.inverted().transform((0.0, py))[1])
            return float(self.ax_y.transData.inverted().transform((ev.x, ev.y))[1])
        except Exception:
            return None

    def _u_to_ydata(self, x: float, uval: float) -> float:
        """Mapear valor do eixo direito (u) no tempo x para a coordenada em y (eixo esquerdo) mantendo a altura em pixels."""
        xp, yp = self.ax_u.transData.transform((float(x), float(uval)))
        return float(self.ax_y.transData.inverted().transform((xp, yp))[1])

    # ---------- handlers do mouse/teclado ----------
    def _on_move(self, ev):
        if not ev.inaxes or ev.inaxes not in (self.ax_y, self.ax_u):
            self.hline.set_visible(False); self.vline.set_visible(False); self.request_draw(); return

        # Cursor leve
        self.hline.set_visible(True); self.vline.set_visible(True)
        y_left = self._to_ax_y_ydata(ev)
        if y_left is not None:
            self.hline.set_ydata([y_left])
        if ev.xdata is not None:
            self.vline.set_xdata([ev.xdata])
        else:
            self.vline.set_visible(False)

        self.request_draw()

    def _on_leave(self, _):
        self.hline.set_visible(False); self.vline.set_visible(False); self.request_draw()

    def _on_click(self, ev):
        if not ev.inaxes or ev.inaxes not in (self.ax_y, self.ax_u):
            return

        if self.cursor_mode in ('v', 'h'):
            self._handle_cursor_click(ev)
            return

        # Legado: travar vline
        if ev.button == 1 and ev.xdata is not None:
            x = ev.xdata
            if self.lock_vline is None:
                self.lock_vline = self.ax_y.axvline(x, lw=1.1, ls="-.", alpha=0.7)
            else:
                self.lock_vline.set_xdata([x])
            self.annot.xy = (x, self.ax_y.get_ybound()[1])
            self.annot.set_visible(True)
            self.request_draw()
        elif ev.button == 3:
            if self.lock_vline is not None:
                try:
                    self.lock_vline.remove()
                except Exception:
                    pass
                self.lock_vline = None
            self.annot.set_visible(False)
            self.request_draw()

    def _on_release(self, ev):
        pass

    def _on_key(self, ev):
        pass

    # -------------------- Cursores V/H --------------------
    def set_cursor_mode(self, mode: Optional[str]):
        self.cursor_mode = mode
        self.cursor_points.clear()
        self.request_draw()

    def clear_cursors(self):
        for a in self.cursor_artists:
            try:
                a.remove()
            except Exception:
                pass
        self.cursor_artists.clear()
        self.cursor_points.clear()
        self.cursor_text_box_v.set_visible(False)
        self.cursor_text_box_h.set_visible(False)
        self.request_draw()

    def _handle_cursor_click(self, ev):
        if ev.xdata is None:
            return
        x = float(ev.xdata)
        if self.cursor_mode == 'h':
            y_left = self._to_ax_y_ydata(ev)
            if y_left is None:
                return
            self.cursor_points.append((x, float(y_left)))
            ln = self.ax_y.axhline(y_left, lw=1.2, ls="--", alpha=0.8, color='k')
            self.cursor_artists.append(ln)
        elif self.cursor_mode == 'v':
            self.cursor_points.append((x, float(ev.ydata if ev.ydata is not None else 0.0)))
            ln = self.ax_y.axvline(x, lw=1.2, ls="--", alpha=0.8, color='k')
            self.cursor_artists.append(ln)
        self.request_draw()

        if len(self.cursor_points) >= 2:
            p1, p2 = self.cursor_points[-2], self.cursor_points[-1]
            if self.cursor_mode == 'v':
                self._calc_vertical_cursors(p1, p2)
            elif self.cursor_mode == 'h':
                self._calc_horizontal_cursors(p1, p2)

    @staticmethod
    def _interp_at(xq: float, x: np.ndarray, y: np.ndarray) -> float:
        if len(x) < 2 or not np.isfinite(xq):
            return float('nan')
        x = np.asarray(x); y = np.asarray(y)
        return float(np.interp(xq, x, y))

    def _calc_vertical_cursors(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        x1, _ = p1; x2, _ = p2
        if x2 < x1:
            x1, x2 = x2, x1
        dt = x2 - x1
        l1 = self.ax_y.axvline(x1, lw=1.4, ls="-.", alpha=0.9, color='k')
        l2 = self.ax_y.axvline(x2, lw=1.4, ls="-.", alpha=0.9, color='k')
        self.cursor_artists += [l1, l2]
        txt = f"V: x1={x1:.4g}s  x2={x2:.4g}s  Δt={dt:.4g}s"
        self.cursor_text_box_v.set_text(txt)
        self.cursor_text_box_v.set_visible(True)
        self.request_draw()

    def _calc_horizontal_cursors(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        x1, y1 = p1; x2, y2 = p2
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        u1 = self._interp_at(x1, tx, uu)
        u2 = self._interp_at(x2, tx, uu)
        dy = abs(y2 - y1)
        du = abs(u2 - u1)
        lh1 = self.ax_y.axhline(y1, lw=1.4, ls="-.", alpha=0.9, color='k')
        lh2 = self.ax_y.axhline(y2, lw=1.4, ls="-.", alpha=0.9, color='k')
        self.cursor_artists += [lh1, lh2]
        txt = f"H: y1={y1:.4g}  y2={y2:.4g}  |Δy|={dy:.4g}   |Δu|={du:.4g}"
        self.cursor_text_box_h.set_text(txt)
        self.cursor_text_box_h.set_visible(True)
        self.request_draw()

    # ---- helpers overlays ----
    def clear_overlays(self):
        for a in self.overlays:
            try:
                a.remove()
            except Exception:
                pass
        self.overlays.clear()
        self.request_draw()

    def add_vline(self, x, **kw):
        a = self.ax_y.axvline(x, **kw); self.overlays.append(a); self.request_draw(); return a

    def add_hline(self, y, **kw):
        a = self.ax_y.axhline(y, **kw); self.overlays.append(a); self.request_draw(); return a

    def add_text(self, x, y, s, **kw):
        a = self.ax_y.text(x, y, s, **kw); self.overlays.append(a); self.request_draw(); return a