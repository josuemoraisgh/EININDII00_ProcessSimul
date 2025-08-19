#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Viewer (ReactVar) • PySide6
---------------------------------
• Modo Real: desenha quando chegam sinais das ReactVars.
• Entrada (u) por incremento A com botões +A e -A (funciona em Real e Simulado).
• Toolbar: 📏 V | 📐 H | 🧭 Kp | ❌ Limpar | 🧹 Reset
  - V: duas barras verticais → Δt.
  - H: duas barras horizontais → |Δy| e |Δu|.
  - Kp (hipotenusa):
      • Ao ativar (se não existir): P1 é colocado automaticamente no início da variação de y;
        P2 é onde a tangente em P1 “toca” (encosta) a curva u(t) (mapeada para o eixo esquerdo).
      • Existindo: clique perto de um endpoint (≤12 px) para “pegar”; mova o mouse (linha pontilhada);
        clique novamente para “soltar” (linha sólida). Clique longe dos endpoints → ignora.
      • ESC ou botão direito: cancela a edição/colocação e volta ao estado anterior.
      • Caixa mostra Δt, |Δy|, |Δu| e atualiza em tempo real.
  - Limpar: remove apenas cursores/Kp (não mexe nos dados).
  - Reset: zera buffers, t=0, desativa cursores/Kp.
• Eixos Y independentes: y (esquerda) e u (direita).
• Ajuste (Real × Simulado): aba Simulado roda FOPDT (Kp, τ, L) com tempo de integração ajustável.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, List, Tuple
from collections import deque

import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QComboBox, QGroupBox,
    QPushButton, QSpinBox, QLabel, QTabWidget
)

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
    changed = QtCore.Signal(float)

    def __init__(self, rv_obj):
        super().__init__()
        self._rv = rv_obj
        self._rv.valueChangedSignal.connect(self._on_raw)

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


# =============================================================================
# Utilidades: buffers
# =============================================================================

