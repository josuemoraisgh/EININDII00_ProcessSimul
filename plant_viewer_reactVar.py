#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Viewer (ReactVar) • PySide6
---------------------------------
• Sem timer: só desenha quando chegam sinais das ReactVars.
• Seleção de variáveis via combobox (varre reactFactory.df).
• Entrada (u) por incremento A com botões +A e -A (soma/subtrai ao valor atual).
• Toolbar com botão "Limpar" (zera buffers e reinicia t=0).
• Eixos Y independentes: y à ESQUERDA, u à DIREITA, com autoscale separado.
• Start/Stop/Reset espelháveis com a janela principal via sinais.

Para ajustar a largura ocupada pelas escalas:
  UIConfig.LEFT_MARGIN  → margem esquerda do subplot (0..1)
  UIConfig.RIGHT_MARGIN → margem direita do subplot (0..1)
  UIConfig.LABELPAD / TICK_PAD → afastamentos finos
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, List

import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QComboBox, QGroupBox,
    QPushButton, QSpinBox, QLabel
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# =============================================================================
# Config
# =============================================================================

@dataclass
class UIConfig:
    CONTROL_PANEL_WIDTH: int = 300
    SLIDER_STEPS: int = 10_000
    # ---- Margens do gráfico (ajuste aqui para "apertar" as escalas) ----
    LEFT_MARGIN: float = 0.08   # margem esquerda (0..1)
    RIGHT_MARGIN: float = 0.94  # margem direita (0..1) — deixe < 1 para caber os ticks da direita
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
    """Wrapper pequeno para padronizar leitura/escrita + sinal float."""
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
    def __init__(self, maxlen: int = 100_000):
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
    """Toolbar do Matplotlib com botão extra 'Limpar'."""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        act = self.addAction("🧹 Limpar")
        act.triggered.connect(parent.on_clear_clicked)


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

        # Cursor (linhas-guia no eixo y principal)
        self.hline = self.ax_y.axhline(0, lw=0.8, ls="--", alpha=0.4, visible=False)
        self.vline = self.ax_y.axvline(0, lw=0.8, ls="--", alpha=0.4, visible=False)
        self.mpl_connect("motion_notify_event", self._on_move)
        self.mpl_connect("axes_leave_event", self._on_leave)

        self.lock_vline = None
        self.annot = self.ax_y.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)
        self.mpl_connect("button_press_event", self._on_click)

        self.overlays = []

    # --- Cursor handlers
    def _on_move(self, ev):
        if not ev.inaxes:
            self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle(); return
        self.hline.set_visible(True); self.vline.set_visible(True)
        self.hline.set_ydata([ev.ydata]); self.vline.set_xdata([ev.xdata])
        self.draw_idle()

    def _on_leave(self, _):
        self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle()

    def _on_click(self, ev):
        if not ev.inaxes:
            return
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

    # --- helpers overlays
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
    # Emite intenção de start/stop/reset p/ janela principal (se houver)
    simStartStop = QtCore.Signal(bool)
    simReset = QtCore.Signal()

    def __init__(self, react_factory=None, simul_tf=None):
        super().__init__()
        self.setWindowTitle("Planta (ReactVar) — Viewer")
        self.resize(1200, 700)

        self.factory = react_factory
        self.simul_tf = simul_tf

        self.running = False
        self.t0: Optional[float] = None
        self.buff = DataBuffers(200_000)

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

        # --- Seleção de variáveis (a partir do df) ---
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

        # --- Entrada (u): apenas A, +A e -A ---
        g_u = QGroupBox("Entrada (u)")
        lay_u = QHBoxLayout(g_u)
        self.sb_A = QDoubleSpinBox(); self.sb_A.setDecimals(3); self.sb_A.setRange(0.0, 1e9); self.sb_A.setValue(1.0)
        self.btn_step_pos = QPushButton("+A"); self.btn_step_neg = QPushButton("-A")
        self.btn_step_pos.clicked.connect(lambda: self._inc_u(+self.sb_A.value()))
        self.btn_step_neg.clicked.connect(lambda: self._inc_u(-self.sb_A.value()))
        lay_u.addWidget(QLabel("A:")); lay_u.addWidget(self.sb_A, 1); lay_u.addWidget(self.btn_step_pos); lay_u.addWidget(self.btn_step_neg)

        # --- Simulação (por último) ---
        g_sim = QGroupBox("Simulação")
        lay_sim = QVBoxLayout(g_sim)
        row_port = QHBoxLayout()
        row_port.addWidget(QLabel("MB_PORT:"))
        self.sb_port = QSpinBox(); self.sb_port.setRange(1, 65535); self.sb_port.setValue(502)
        row_port.addWidget(self.sb_port, 1)
        lay_sim.addLayout(row_port)

        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop"); self.btn_reset = QPushButton("reset")
        self.btn_start.setCheckable(True); self.btn_stop.setCheckable(True)

        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_reset.pressed.connect(lambda: self.btn_reset.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.released.connect(lambda: self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;"))
        self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;")
        self.btn_reset.clicked.connect(self.on_reset_clicked)

        lay_sim.addWidget(self.btn_start)
        lay_sim.addWidget(self.btn_stop)
        lay_sim.addWidget(self.btn_reset)

        # Monta colunas
        for w in (g_sel, g_u, g_sim):
            right.addWidget(w)
        right.addStretch(1)

        main.addLayout(left, 1)
        main.addWidget(right_container)

        # Estilo inicial
        self._set_running_visual(False)

    # ----------------------- Factory -> Combos -----------------------
    def _populate_from_factory(self):
        """Carrega os nomes de tabelas/linhas/colunas a partir do self.factory.df"""
        self._df = getattr(self.factory, "df", None)
        if not self._df:
            return
        # Tabelas
        tables = list(self._df.keys())
        self.cb_u_tbl.addItems(tables); self.cb_y_tbl.addItems(tables)

        # Handlers para popular linhas/colunas quando muda a tabela
        self.cb_u_tbl.currentTextChanged.connect(lambda _: self._fill_row_col(self.cb_u_tbl, self.cb_u_row, self.cb_u_col))
        self.cb_y_tbl.currentTextChanged.connect(lambda _: self._fill_row_col(self.cb_y_tbl, self.cb_y_row, self.cb_y_col))

        # Inicializa
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

    # -------------------------- Start/Stop/Reset --------------------------
    def _set_running_visual(self, running: bool):
        self.btn_start.blockSignals(True); self.btn_stop.blockSignals(True)
        self.btn_start.setChecked(running); self.btn_stop.setChecked(not running)
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
        self.buff.clear()
        self.canvas.clear_overlays()
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

    # --- Métodos que o MAIN pode chamar para espelhar o visual aqui
    def sync_running_state(self, running: bool):
        self.running = bool(running)
        self._set_running_visual(self.running)

    def sync_reset(self):
        self.running = False
        self._set_running_visual(False)
        self.buff.clear(); self.canvas.clear_overlays()
        self.canvas.ax_y.set_xlim(0, 10); self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self._redraw()

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
                try: delattr(self, nm)
                except Exception: pass

    def on_connect_clicked(self):
        """Cria ReactVars a partir das seleções dos combos e conecta sinais."""
        if ReactVarClass is None or self._df is None:
            return

        # Desconecta anteriores
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
        if not hasattr(self, "rv_u"):
            return
        cur = self.rv_u.read_sync()
        if cur is None:
            cur = 0.0
        v = float(cur) + float(delta)
        self.rv_u.write(v)  # dispara _on_u_external via sinal

    # -------------------------- Callbacks de sinais --------------------------
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

    # -------------------------- Desenho --------------------------
    def _auto_axes(self):
        if len(self.buff.t) < 2:
            return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        self.canvas.ax_y.set_xlim(tmin, tmax)

        # y
        y_min, y_max = min(self.buff.y), max(self.buff.y)
        if y_min == y_max:
            y_min -= 1; y_max += 1
        y_pad = 0.06 * (y_max - y_min)
        self.canvas.ax_y.set_ylim(y_min - y_pad, y_max + y_pad)

        # u
        u_min, u_max = min(self.buff.u), max(self.buff.u)
        if u_min == u_max:
            u_min -= 1; u_max += 1
        u_pad = 0.06 * (u_max - u_min)
        self.canvas.ax_u.set_ylim(u_min - u_pad, u_max + u_pad)

    def _redraw(self):
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        self.canvas.draw_idle()

    # -------------------------- Toolbar extra --------------------------
    def on_clear_clicked(self):
        self.buff.clear()
        if self.running:
            self.t0 = time.monotonic()  # reinicia t=0 daqui em diante
        self.canvas.clear_overlays()
        self.canvas.ax_y.relim(); self.canvas.ax_y.autoscale_view()
        self.canvas.ax_u.relim(); self.canvas.ax_u.autoscale_view()
        self._redraw()


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
