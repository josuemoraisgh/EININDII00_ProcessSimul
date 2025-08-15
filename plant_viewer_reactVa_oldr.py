#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Viewer (ReactVar) • PySide6
---------------------------------
• Atualiza gráfico APENAS quando chegam sinais (sem timer).
• Cursor com linha vertical travável (esq = fixa, dir = limpa) e tooltip.
• Zoom/pan pelo NavigationToolbar do Matplotlib.
• Entrada (u): somente A, +A e -A (soma/subtrai A ao valor atual de u).
• Seleção de u e y via combobox a partir de reactFactory.df.
• Identificação FOPDT (1ª ordem com atraso) com marcações no gráfico.
• Sincronia visual Start/Stop/Reset com a janela principal.
• **NOVO**: botão na toolbar do gráfico para **Limpar** e reiniciar t=0.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple, List, Any

import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QComboBox, QGroupBox,
    QPushButton, QSpinBox, QLabel, QStyle
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# =============================================================================
# Config
# =============================================================================

@dataclass
class UIConfig:
    CONTROL_PANEL_WIDTH: int = 320   # largura fixa do painel (px)


# =============================================================================
# Utilidades: buffers e identificação FOPDT
# =============================================================================

class DataBuffers:
    def __init__(self, maxlen: int = 20_000):
        self.maxlen = maxlen
        self.t: List[float] = []
        self.y: List[float] = []
        self.u: List[float] = []

    def clear(self):
        self.t.clear()
        self.y.clear()
        self.u.clear()

    def append(self, t: float, y: Optional[float], u: Optional[float]):
        """Append mantendo último valor quando um dos canais vier None."""
        if self.t and t < self.t[-1]:
            return
        self.t.append(t)
        if len(self.t) > self.maxlen:
            self.t.pop(0)
            if self.y:
                self.y.pop(0)
            if self.u:
                self.u.pop(0)

        y_last = self.y[-1] if self.y else 0.0
        u_last = self.u[-1] if self.u else 0.0
        self.y.append(float(y) if y is not None else y_last)
        self.u.append(float(u) if u is not None else u_last)


@dataclass
class FOPDTParams:
    K: float
    L: float
    tau: float
    t_step: float
    t_delay: float
    t_settle: float
    y0: float
    y_inf: float


class FOPDTIdentifier:
    @staticmethod
    def detect_last_step(t: np.ndarray, u: np.ndarray) -> Optional[Tuple[float, float, float]]:
        if t.size < 3:
            return None
        du = np.diff(u)
        thr = max(1e-6, 0.01 * (np.max(np.abs(u)) + 1e-9))
        idx = np.where(np.abs(du) >= thr)[0]
        if idx.size == 0:
            return None
        i = int(idx[-1])
        return float(t[i + 1]), float(u[i]), float(u[i + 1])

    @staticmethod
    def fit_from_step(t: np.ndarray, y: np.ndarray, u: np.ndarray) -> Optional[FOPDTParams]:
        step = FOPDTIdentifier.detect_last_step(t, u)
        if step is None:
            return None
        t_step, u_before, u_after = step
        du = u_after - u_before
        if abs(du) < 1e-12:
            return None

        pre_mask = (t >= (t_step - 1.0)) & (t < t_step)
        if not np.any(pre_mask):
            pre_mask = (t < t_step)
        y0 = float(np.mean(y[pre_mask])) if np.any(pre_mask) else float(y[0])

        tail = max(1, int(0.1 * y.size))
        y_inf = float(np.mean(y[-tail:]))

        dy = y_inf - y0
        if abs(dy) < 1e-12:
            return None
        sign = 1.0 if dy >= 0 else -1.0

        def cross(frac: float) -> Optional[float]:
            target = y0 + sign * abs(dy) * frac
            idx = np.where((t >= t_step) & (sign * (y - target) >= 0))[0]
            return float(t[idx[0]]) if idx.size > 0 else None

        t28 = cross(0.283)
        t63 = cross(0.632)
        if t28 is None or t63 is None:
            return None

        tau = (t63 - t28) / (1.0 - 1.0 / 3.0)  # (t63 - t28)/(2/3)
        L = t28 - (1.0 / 3.0) * tau
        K = (y_inf - y0) / du
        t_delay = t_step + L
        t_settle = t_delay + 4.0 * tau
        return FOPDTParams(K=K, L=L, tau=tau, t_step=t_step, t_delay=t_delay, t_settle=t_settle, y0=y0, y_inf=y_inf)