class DataBuffers:
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
    """Toolbar do Matplotlib com botões extras."""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)

        # Ordem: V | H | Kp | Limpar | Reset
        self.addSeparator()
        self.act_v = self.addAction("📏 V")
        self.act_h = self.addAction("📐 H")
        self.act_kp = self.addAction("🧭 Kp")
        self.act_clear = self.addAction("❌ Limpar")
        self.act_reset = self.addAction("🧹 Reset")

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
        self.cursor_text_box = self.ax_y.text(
            0.01, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='left',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False
        )

        # Kp (hipotenusa)
        self.kp_mode: bool = False
        self.kp_points: List[Tuple[float, float]] = []   # (x,y) em eixo y
        self.kp_line = None
        self.kp_text_box = self.ax_y.text(
            0.99, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='right',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False
        )
        # Estados de edição/colocação
        self.kp_edit_idx: Optional[int] = None       # 0/1 durante edição; None caso contrário
        self.kp_creating: bool = False               # True após 1º clique quando não existe Kp
        self.kp_backup_points: Optional[List[Tuple[float,float]]] = None

        self.overlays = []

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
            self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle(); return

        # Cursor leve
        self.hline.set_visible(True); self.vline.set_visible(True)
        y_left = self._to_ax_y_ydata(ev)
        if y_left is not None:
            self.hline.set_ydata([y_left])
        self.vline.set_xdata([ev.xdata])

        # Kp: mover sem segurar (edição ou colocação)
        if self.kp_mode and ev.xdata is not None:
            if self.kp_edit_idx is not None and len(self.kp_points) == 2:
                # Editando endpoint existente
                self._kp_update_point(self.kp_edit_idx, ev.xdata, live=True, ev_pixels=(ev.x, ev.y))
                if self.kp_line is not None:
                    self.kp_line.set_linestyle('--')
            elif self.kp_creating and len(self.kp_points) >= 1:
                # Colocando P2 provisório
                xq = float(ev.xdata)
                tx = np.asarray(self.line_y.get_xdata(), dtype=float)
                yy = np.asarray(self.line_y.get_ydata(), dtype=float)
                y_guess = self._interp_at(xq, tx, yy)
                if np.isfinite(y_guess):
                    x_final, y_final = self._kp_snap_point(xq, y_guess, ev_pixels=(ev.x, ev.y))
                    if len(self.kp_points) == 1:
                        self.kp_points = [self.kp_points[0], (x_final, y_final)]
                    else:
                        self.kp_points[1] = (x_final, y_final)
                    self._kp_draw_line(linestyle='--')
                    self._kp_update_text()

        self.draw_idle()

    def _on_leave(self, _):
        self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle()

    def _on_click(self, ev):
        if not ev.inaxes or ev.inaxes not in (self.ax_y, self.ax_u):
            return

        if self.kp_mode:
            if ev.button == 3:
                self._kp_cancel_operation()
                return
            self._kp_click_flow(ev)
            return

        if self.cursor_mode in ('v', 'h'):
            self._handle_cursor_click(ev)
            return

        # Legado: travar vline
        if ev.button == 1:
            x = ev.xdata
            if self.lock_vline is None:
                self.lock_vline = self.ax_y.axvline(x, lw=1.1, ls="-.", alpha=0.7)
            else:
                self.lock_vline.set_xdata([x])
            self.annot.xy = (x, self.ax_y.get_ybound()[1])
            self.annot.set_visible(True)
            self.draw_idle()
        elif ev.button == 3:
            if self.lock_vline is not None:
                self.lock_vline.remove(); self.lock_vline = None
            self.annot.set_visible(False)
            self.draw_idle()

    def _on_release(self, ev):
        pass

    def _on_key(self, ev):
        if self.kp_mode and ev.key == 'escape':
            self._kp_cancel_operation()

    # -------------------- Cursores V/H --------------------
    def set_cursor_mode(self, mode: Optional[str]):
        self.cursor_mode = mode
        self.cursor_points.clear()
        self.draw_idle()

    def clear_cursors(self):
        for a in self.cursor_artists:
            try:
                a.remove()
            except Exception:
                pass
        self.cursor_artists.clear()
        self.cursor_points.clear()
        self.cursor_text_box.set_visible(False)
        self.kp_clear()
        self.draw_idle()

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
        self.draw_idle()

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
        self.cursor_text_box.set_text(txt)
        self.cursor_text_box.set_visible(True)
        self.draw_idle()

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
        self.cursor_text_box.set_text(txt)
        self.cursor_text_box.set_visible(True)
        self.draw_idle()

    # -------------------- Kp (hipotenusa) --------------------
    def set_kp_mode(self, enabled: bool):
        self.kp_mode = bool(enabled)
        if enabled:
            self.kp_edit_idx = None
            self.kp_creating = False
            self.kp_backup_points = None
            # Auto-colocação se não existir Kp ainda
            if not self.kp_points and self.kp_line is None:
                try:
                    self._kp_auto_place()
                except Exception:
                    pass
        self.draw_idle()

    def kp_clear(self):
        self.kp_points.clear()
        if self.kp_line is not None:
            try: self.kp_line.remove()
            except Exception: pass
            self.kp_line = None
        self.kp_text_box.set_visible(False)
        self.kp_edit_idx = None
        self.kp_creating = False
        self.kp_backup_points = None

    def _kp_click_flow(self, ev):
        xq = float(ev.xdata)
        # Caso 1: já existe Kp completo → tentar pegar endpoint próximo
        if len(self.kp_points) == 2 and self.kp_line is not None and not self.kp_creating and self.kp_edit_idx is None:
            idx = self._kp_pick_endpoint_by_click(ev, radius_px=12.0)
            if idx is None:
                return
            self.kp_edit_idx = idx
            self.kp_backup_points = list(self.kp_points)
            if self.kp_line is not None:
                self.kp_line.set_linestyle('--')
            return

        # Caso 2: estamos editando → segundo clique fixa
        if self.kp_edit_idx is not None:
            if self.kp_line is not None:
                self.kp_line.set_linestyle('-')
            self.kp_edit_idx = None
            self.kp_backup_points = None
            self._kp_update_text()
            self.draw_idle()
            return

        # Caso 3: não existe Kp ainda → iniciar colocação P1 manual (fallback, se auto-place não ocorreu)
        if len(self.kp_points) < 2 and self.kp_line is None and not self.kp_creating:
            tx = np.asarray(self.line_y.get_xdata(), dtype=float)
            yy = np.asarray(self.line_y.get_ydata(), dtype=float)
            y_guess = self._interp_at(xq, tx, yy)
            if not np.isfinite(y_guess):
                return
            x1, y1 = self._kp_snap_point(xq, y_guess, ev_pixels=(ev.x, ev.y))
            self.kp_points = [(x1, y1)]
            self.kp_creating = True
            (self.kp_line,) = self.ax_y.plot([x1, x1], [y1, y1], linestyle='--', color='k', lw=1.5, label='Kp')
            self.draw_idle()
            return

        # Caso 4: estamos criando e já temos P1 → segundo clique fixa P2
        if self.kp_creating and len(self.kp_points) == 2:
            if self.kp_line is not None:
                self.kp_line.set_linestyle('-')
            self.kp_creating = False
            self._kp_update_text()
            self.draw_idle()
            return

    def _kp_pick_endpoint_by_click(self, ev, radius_px: float) -> Optional[int]:
        if len(self.kp_points) != 2:
            return None
        x0, y0 = self.kp_points[0]
        x1, y1 = self.kp_points[1]
        p0 = self.ax_y.transData.transform((x0, y0))
        p1 = self.ax_y.transData.transform((x1, y1))
        click = np.array([ev.x, ev.y], dtype=float)
        d0 = np.linalg.norm(click - p0)
        d1 = np.linalg.norm(click - p1)
        if d0 <= radius_px or d1 <= radius_px:
            return 0 if d0 <= d1 else 1
        return None

    def _kp_cancel_operation(self):
        if self.kp_edit_idx is not None and self.kp_backup_points is not None:
            self.kp_points = list(self.kp_backup_points)
            self.kp_backup_points = None
            self.kp_edit_idx = None
            if self.kp_line is not None:
                (x0, y0), (x1, y1) = self.kp_points
                self.kp_line.set_data([x0, x1], [y0, y1])
                self.kp_line.set_linestyle('-')
            self._kp_update_text()
            self.draw_idle()
            return

        if self.kp_creating:
            self.kp_creating = False
            self.kp_points.clear()
            if self.kp_line is not None:
                try: self.kp_line.remove()
                except Exception: pass
                self.kp_line = None
            self.kp_text_box.set_visible(False)
            self.draw_idle()

    def _kp_update_point(self, idx: int, xnew: float, live: bool = True, ev_pixels=None):
        if len(self.kp_points) < 1:
            return
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        if len(tx) < 2:
            return
        y_guess = self._interp_at(float(xnew), tx, yy)
        if not np.isfinite(y_guess):
            return
        x_final, y_final = self._kp_snap_point(float(xnew), float(y_guess), ev_pixels=ev_pixels)

        if len(self.kp_points) == 1:
            self.kp_points = [self.kp_points[0], (x_final, y_final)]
        else:
            pts = list(self.kp_points)
            pts[idx] = (x_final, y_final)
            self.kp_points = pts

        ls = '--' if live else '-'
        self._kp_draw_line(linestyle=ls)
        self._kp_update_text()

    def _kp_draw_line(self, linestyle='-'):
        if len(self.kp_points) < 1:
            return
        if self.kp_line is None:
            if len(self.kp_points) == 1:
                (x0, y0) = self.kp_points[0]
                (self.kp_line,) = self.ax_y.plot([x0, x0], [y0, y0], linestyle=linestyle, color='k', lw=1.5, label='Kp')
            else:
                (x0, y0), (x1, y1) = self.kp_points[:2]
                (self.kp_line,) = self.ax_y.plot([x0, x1], [y0, y1], linestyle=linestyle, color='k', lw=1.5, label='Kp')
        else:
            if len(self.kp_points) == 1:
                (x0, y0) = self.kp_points[0]
                self.kp_line.set_data([x0, x0], [y0, y0])
            else:
                (x0, y0), (x1, y1) = self.kp_points[:2]
                self.kp_line.set_data([x0, x1], [y0, y1])
            self.kp_line.set_linestyle(linestyle)
            self.kp_line.set_color('k')
            self.kp_line.set_linewidth(1.5)
        self.draw_idle()

    def _kp_update_text(self):
        if len(self.kp_points) != 2:
            self.kp_text_box.set_visible(False)
            return
        (x0, y0), (x1, y1) = self.kp_points[:2]
        dt = abs(x1 - x0)
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        u0 = self._interp_at(x0, tx, uu)
        u1 = self._interp_at(x1, tx, uu)
        dy = abs(y1 - y0)
        du = abs(u1 - u0)
        txt = f"Kp  Δt={dt:.4g}s  |Δy|={dy:.4g}  |Δu|={du:.4g}"
        self.kp_text_box.set_text(txt)
        self.kp_text_box.set_visible(True)
        self.draw_idle()

    def _kp_snap_point(self, xq: float, y_guess: float, ev_pixels=None, radius_px: float = 12.0, win_frac: float = 0.05):
        if ev_pixels is None:
            px_ref, py_ref = self.ax_y.transData.transform((xq, y_guess))
        else:
            px_ref, py_ref = float(ev_pixels[0]), float(ev_pixels[1])

        xmin, xmax = self.ax_y.get_xbound()
        dx = max(1e-12, xmax - xmin)
        xwin = max(1e-9, win_frac * dx)

        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        if len(tx) < 2:
            return float(xq), float(y_guess)

        m = np.abs(tx - xq) <= xwin
        idxs = np.where(m)[0]
        if idxs.size == 0:
            return float(xq), float(y_guess)

        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        pts_y = np.column_stack([tx[idxs], yy[idxs]])
        pix_y = self.ax_y.transData.transform(pts_y)
        dists_y = np.hypot(pix_y[:,0] - px_ref, pix_y[:,1] - py_ref)
        best_y_dist = float(np.min(dists_y)) if dists_y.size else float('inf')
        best_y_idx = int(idxs[int(np.argmin(dists_y))]) if dists_y.size else None

        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        pts_u = np.column_stack([tx[idxs], uu[idxs]])
        pix_u = self.ax_u.transData.transform(pts_u)
        dists_u = np.hypot(pix_u[:,0] - px_ref, pix_u[:,1] - py_ref)
        best_u_dist = float(np.min(dists_u)) if dists_u.size else float('inf')
        best_u_idx = int(idxs[int(np.argmin(dists_u))]) if dists_u.size else None

        best_dist = min(best_y_dist, best_u_dist)
        if not np.isfinite(best_dist) or best_dist > radius_px:
            return float(xq), float(y_guess)

        if best_y_dist <= best_u_dist:
            x_fin = float(tx[best_y_idx]); y_fin = float(yy[best_y_idx])
            return x_fin, y_fin
        else:
            x_fin = float(tx[best_u_idx]); u_val = float(uu[best_u_idx])
            _, py = self.ax_u.transData.transform((x_fin, u_val))
            y_fin = float(self.ax_y.transData.inverted().transform((x_fin, py))[1])
            return x_fin, y_fin

    # ---------- Auto-colocação inicial do Kp ao ativar (reta tangente) ----------
    def _kp_auto_place(self):
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        uu_r = np.asarray(self.line_u.get_ydata(), dtype=float)
        if tx.size < 8 or yy.size != tx.size or uu_r.size != tx.size:
            return

        # 1) Derivada e detecção robusta do início
        try:
            dydt = np.gradient(yy, tx)
        except Exception:
            return
        absd = np.abs(dydt)
        max_s = float(np.max(absd)) if absd.size else 0.0
        if not np.isfinite(max_s) or max_s <= 0.0:
            return
        thr = 0.10 * max_s

        sel = absd >= thr
        if not np.any(sel):
            return
        sign_mean = np.sign(np.mean(dydt[sel]))
        sign_mean = 1.0 if sign_mean >= 0 else -1.0

        m_consec = 3
        i0 = None
        for k in range(0, tx.size - m_consec):
            window = dydt[k:k+m_consec]
            if np.all(np.abs(window) >= thr*0.8) and np.all(np.sign(window) == sign_mean):
                i0 = k
                break
        if i0 is None:
            cand = np.where(sel)[0]
            if cand.size == 0:
                return
            i0 = int(cand[0])

        # 2) Regressão linear local para slope e tangência
        n_total = tx.size
        n_win = max(5, min(50, int(0.03 * n_total)))
        j1 = i0
        j2 = min(n_total, i0 + n_win)
        if j2 - j1 < 3:
            j2 = min(n_total, i0 + 3)
        try:
            coeff = np.polyfit(tx[j1:j2], yy[j1:j2], 1)  # y ≈ s*x + b
            s = float(coeff[0])
            x0 = float(tx[i0]); y0 = float(yy[i0])
            b = y0 - s * x0  # reancora a reta em P1
        except Exception:
            x0 = float(tx[i0]); y0 = float(yy[i0])
            s = float(dydt[i0])
            b = y0 - s * x0

        # 3) P2: onde a reta tangente mais se aproxima de u(t) mapeado para o eixo y
        best_j = None
        best_px = None
        for j in range(i0, tx.size):
            xj = float(tx[j])
            y_line = s * xj + b
            y_u = self._u_to_ydata(xj, float(uu_r[j]))
            py_line = self.ax_y.transData.transform((xj, y_line))[1]
            py_u    = self.ax_y.transData.transform((xj, y_u))[1]
            dist_px = abs(py_line - py_u)
            if (best_px is None) or (dist_px < best_px):
                best_px = dist_px
                best_j = j

        if best_j is None:
            return

        x2 = float(tx[best_j])
        y2 = float(s * x2 + b)

        self.kp_points = [(x0, y0), (x2, y2)]
        if self.kp_line is None:
            (self.kp_line,) = self.ax_y.plot([x0, x2], [y0, y2], linestyle='-', color='k', lw=1.5, label='Kp')
        else:
            self.kp_line.set_data([x0, x2], [y0, y2])
            self.kp_line.set_linestyle('-')
            self.kp_line.set_color('k')
            self.kp_line.set_linewidth(1.5)
        self._kp_update_text()
        self.draw_idle()

    # ---- helpers overlays ----
    def clear_overlays(self):
        for a in self.overlays:
            try:
                a.remove()
            except Exception:
                pass
        self.overlays.clear()
        self.draw_idle()

    def add_vline(self, x, **kw):
        a = self.ax_y.axvline(x, **kw); self.overlays.append(a); return a

    def add_hline(self, y, **kw):
        a = self.ax_y.axhline(y, **kw); self.overlays.append(a); return a

    def add_text(self, x, y, s, **kw):
        a = self.ax_y.text(x, y, s, **kw); self.overlays.append(a); return a