# =============================================================================
# Canvas Matplotlib
# =============================================================================

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(7, 4), tight_layout=True)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True)

        (self.line_y,) = self.ax.plot([], [], label="PV (y)")
        (self.line_u,) = self.ax.plot([], [], label="Entrada (u)")
        self.ax.legend(loc="upper right")

        self.hline = self.ax.axhline(0, lw=0.8, ls="--", alpha=0.5, visible=False)
        self.vline = self.ax.axvline(0, lw=0.8, ls="--", alpha=0.5, visible=False)
        self.mpl_connect("motion_notify_event", self._on_move)
        self.mpl_connect("axes_leave_event", self._on_leave)

        self.lock_vline = None
        self.annot = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)
        self.mpl_connect("button_press_event", self._on_click)

        self.overlays = []

    def _on_move(self, ev):
        if not ev.inaxes:
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.draw_idle()
            return
        self.hline.set_visible(True)
        self.vline.set_visible(True)
        self.hline.set_ydata([ev.ydata])
        self.vline.set_xdata([ev.xdata])
        self.draw_idle()

    def _on_leave(self, _):
        self.hline.set_visible(False)
        self.vline.set_visible(False)
        self.draw_idle()

    def _on_click(self, ev):
        if not ev.inaxes:
            return
        if ev.button == 1:
            x = ev.xdata
            if self.lock_vline is None:
                self.lock_vline = self.ax.axvline(x, lw=1.2, ls="-.", alpha=0.7)
            else:
                self.lock_vline.set_xdata([x])
            self.annot.xy = (x, self.ax.get_ybound()[1])
            self.annot.set_visible(True)
            self.draw_idle()
        elif ev.button == 3:
            if self.lock_vline is not None:
                self.lock_vline.remove()
                self.lock_vline = None
            self.annot.set_visible(False)
            self.draw_idle()

    def clear_overlays(self):
        for a in self.overlays:
            try:
                a.remove()
            except Exception:
                pass
        self.overlays.clear()
        self.draw_idle()

    def add_vline(self, x, **kw):
        a = self.ax.axvline(x, **kw)
        self.overlays.append(a)
        return a

    def add_hline(self, y, **kw):
        a = self.ax.axhline(y, **kw)
        self.overlays.append(a)
        return a

    def add_text(self, x, y, s, **kw):
        a = self.ax.text(x, y, s, **kw)
        self.overlays.append(a)
        return a


# ---- Toolbar personalizada: adiciona ação "Limpar" ---------------------------------

class PVToolbar(NavigationToolbar):
    clearRequested = QtCore.Signal()

    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        # separador visual
        self.addSeparator()
        # botão limpar
        act = QAction(parent.style().standardIcon(QStyle.SP_DialogResetButton), "Limpar", self)
        act.setToolTip("Limpar a tela e reiniciar tempo (t=0)")
        act.triggered.connect(self._emit_clear)
        self.addAction(act)

    def _emit_clear(self):
        self.clearRequested.emit()


# =============================================================================
# ReactVar adapter (usa a instância JÁ existente em reactFactory.df)
# =============================================================================

class ReactVarAdapter(QtCore.QObject):
    """Pequeno adaptador para padronizar leitura/escrita e emitir 'changed'."""
    changed = QtCore.Signal(object)  # emitimos o payload cru

    def __init__(self, rv_obj: Any):
        super().__init__()
        self._rv = rv_obj
        # Conecta diretamente no sinal da ReactVar real
        try:
            self._rv.valueChangedSignal.connect(self._on_raw)
        except Exception as e:
            print("[PV] ERRO conectando valueChangedSignal:", e)

    @Slot(object)
    def _on_raw(self, payload):
        self.changed.emit(payload)

    def write(self, v: float):
        """Escreve na variável reativa (sem clamp)."""
        try:
            self._rv.setValue(float(v), isWidgetValueChanged=True)
        except TypeError:
            # fallback para assinatura antiga
            self._rv.setValue(float(v))

    def current_value(self) -> Optional[float]:
        """Lê valor atual de forma síncrona (usa atributo interno)."""
        try:
            return float(getattr(self._rv, "_value"))
        except Exception:
            return None