# =============================================================================
# Janela
# =============================================================================

class PlantViewerWindow(QMainWindow):
    simStartStop = QtCore.Signal(bool)
    simReset = QtCore.Signal()

    def __init__(self, react_factory=None, simul_tf=None):
        super().__init__()
        self.setWindowTitle("Planta (ReactVar) — Viewer")
        self.resize(1200, 700)

        self.factory = react_factory
        self.simul_tf = simul_tf

        # Real
        self.running = False
        self.t0: Optional[float] = None
        self.buff = DataBuffers(200_000)

        # Simulador FOPDT
        self.sim_running = False
        self.sim_Kp = 1.0
        self.sim_tau = 1.0
        self.sim_L = 0.0
        self.sim_dt = 0.05  # s
        self.sim_t = 0.0
        self.sim_y = 0.0
        self.sim_u = 0.0
        self.sim_delay_buf = deque([0.0], maxlen=1)
        self.sim_timer = QtCore.QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_tick)

        self._build_ui()
        self._populate_from_factory()

    # -------------------------- UI --------------------------
    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Plot
        left = QVBoxLayout()
        self.canvas = MplCanvas(self)
        self.toolbar = PVToolbar(self.canvas, self)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, 1)

        # Painel lateral
        right_container = QWidget(self); right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # Seleção de variáveis
        g_sel = QGroupBox("Seleção de Variáveis (ReactFactory.df)")
        lay = QFormLayout(g_sel)

        self.cb_u_tbl = QComboBox(); self.cb_u_row = QComboBox(); self.cb_u_col = QComboBox()
        self.cb_y_tbl = QComboBox(); self.cb_y_row = QComboBox(); self.cb_y_col = QComboBox()

        lay.addRow("Entrada (u) — Tabela:", self.cb_u_tbl)
        lay.addRow("Entrada (u) — Dispositivo/Linha:", self.cb_u_row)
        lay.addRow("Entrada (u) — Variável/Coluna:", self.cb_u_col)
        lay.addRow("Saída (y) — Tabela:", self.cb_y_tbl)
        lay.addRow("Saída (y) — Dispositivo/Linha:", self.cb_y_row)
        lay.addRow("Saída (y) — Variável/Coluna:", self.cb_y_col)

        self.btn_connect = QPushButton("Ativar seleção (u  &  y)")
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        lay.addRow(self.btn_connect)

        # Ajuste (Real × Simulado)
        g_adj = QGroupBox("Ajuste")
        adj_lay = QVBoxLayout(g_adj)
        self.tabs_adj = QTabWidget()

        # Aba Real
        self.tab_real = QWidget(); real_lay = QVBoxLayout(self.tab_real)
        row_port = QHBoxLayout()
        row_port.addWidget(QLabel("MB_PORT:"))
        self.sb_port = QSpinBox(); self.sb_port.setRange(1, 65535); self.sb_port.setValue(502)
        row_port.addWidget(self.sb_port, 1)
        real_lay.addLayout(row_port)

        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop"); self.btn_reset = QPushButton("reset")
        self.btn_start.setCheckable(True); self.btn_stop.setCheckable(True)

        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_reset.pressed.connect(lambda: self.btn_reset.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.released.connect(lambda: self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;"))
        self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;")
        self.btn_reset.clicked.connect(self.on_reset_clicked)

        real_lay.addWidget(self.btn_start)
        real_lay.addWidget(self.btn_stop)
        real_lay.addWidget(self.btn_reset)

        # Aba Simulado
        self.tab_sim = QWidget(); sim_lay = QFormLayout(self.tab_sim)
        self.sb_sim_Kp = QDoubleSpinBox(); self.sb_sim_Kp.setDecimals(4); self.sb_sim_Kp.setRange(-1e6, 1e6); self.sb_sim_Kp.setValue(1.0)
        self.sb_sim_tau = QDoubleSpinBox(); self.sb_sim_tau.setDecimals(4); self.sb_sim_tau.setRange(1e-6, 1e6); self.sb_sim_tau.setValue(1.0)
        self.sb_sim_L   = QDoubleSpinBox(); self.sb_sim_L.setDecimals(4); self.sb_sim_L.setRange(0.0, 1e6); self.sb_sim_L.setValue(0.0)
        self.sb_sim_dt  = QSpinBox(); self.sb_sim_dt.setRange(1, 2000); self.sb_sim_dt.setValue(50)  # ms
        self.btn_sim_start = QPushButton("Start (Sim)")
        self.btn_sim_stop  = QPushButton("Stop (Sim)")
        self.btn_sim_start.clicked.connect(self.on_sim_start_clicked)
        self.btn_sim_stop.clicked.connect(self.on_sim_stop_clicked)

        sim_lay.addRow("Kp:", self.sb_sim_Kp)
        sim_lay.addRow("τ (tau):", self.sb_sim_tau)
        sim_lay.addRow("Atraso (L) [s]:", self.sb_sim_L)
        sim_lay.addRow("Tempo de integração [ms]:", self.sb_sim_dt)
        sim_lay.addRow(self.btn_sim_start)
        sim_lay.addRow(self.btn_sim_stop)

        self.tabs_adj.addTab(self.tab_real, "Real")
        self.tabs_adj.addTab(self.tab_sim, "Simulado")
        adj_lay.addWidget(self.tabs_adj)

        # Entrada (u): A, +A, -A (último bloco)
        g_u = QGroupBox("Entrada (u)")
        lay_u = QHBoxLayout(g_u)
        self.sb_A = QDoubleSpinBox(); self.sb_A.setDecimals(3); self.sb_A.setRange(-1e9, 1e9); self.sb_A.setValue(1.0)
        self.btn_step_pos = QPushButton("+A"); self.btn_step_neg = QPushButton("-A")
        self.btn_step_pos.clicked.connect(lambda: self._inc_u(+self.sb_A.value()))
        self.btn_step_neg.clicked.connect(lambda: self._inc_u(-self.sb_A.value()))
        lay_u.addWidget(QLabel("A:")); lay_u.addWidget(self.sb_A, 1); lay_u.addWidget(self.btn_step_pos); lay_u.addWidget(self.btn_step_neg)

        # Monta colunas
        for w in (g_sel, g_adj, g_u):
            right.addWidget(w)
        right.addStretch(1)

        main.addLayout(left, 1)
        main.addWidget(right_container)

        # Estilo inicial
        self._set_running_visual(False)

    # ----------------------- Exclusividade dos modos -----------------------
    def set_cursor_mode(self, mode: Optional[str]):
        if mode == 'v':
            self.toolbar.act_h.blockSignals(True); self.toolbar.act_h.setChecked(False); self.toolbar.act_h.blockSignals(False)
            self.set_kp_mode(False)
        elif mode == 'h':
            self.toolbar.act_v.blockSignals(True); self.toolbar.act_v.setChecked(False); self.toolbar.act_v.blockSignals(False)
            self.set_kp_mode(False)
        else:
            self.toolbar.act_v.blockSignals(True); self.toolbar.act_h.blockSignals(True)
            self.toolbar.act_v.setChecked(False); self.toolbar.act_h.setChecked(False)
            self.toolbar.act_v.blockSignals(False); self.toolbar.act_h.blockSignals(False)
        self.canvas.set_cursor_mode(mode)

    def set_kp_mode(self, enabled: bool):
        if enabled:
            self.toolbar.act_v.blockSignals(True); self.toolbar.act_h.blockSignals(True)
            self.toolbar.act_v.setChecked(False); self.toolbar.act_h.setChecked(False)
            self.toolbar.act_v.blockSignals(False); self.toolbar.act_h.blockSignals(False)
        self.toolbar.act_kp.blockSignals(True); self.toolbar.act_kp.setChecked(enabled); self.toolbar.act_kp.blockSignals(False)
        self.canvas.set_kp_mode(enabled)

    # ----------------------- Toolbar: Limpar / Reset -----------------------
    def on_clear_cursors_clicked(self):
        self.canvas.clear_cursors()

    def on_reset_toolbar(self):
        self.on_stop_clicked()
        self.on_sim_stop_clicked()

        self.buff.clear()
        self.canvas.clear_overlays()
        self.canvas.clear_cursors()
        self.canvas.ax_y.set_xlim(0, 10); self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self._redraw()

        self.toolbar.act_v.setChecked(False)
        self.toolbar.act_h.setChecked(False)
        self.toolbar.act_kp.setChecked(False)

        self.t0 = time.monotonic()
        self.sim_t = 0.0

    # ----------------------- Factory -> Combos -----------------------
    def _populate_from_factory(self):
        self._df = getattr(self.factory, "df", None)
        if not self._df:
            return
        tables = list(self._df.keys())
        self.cb_u_tbl.addItems(tables); self.cb_y_tbl.addItems(tables)
        self.cb_u_tbl.currentTextChanged.connect(lambda _: self._fill_row_col(self.cb_u_tbl, self.cb_u_row, self.cb_u_col))
        self.cb_y_tbl.currentTextChanged.connect(lambda _: self._fill_row_col(self.cb_y_tbl, self.cb_y_row, self.cb_y_col))
        if tables:
            self._fill_row_col(self.cb_u_tbl, self.cb_u_row, self.cb_u_col)
            self._fill_row_col(self.cb_y_tbl, self.cb_y_row, self.cb_y_col)

    def _fill_row_col(self, cb_tbl: QComboBox, cb_row: QComboBox, cb_col: QComboBox):
        tbl = cb_tbl.currentText()
        cb_row.blockSignals(True); cb_col.blockSignals(True)
        cb_row.clear(); cb_col.clear()
        try:
            df = self._df.get(tbl)
            cb_row.addItems([str(x) for x in df.index])
            cb_col.addItems([str(c) for c in df.columns])
        except Exception:
            pass
        cb_row.blockSignals(False); cb_col.blockSignals(False)

    # -------------------------- Start/Stop/Reset (Real) --------------------------
    def _set_running_visual(self, running: bool):
        self.btn_start.blockSignals(True); self.btn_stop.blockSignals(True)
        self.btn_start.setChecked(running)
        self.btn_stop.setChecked(not running)
        if running:
            self.btn_start.setStyleSheet("background:#2ecc71; color:white; font-weight:bold;")
            self.btn_stop.setStyleSheet("")
        else:
            self.btn_start.setStyleSheet("")
            self.btn_stop.setStyleSheet("background:#ff2d2d; color:white; font-weight:bold;")
        self.btn_start.blockSignals(False); self.btn_stop.blockSignals(False)

    def on_start_clicked(self):
        if self.running:
            return
        if not hasattr(self, "rv_u") or not hasattr(self, "rv_y"):
            self.on_connect_clicked()
            if not (hasattr(self, "rv_u") and hasattr(self, "rv_y")):
                return
        self.running = True
        self.t0 = time.monotonic()
        self._set_running_visual(True)
        self.simStartStop.emit(True)

    def on_stop_clicked(self):
        self.running = False
        self._set_running_visual(False)
        self.simStartStop.emit(False)

    def on_reset_clicked(self):
        self.on_stop_clicked()
        self.buff.clear(); self.canvas.clear_overlays()
        self.canvas.ax_y.set_xlim(0, 10); self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self._redraw()
        self.simReset.emit()

    # -------------------------- Conectar ReactVars --------------------------
    def _disconnect_current(self):
        for attr in ("rv_u", "rv_y"):
            if hasattr(self, attr):
                rv = getattr(self, attr)
                try:
                    rv.changed.disconnect()
                except Exception:
                    pass
        for nm in ("rv_u", "rv_y"):
            if hasattr(self, nm):
                try:
                    delattr(self, nm)
                except Exception:
                    pass

    def on_connect_clicked(self):
        if ReactVarClass is None or self._df is None:
            return
        self._disconnect_current()
        try:
            t_u = self.cb_u_tbl.currentText()
            r_u = self.cb_u_row.currentText()
            c_u = self.cb_u_col.currentText()
            t_y = self.cb_y_tbl.currentText()
            r_y = self.cb_y_row.currentText()
            c_y = self.cb_y_col.currentText()

            rv_u_obj = self._df[t_u].at[r_u, c_u]
            rv_y_obj = self._df[t_y].at[r_y, c_y]

            self.rv_u = ReactVarAdapter(rv_u_obj)
            self.rv_y = ReactVarAdapter(rv_y_obj)

            self.rv_u.changed.connect(self._on_u_external)
            self.rv_y.changed.connect(self._on_y_external)
        except Exception as e:
            print("[PV] ERRO CONNECT:", e)
            return

    # -------------------------- Entrada u (A, +A, -A) --------------------------
    def _inc_u(self, delta: float):
        if self.tabs_adj.currentWidget() is self.tab_sim:
            self.sim_u = float(self.sim_u) + float(delta)
        else:
            if not hasattr(self, "rv_u"):
                return
            cur = self.rv_u.read_sync()
            if cur is None:
                cur = 0.0
            v = float(cur) + float(delta)
            self.rv_u.write(v)

    # -------------------------- Callbacks (Real) --------------------------
    @Slot(float)
    def _on_u_external(self, value: float):
        if not self.running or self.t0 is None:
            return
        t = time.monotonic() - self.t0
        self.buff.append(t, y=None, u=float(value))
        self._auto_axes(); self._redraw()

    @Slot(float)
    def _on_y_external(self, value: float):
        if not self.running or self.t0 is None:
            return
        t = time.monotonic() - self.t0
        self.buff.append(t, y=float(value), u=None)
        self._auto_axes(); self._redraw()

    # -------------------------- Simulador FOPDT --------------------------
    def _init_sim_delay_buf(self):
        N = max(1, int(round(self.sim_L / self.sim_dt)))
        self.sim_delay_buf = deque([self.sim_u]*N, maxlen=N)

    def on_sim_start_clicked(self):
        self.sim_Kp = float(self.sb_sim_Kp.value())
        self.sim_tau = float(self.sb_sim_tau.value())
        self.sim_L   = float(self.sb_sim_L.value())
        self.sim_dt  = float(self.sb_sim_dt.value()) / 1000.0  # ms → s

        self._init_sim_delay_buf()
        self.sim_running = True
        self.sim_t = 0.0
        self.sim_y = self.buff.y[-1] if self.buff.y else 0.0
        self.t0 = time.monotonic()
        self.buff.clear()
        self.canvas.ax_y.set_xlim(0, 10)
        self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self.sim_timer.start(int(max(1, self.sb_sim_dt.value())))  # ms

    def on_sim_stop_clicked(self):
        self.sim_running = False
        self.sim_timer.stop()

    def _on_sim_tick(self):
        if not self.sim_running:
            return
        dt = self.sim_dt
        if len(self.sim_delay_buf) == 0:
            u_delay = self.sim_u
        else:
            u_delay = self.sim_delay_buf[0]
            self.sim_delay_buf.append(self.sim_u)
            self.sim_delay_buf.popleft()

        if self.sim_tau > 0:
            dydt = (-self.sim_y + self.sim_Kp * u_delay) / self.sim_tau
        else:
            dydt = 0.0
        self.sim_y += dydt * dt
        self.sim_t += dt

        self.buff.append(self.sim_t, y=self.sim_y, u=self.sim_u)
        self._auto_axes(); self._redraw()

    # -------------------------- Desenho --------------------------
    def _auto_axes(self):
        if len(self.buff.t) < 2:
            return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        self.canvas.ax_y.set_xlim(tmin, tmax)

        y_min, y_max = min(self.buff.y), max(self.buff.y)
        if y_min == y_max:
            y_min -= 1; y_max += 1
        y_pad = 0.06 * (y_max - y_min)
        self.canvas.ax_y.set_ylim(y_min - y_pad, y_max + y_pad)

        u_min, u_max = min(self.buff.u), max(self.buff.u)
        if u_min == u_max:
            u_min -= 1; u_max += 1
        u_pad = 0.06 * (u_max - u_min)
        self.canvas.ax_u.set_ylim(u_min - u_pad, u_max + u_pad)

    def _redraw(self):
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        self.canvas.draw_idle()

    # ----------------------- Compatibilidade (espelhamento) -----------------------
    def sync_running_state(self, running: bool):
        self.running = bool(running)
        self._set_running_visual(self.running)

    def sync_reset(self):
        self.on_reset_toolbar()


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