def _extract_numeric(v: Any) -> Optional[float]:
    """Extrai número do payload da ReactVar ou de tipos simples."""
    try:
        if isinstance(v, (int, float)):
            return float(v)
        if hasattr(v, "_value"):
            return float(getattr(v, "_value"))
        if hasattr(v, "value"):
            return float(getattr(v, "value"))
    except Exception:
        pass
    return None


# =============================================================================
# Janela PlantViewer
# =============================================================================

class PlantViewerWindow(QMainWindow):
    # Emite intenção de start/stop/reset para o MAIN executar a lógica
    simStartStop = QtCore.Signal(bool)  # True=start, False=stop
    simReset = QtCore.Signal()

    def __init__(self, react_factory=None, simul_tf=None):
        super().__init__()
        self.setWindowTitle("Planta (ReactVar) — Viewer & FOPDT Fit")
        self.resize(1200, 700)

        self.factory = react_factory
        self.simul_tf = simul_tf

        self.running = False
        self.t0: Optional[float] = None
        self.buff = DataBuffers(maxlen=20_000)
        self._last_u: Optional[float] = None  # último u recebido (para +A/-A)

        self._build_ui()

        # estilo inicial (parado)
        self._set_viewer_running_visual(False)

    # ------------------------- UI -------------------------
    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Gráfico
        left = QVBoxLayout()
        self.canvas = MplCanvas(self)
        self.toolbar = PVToolbar(self.canvas, self)
        self.toolbar.clearRequested.connect(self._toolbar_clear)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, stretch=1)

        # Painel (largura fixa)
        right_container = QWidget(self)
        right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # Seleção de variáveis a partir do DF
        g_sel = QGroupBox("Seleção de Variáveis (ReactFactory.df)")
        lay_sel = QFormLayout(g_sel)

        self.cb_u_tbl = QComboBox(); self.cb_u_row = QComboBox(); self.cb_u_col = QComboBox()
        self.cb_y_tbl = QComboBox(); self.cb_y_row = QComboBox(); self.cb_y_col = QComboBox()

        lay_sel.addRow(QLabel("Entrada (u) — Tabela:"), self.cb_u_tbl)
        lay_sel.addRow(QLabel("Entrada (u) — Dispositivo/Linha:"), self.cb_u_row)
        lay_sel.addRow(QLabel("Entrada (u) — Variável/Coluna:"), self.cb_u_col)

        lay_sel.addRow(QLabel("Saída (y) — Tabela:"), self.cb_y_tbl)
        lay_sel.addRow(QLabel("Saída (y) — Dispositivo/Linha:"), self.cb_y_row)
        lay_sel.addRow(QLabel("Saída (y) — Variável/Coluna:"), self.cb_y_col)

        # indicadores simples
        self.lbl_u_ok = QLabel("–")
        self.lbl_y_ok = QLabel("–")
        lay_sel.addRow("u selecionado ✔ ?", self.lbl_u_ok)
        lay_sel.addRow("y selecionado ✔ ?", self.lbl_y_ok)

        self.btn_connect = QPushButton("Ativar seleção (u  y)")
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        lay_sel.addRow(self.btn_connect)

        # Entrada (u) — SOMENTE A, +A, -A
        g_u = QGroupBox("Entrada (u)")
        lay_u = QHBoxLayout(g_u)
        self.sb_A = QDoubleSpinBox()
        self.sb_A.setDecimals(3)
        self.sb_A.setRange(0.0, 1e9)
        self.sb_A.setValue(1.0)
        self.btn_step_pos = QPushButton("+A")
        self.btn_step_neg = QPushButton("-A")
        self.btn_step_pos.clicked.connect(lambda: self._apply_u_delta(+self.sb_A.value()))
        self.btn_step_neg.clicked.connect(lambda: self._apply_u_delta(-self.sb_A.value()))
        lay_u.addWidget(QLabel("A:"))
        lay_u.addWidget(self.sb_A, 1)
        lay_u.addWidget(self.btn_step_pos)
        lay_u.addWidget(self.btn_step_neg)

        # Identificação
        g_id = QGroupBox("Identificação FOPDT")
        lay_id = QHBoxLayout(g_id)
        self.btn_fit = QPushButton("Processar")
        self.btn_clear = QPushButton("Limpar")
        self.btn_fit.clicked.connect(self.on_fit)
        self.btn_clear.clicked.connect(self.on_clear)
        lay_id.addWidget(self.btn_fit)
        lay_id.addWidget(self.btn_clear)

        # Simulação (por último)
        g_sim = QGroupBox("Simulação")
        lay_sim = QVBoxLayout(g_sim)
        row_port = QHBoxLayout()
        row_port.addWidget(QLabel("MB_PORT:"))
        self.sb_port = QSpinBox(); self.sb_port.setRange(1, 65535); self.sb_port.setValue(502)
        row_port.addWidget(self.sb_port, 1)
        lay_sim.addLayout(row_port)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("reset")

        # estados checkable + estilos
        self.btn_start.setCheckable(True)
        self.btn_stop.setCheckable(True)

        # estilos dos botões
        self.btn_reset.setStyleSheet("""
            QPushButton { background: #ffe600; font-weight: bold; }
            QPushButton:pressed { background: #2e86de; color: white; }
        """)

        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_reset.clicked.connect(self.on_reset)

        lay_sim.addWidget(self.btn_start)
        lay_sim.addWidget(self.btn_stop)
        lay_sim.addWidget(self.btn_reset)

        # ordem
        for w in (g_sel, g_u, g_id, g_sim):
            right.addWidget(w)
        right.addStretch(1)

        main.addLayout(left, stretch=1)
        main.addWidget(right_container)

        # preenche comboboxes com base no DF
        self._populate_df_combos()

        # cursor -> atualizar tooltip quando travado
        self.canvas.mpl_connect("button_press_event", self._update_cursor_annotation)

    # ------------------------- DF helpers -------------------------
    def _populate_df_combos(self):
        self._df = getattr(self.factory, "df", None)
        if self._df is None or not isinstance(self._df, dict) or len(self._df) == 0:
            self.cb_u_tbl.clear(); self.cb_y_tbl.clear()
            return

        tables = list(self._df.keys())
        self.cb_u_tbl.clear(); self.cb_y_tbl.clear()
        self.cb_u_tbl.addItems(tables); self.cb_y_tbl.addItems(tables)

        # callbacks: quando muda tabela, recarrega linhas/colunas
        self.cb_u_tbl.currentTextChanged.connect(lambda _: self._reload_rc(for_u=True))
        self.cb_y_tbl.currentTextChanged.connect(lambda _: self._reload_rc(for_u=False))

        # carrega inicial
        self._reload_rc(True)
        self._reload_rc(False)

    def _reload_rc(self, for_u: bool):
        cb_tbl = self.cb_u_tbl if for_u else self.cb_y_tbl
        cb_row = self.cb_u_row if for_u else self.cb_y_row
        cb_col = self.cb_u_col if for_u else self.cb_y_col

        cb_row.clear(); cb_col.clear()
        tbl = cb_tbl.currentText()
        try:
            df = self._df[tbl]
            # rows e cols como strings
            cb_row.addItems([str(r) for r in df.index])
            cb_col.addItems([str(c) for c in df.columns])
        except Exception:
            pass

    def _check_cell_is_reactvar(self, table: str, row: str, col: str) -> bool:
        try:
            var = self._df[table].at[row, col]
            ok = hasattr(var, "valueChangedSignal")
            print("[PV] CHECK CELL", (table, row, col), "->", ok, "type:", type(var))
            return ok
        except Exception as e:
            print("[PV] CHECK CELL FAILED:", e)
            return False

    # ------------------------- Conexão -------------------------
    def _on_connect_clicked(self):
        """Cria adapters para u e y, conectando sinais."""
        tbl_u, row_u, col_u = self.cb_u_tbl.currentText(), self.cb_u_row.currentText(), self.cb_u_col.currentText()
        tbl_y, row_y, col_y = self.cb_y_tbl.currentText(), self.cb_y_row.currentText(), self.cb_y_col.currentText()

        u_ok = self._check_cell_is_reactvar(tbl_u, row_u, col_u)
        y_ok = self._check_cell_is_reactvar(tbl_y, row_y, col_y)
        self.lbl_u_ok.setText("✔ Válido" if u_ok else "✖ inválido")
        self.lbl_y_ok.setText("✔ Válido" if y_ok else "✖ inválido")
        if not (u_ok and y_ok):
            return

        # desconecta anteriores (se existirem)
        try:
            if hasattr(self, "rv_u"):
                self.rv_u.changed.disconnect(self._on_u_external_any)
        except Exception:
            pass
        try:
            if hasattr(self, "rv_y"):
                self.rv_y.changed.disconnect(self._on_y_external)
        except Exception:
            pass

        # cria adaptadores a partir da MESMA instância existente no DF
        var_u = self._df[tbl_u].at[row_u, col_u]
        var_y = self._df[tbl_y].at[row_y, col_y]

        self.rv_u = ReactVarAdapter(var_u)
        self.rv_y = ReactVarAdapter(var_y)

        self.rv_u.changed.connect(self._on_u_external_any)
        self.rv_y.changed.connect(self._on_y_external)

        print(f"[PV] CONNECT u=( {tbl_u} {row_u} {col_u} ) y=( {tbl_y} {row_y} {col_y} )")

    # ------------------------- Execução (VISUAL + sinais p/ MAIN) -------------------------
    def _set_viewer_running_visual(self, running: bool):
        """Atualiza apenas o VISUAL dos botões Start/Stop (sem emitir sinais)."""
        self.btn_start.blockSignals(True)
        self.btn_stop.blockSignals(True)
        self.btn_start.setChecked(running)
        self.btn_stop.setChecked(not running)
        if running:
            self.btn_start.setStyleSheet("background:#2ecc71; color:white; font-weight:bold;")
            self.btn_stop.setStyleSheet("")
        else:
            self.btn_start.setStyleSheet("")
            self.btn_stop.setStyleSheet("background:#ff2d2d; color:white; font-weight:bold;")
        self.btn_start.blockSignals(False)
        self.btn_stop.blockSignals(False)
        print("[PV] SYNC RUN", running)

    def on_start(self):
        if self.running:
            return
        if not hasattr(self, "rv_u") or not hasattr(self, "rv_y"):
            QMessageBox.information(self, "Seleção", "Selecione u e y e clique em 'Ativar seleção'.")
            return
        self.running = True
        self.t0 = time.monotonic()
        self.buff.clear()
        self.canvas.clear_overlays()

        # valores iniciais (se disponíveis) para começar gráfico
        u0 = self.rv_u.current_value()
        y0 = self.rv_y.current_value()
        self._last_u = u0 if u0 is not None else self._last_u
        if u0 is not None or y0 is not None:
            self.buff.append(0.0, y0, u0)
            self._auto_axes()
            self._redraw()

        self._set_viewer_running_visual(True)
        print("[PV] START")
        self.simStartStop.emit(True)

    def on_stop(self):
        self.running = False
        self._set_viewer_running_visual(False)
        print("[PV] STOP")
        self.simStartStop.emit(False)

    def on_reset(self):
        self.on_stop()
        self.buff.clear()
        self.canvas.clear_overlays()
        self.canvas.ax.set_xlim(0, 10)
        self.canvas.ax.set_ylim(-1, 1)
        self._redraw()
        self.simReset.emit()

    def _toolbar_clear(self):
        """Limpa o gráfico e reinicia o tempo (t=0) a partir de agora."""
        self.buff.clear()
        self.canvas.clear_overlays()
        self.t0 = time.monotonic()
        # adiciona ponto inicial com valores correntes (se soubermos)
        u0 = getattr(self, "rv_u", None).current_value() if hasattr(self, "rv_u") else None
        y0 = getattr(self, "rv_y", None).current_value() if hasattr(self, "rv_y") else None
        if u0 is not None or y0 is not None:
            self.buff.append(0.0, y0, u0)
        self.canvas.ax.set_xlim(0, 1)
        self._auto_axes()
        self._redraw()

    # ---- Chamadas que o MAIN usa para espelhar apenas VISUAL aqui ----
    def sync_running_state(self, running: bool):
        self.running = bool(running)
        self._set_viewer_running_visual(self.running)

    def sync_reset(self):
        self.running = False
        self._set_viewer_running_visual(False)
        self.buff.clear()
        self.canvas.clear_overlays()
        self.canvas.ax.set_xlim(0, 10)
        self.canvas.ax.set_ylim(-1, 1)
        self._redraw()

    # ------------------------- Entrada (u) por +A/-A -------------------------
    def _apply_u_delta(self, delta: float):
        """Soma delta ao u atual e escreve na ReactVar."""
        if not hasattr(self, "rv_u"):
            QMessageBox.information(self, "Entrada (u)", "Selecione a variável de entrada (u).")
            return
        base = self._last_u
        if base is None:
            base = self.rv_u.current_value() or 0.0
        new_u = float(base) + float(delta)
        try:
            self.rv_u.write(new_u)
        except Exception as e:
            self.statusBar().showMessage(f"Falha ao escrever u: {e}")

    # ------------------------- Callbacks ReactVar -------------------------
    @Slot(object)
    def _on_u_external_any(self, payload: object):
        v = _extract_numeric(payload)
        print("[PV] SIG from RV:", v)
        if v is None:
            return
        self._last_u = float(v)
        if not self.running or self.t0 is None:
            return
        t = time.monotonic() - self.t0
        self.buff.append(t, y=None, u=float(v))
        self._auto_axes()
        self._redraw()

    @Slot(object)
    def _on_y_external(self, payload: object):
        v = _extract_numeric(payload)
        print("[PV] SIG from RV:", v)
        if v is None:
            return
        if not self.running or self.t0 is None:
            return
        t = time.monotonic() - self.t0
        self.buff.append(t, y=float(v), u=None)
        self._auto_axes()
        self._redraw()
        self._update_cursor_annotation(None)

    # ------------------------- Desenho -------------------------
    def _auto_axes(self):
        if len(self.buff.t) < 2:
            return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        self.canvas.ax.set_xlim(tmin, tmax)
        y_all = self.buff.y + self.buff.u  # concat listas para min/max global
        ymin, ymax = min(y_all), max(y_all)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        pad = 0.05 * (ymax - ymin)
        self.canvas.ax.set_ylim(ymin - pad, ymax + pad)

    def _redraw(self):
        npts = len(self.buff.t)
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        self.canvas.draw_idle()
        try:
            xlim = self.canvas.ax.get_xlim(); ylim = self.canvas.ax.get_ylim()
            print("[PV] REDRAW npts=", npts, "xlim=", xlim, "ylim=", ylim)
        except Exception:
            pass

    def _update_cursor_annotation(self, _):
        if self.canvas.lock_vline is None or not self.buff.t:
            return
        x = float(self.canvas.lock_vline.get_xdata()[0])
        idx = min(range(len(self.buff.t)), key=lambda i: abs(self.buff.t[i] - x))
        t_near = self.buff.t[idx]
        y_near = self.buff.y[idx]
        u_near = self.buff.u[idx]
        self.canvas.annot.xy = (t_near, y_near)
        self.canvas.annot.set_text(f"t={t_near:.2f}s\nPV={y_near:.4g}\nu={u_near:.4g}")
        self.canvas.annot.set_visible(True)
        self.canvas.draw_idle()

    # ------------------------- Identificação FOPDT -------------------------
    def on_clear(self):
        self.canvas.clear_overlays()
        self.statusBar().showMessage("Marcações removidas.")

    def on_fit(self):
        if len(self.buff.t) < 10:
            QMessageBox.information(self, "Identificação", "Poucos dados para identificar.")
            return
        t = np.asarray(self.buff.t, dtype=float)
        y = np.asarray(self.buff.y, dtype=float)
        u = np.asarray(self.buff.u, dtype=float)
        params = FOPDTIdentifier.fit_from_step(t, y, u)
        if params is None:
            QMessageBox.information(self, "Identificação", "Não foi possível estimar parâmetros (verifique o degrau e a curva).")
            return
        self.canvas.clear_overlays()
        self.canvas.add_vline(params.t_step, color="k", ls="--", lw=1.0)
        self.canvas.add_vline(params.t_delay, color="m", ls="--", lw=1.2)
        self.canvas.add_vline(params.t_settle, color="g", ls="--", lw=1.2)
        self.canvas.add_hline(params.y0, color="gray", ls=":", lw=1.0)
        self.canvas.add_hline(params.y_inf, color="gray", ls=":", lw=1.0)
        self.canvas.add_text(params.t_delay, params.y0, "  L", fontsize=9, color="m")
        self.canvas.add_text(params.t_settle, params.y_inf, "  t_settle", fontsize=9, color="g")
        self.canvas.draw_idle()
        QMessageBox.information(
            self,
            "Parâmetros FOPDT",
            (
                f"K={params.K:.4g}\nL={params.L:.4g} s\nτ={params.tau:.4g} s\n"
                f"t_step={params.t_step:.4g} s\n"
                f"t_delay={params.t_delay:.4g} s\n"
                f"t_settle≈{params.t_settle:.4g} s\n"
                f"y0={params.y0:.4g}, y∞={params.y_inf:.4g}"
            ),
        )


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
