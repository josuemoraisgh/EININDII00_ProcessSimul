#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Viewer (ReactVar) • PySide6 (com seleção por combobox do ReactFactory.df)
-------------------------------------------------------------------------------
• Varre self.factory.df e oferece comboboxes dependentes para escolher u e y:
  Tabela → Linha/Dispositivo → Coluna/Variável.
• Start/Stop/Reset sincronizados via sinais com a tela principal.
• Atualiza gráfico APENAS quando chegam sinais (sem timer).
• Reset: amarelo (idle) e azul (pressed).
• Escritura de u compatível com DBState.humanValue quando disponível.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple, List

import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QLineEdit, QSlider, QLabel, QGroupBox,
    QPushButton, QSpinBox, QAbstractSpinBox, QComboBox
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    # type: ignore
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Tentativa opcional de importar DBState (para escrita correta)
try:
    from db.db_types import DBState  # type: ignore
except Exception:
    DBState = None  # fallback


# =============================================================================
# Config
# =============================================================================

@dataclass
class UIConfig:
    CONTROL_PANEL_WIDTH: int = 360   # largura fixa do painel (px)
    SLIDER_STEPS: int = 10_000      # resolução do slider


# =============================================================================
# ReactVar adapter
# =============================================================================

ReactVarClass = None
try:
    from react.react_var import ReactVar as _RV  # type: ignore
    ReactVarClass = _RV
except Exception:
    try:
        from react_var import ReactVar as _RV  # type: ignore
        ReactVarClass = _RV
    except Exception:
        ReactVarClass = None


class ReactVarAdapter(QtCore.QObject):
    """Adapter que normaliza leitura do sinal e escrita com DBState quando existir."""
    changed = QtCore.Signal(float)

    def __init__(self, table: str, row: str, col: str, factory):
        super().__init__()
        if ReactVarClass is None:
            raise RuntimeError("ReactVar não encontrada (ajuste os imports).")
        self._rv = ReactVarClass(table, row, col, factory)
        # Conecta no sinal de mudança do ReactVar
        self._rv.valueChangedSignal.connect(self._on_raw)

    @Slot(object)
    def _on_raw(self, payload):
        """Payload pode ser o próprio ReactVar, um wrapper com _value ou um número."""
        val = None
        try:
            # 1) payload com atributo _value
            if hasattr(payload, "_value"):
                val = float(getattr(payload, "_value"))
            # 2) o payload já é numérico
            elif isinstance(payload, (int, float)):
                val = float(payload)
            # 3) tentamos acessar o próprio ReactVar interno
            elif hasattr(self, "_rv") and hasattr(self._rv, "_value"):
                val = float(getattr(self._rv, "_value"))
        except Exception:
            pass

        if val is not None:
            self.changed.emit(val)

    def write(self, v: float):
        """Escreve usando DBState.humanValue quando disponível; cai no melhor esforço."""
        try:
            if DBState is not None:
                self._rv.setValue(float(v), DBState.humanValue, True)
            else:
                # fallback comum em versões anteriores do seu ReactVar
                self._rv.setValue(float(v), isWidgetValueChanged=True)
        except TypeError:
            # última tentativa: assinatura simples
            self._rv.setValue(float(v))


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
        self.y.append(y if y is not None else y_last)
        self.u.append(u if u is not None else u_last)


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

        def cross(frac: float):
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
        self.resize(1200, 720)

        # Factory vem do construtor (não exibimos na UI)
        self.factory = react_factory if react_factory is not None else None
        self.simul_tf = simul_tf

        self.running = False
        self.t0: Optional[float] = None
        self.buff = DataBuffers(maxlen=20_000)

        self._build_ui()

    # -------- Helpers para varredura do df --------
    def _tables(self) -> List[str]:
        if not self.factory or not hasattr(self.factory, "df"):
            return []
        if isinstance(self.factory.df, dict):
            return list(self.factory.df.keys())
        return []

    def _rows(self, table: str) -> List[str]:
        try:
            df = self.factory.df[table]
            return [str(x) for x in df.index.tolist()]
        except Exception:
            return []

    def _cols(self, table: str) -> List[str]:
        try:
            df = self.factory.df[table]
            return [str(x) for x in df.columns.tolist()]
        except Exception:
            return []

    def _cell_is_reactvar(self, table: str, row: str, col: str) -> bool:
        try:
            cell = self.factory.df[table].at[row, col]
            # Import aqui evita import global forte
            from react.react_var import ReactVar as _RV  # type: ignore
            return isinstance(cell, _RV)
        except Exception:
            try:
                from react_var import ReactVar as _RV2  # type: ignore
                cell = self.factory.df[table].at[row, col]
                return isinstance(cell, _RV2)
            except Exception:
                return False

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Gráfico
        left = QVBoxLayout()
        self.canvas = MplCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, stretch=1)

        # Painel (largura fixa)
        right_container = QWidget(self)
        right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # --- Seleção de variáveis (u e y) ---
        g_sel = QGroupBox("Seleção de Variáveis (ReactFactory.df)")
        lay_sel = QFormLayout(g_sel)

        # Entrada (u)
        self.cb_u_table = QComboBox()
        self.cb_u_row = QComboBox()
        self.cb_u_col = QComboBox()
        self.lbl_u_valid = QLabel("—")
        lay_sel.addRow(QLabel("Entrada (u) — Tabela:"), self.cb_u_table)
        lay_sel.addRow(QLabel("Entrada (u) — Dispositivo/Linha:"), self.cb_u_row)
        lay_sel.addRow(QLabel("Entrada (u) — Variável/Coluna:"), self.cb_u_col)
        lay_sel.addRow(QLabel("u selecionado ✔︎?"), self.lbl_u_valid)

        # Saída (y)
        self.cb_y_table = QComboBox()
        self.cb_y_row = QComboBox()
        self.cb_y_col = QComboBox()
        self.lbl_y_valid = QLabel("—")
        lay_sel.addRow(QLabel("Saída (y) — Tabela:"), self.cb_y_table)
        lay_sel.addRow(QLabel("Saída (y) — Dispositivo/Linha:"), self.cb_y_row)
        lay_sel.addRow(QLabel("Saída (y) — Variável/Coluna:"), self.cb_y_col)
        lay_sel.addRow(QLabel("y selecionado ✔︎?"), self.lbl_y_valid)

        # Botão para ativar/atualizar as ReactVars a partir das seleções
        self.btn_connect = QPushButton("Ativar seleção (u & y)")
        self.btn_connect.clicked.connect(self.on_connect)
        lay_sel.addRow(self.btn_connect)

        # Preenche as tabelas (se houver factory)
        self._populate_table_combos()

        # Conexões dependentes + validação visual
        self.cb_u_table.currentIndexChanged.connect(lambda _: self._populate_row_col_for('u'))
        self.cb_y_table.currentIndexChanged.connect(lambda _: self._populate_row_col_for('y'))
        for cb in (self.cb_u_row, self.cb_u_col):
            cb.currentIndexChanged.connect(self._update_u_validity)
        for cb in (self.cb_y_row, self.cb_y_col):
            cb.currentIndexChanged.connect(self._update_y_validity)

        # Entrada (u) — controles
        g_u = QGroupBox("Entrada (u)")
        lay_u = QVBoxLayout(g_u)
        row_limits = QHBoxLayout()
        self.sb_umin = QDoubleSpinBox()
        self.sb_umin.setDecimals(3)
        self.sb_umin.setRange(-1e6, 1e6)
        self.sb_umin.setValue(-10.0)
        self.sb_umax = QDoubleSpinBox()
        self.sb_umax.setDecimals(3)
        self.sb_umax.setRange(1e-6, 1e6)
        self.sb_umax.setValue(10.0)
        self.sb_step = QDoubleSpinBox()
        self.sb_step.setDecimals(3)
        self.sb_step.setRange(1e-6, 1e6)
        self.sb_step.setValue(0.1)
        for sb in (self.sb_umin, self.sb_umax, self.sb_step):
            sb.setButtonSymbols(QAbstractSpinBox.NoButtons)
        row_limits.addWidget(QLabel("u_min"))
        row_limits.addWidget(self.sb_umin)
        row_limits.addWidget(QLabel("u_max"))
        row_limits.addWidget(self.sb_umax)
        row_limits.addWidget(QLabel("step"))
        row_limits.addWidget(self.sb_step)
        lay_u.addLayout(row_limits)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, UIConfig.SLIDER_STEPS)
        self.slider.valueChanged.connect(self._on_slider_changed)
        row_apply = QHBoxLayout()
        self.le_u = QLineEdit("0.0")
        self.btn_apply_u = QPushButton("Aplicar u")
        self.btn_apply_u.clicked.connect(self.apply_u_from_text)
        self.le_u.returnPressed.connect(self.apply_u_from_text)
        row_apply.addWidget(self.le_u)
        row_apply.addWidget(self.btn_apply_u)
        lay_u.addWidget(self.slider)
        lay_u.addLayout(row_apply)

        row_step = QHBoxLayout()
        self.sb_A = QDoubleSpinBox()
        self.sb_A.setDecimals(3)
        self.sb_A.setRange(0.0, 1e6)
        self.sb_A.setValue(1.0)
        self.btn_step_pos = QPushButton("+A")
        self.btn_step_neg = QPushButton("-A")
        self.btn_step_pos.clicked.connect(lambda: self.set_u(+self.sb_A.value()))
        self.btn_step_neg.clicked.connect(lambda: self.set_u(-self.sb_A.value()))
        row_step.addWidget(QLabel("A:"))
        row_step.addWidget(self.sb_A)
        row_step.addWidget(self.btn_step_pos)
        row_step.addWidget(self.btn_step_neg)
        lay_u.addLayout(row_step)

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
        self.sb_port = QSpinBox()
        self.sb_port.setRange(1, 65535)
        self.sb_port.setValue(502)
        row_port.addWidget(self.sb_port, 1)
        lay_sim.addLayout(row_port)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("reset")

        # Reset: amarelo idle, azul pressed
        self.btn_reset.setStyleSheet("""
            QPushButton { background: yellow; color: black; font-weight: bold; }
            QPushButton:pressed { background: #3498db; color: white; font-weight: bold; }
        """)

        # Botões checkables para manter estado e estilo
        self.btn_start.setCheckable(True)
        self.btn_stop.setCheckable(True)

        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_reset.clicked.connect(self.on_reset)

        lay_sim.addWidget(self.btn_start)
        lay_sim.addWidget(self.btn_stop)
        lay_sim.addWidget(self.btn_reset)

        # Ordem dos grupos (simulação por último)
        for w in (g_sel, g_u, g_id, g_sim):
            right.addWidget(w)
        right.addStretch(1)

        main.addLayout(left, stretch=1)
        main.addWidget(right_container)

        for w in (self.sb_umin, self.sb_umax, self.sb_step):
            w.valueChanged.connect(self._refresh_slider_mapping)
        self._refresh_slider_mapping()

        self.canvas.mpl_connect("button_press_event", self._update_cursor_annotation)

        # Estilo inicial (parado)
        self._set_viewer_running_visual(False)

    # ---- Populate combos a partir do df ----
    def _populate_table_combos(self):
        tables = self._tables()
        self.cb_u_table.blockSignals(True)
        self.cb_y_table.blockSignals(True)
        self.cb_u_table.clear(); self.cb_u_table.addItems(tables)
        self.cb_y_table.clear(); self.cb_y_table.addItems(tables)
        self.cb_u_table.blockSignals(False)
        self.cb_y_table.blockSignals(False)
        # popular linhas/colunas iniciais
        self._populate_row_col_for('u')
        self._populate_row_col_for('y')
        self._update_u_validity()
        self._update_y_validity()

    def _populate_row_col_for(self, which: str):
        if which == 'u':
            table = self.cb_u_table.currentText()
            rows = self._rows(table)
            cols = self._cols(table)
            self.cb_u_row.blockSignals(True)
            self.cb_u_col.blockSignals(True)
            self.cb_u_row.clear(); self.cb_u_row.addItems(rows)
            self.cb_u_col.clear(); self.cb_u_col.addItems(cols)
            self.cb_u_row.blockSignals(False)
            self.cb_u_col.blockSignals(False)
            self._update_u_validity()
        else:
            table = self.cb_y_table.currentText()
            rows = self._rows(table)
            cols = self._cols(table)
            self.cb_y_row.blockSignals(True)
            self.cb_y_col.blockSignals(True)
            self.cb_y_row.clear(); self.cb_y_row.addItems(rows)
            self.cb_y_col.clear(); self.cb_y_col.addItems(cols)
            self.cb_y_row.blockSignals(False)
            self.cb_y_col.blockSignals(False)
            self._update_y_validity()

    def _update_u_validity(self):
        t, r, c = self.cb_u_table.currentText(), self.cb_u_row.currentText(), self.cb_u_col.currentText()
        ok = bool(t and r and c and self.factory and self._cell_is_reactvar(t, r, c))
        self.lbl_u_valid.setText("✔︎ Válido" if ok else "✖︎ Inválido")
        self.lbl_u_valid.setStyleSheet("color: #2ecc71;" if ok else "color: #e74c3c;")

    def _update_y_validity(self):
        t, r, c = self.cb_y_table.currentText(), self.cb_y_row.currentText(), self.cb_y_col.currentText()
        ok = bool(t and r and c and self.factory and self._cell_is_reactvar(t, r, c))
        self.lbl_y_valid.setText("✔︎ Válido" if ok else "✖︎ Inválido")
        self.lbl_y_valid.setStyleSheet("color: #2ecc71;" if ok else "color: #e74c3c;")

    # ---------------- Execução (VISUAL + sinais p/ MAIN) ----------------
    def _set_viewer_running_visual(self, running: bool):
        """Atualiza apenas o VISUAL e 'checked' dos botões Start/Stop (sem emitir sinais)."""
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

    def on_start(self):
        if self.running:
            return
        # exige factory configurada e seleção feita
        if not self._ensure_selection_connected():
            return
        self.running = True
        self.t0 = time.monotonic()
        self.buff.clear()
        self.canvas.clear_overlays()
        # VISUAL + avisa o MAIN
        self._set_viewer_running_visual(True)
        self.simStartStop.emit(True)
        self.statusBar().showMessage("Rodando — aguardando sinais (y/u) para pintar.")

    def on_stop(self):
        self.running = False
        self._set_viewer_running_visual(False)
        self.simStartStop.emit(False)
        self.statusBar().showMessage("Parado.")

    def on_reset(self):
        self.on_stop()
        self.buff.clear()
        self.canvas.clear_overlays()
        self.canvas.ax.set_xlim(0, 10)
        self.canvas.ax.set_ylim(-1, 1)
        self._redraw()
        self.simReset.emit()
        self.statusBar().showMessage("Resetado.")

    # ---- Chamadas que o MAIN usa para ESPELHAR apenas VISUAL aqui ----
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

    # ---------------- Conexão ReactVar a partir das seleções ----------------
    def _ensure_selection_connected(self) -> bool:
        """Garante que rv_u e rv_y existem; caso contrário, tenta criar com base nas seleções."""
        if hasattr(self, "rv_u") and hasattr(self, "rv_y"):
            return True
        if self.factory is None or not hasattr(self.factory, "df"):
            QMessageBox.critical(self, "ReactFactory", "Factory não disponível. Abra pelo main que passa a factory.")
            return False
        try:
            self.on_connect()
            return hasattr(self, "rv_u") and hasattr(self, "rv_y")
        except Exception as e:
            QMessageBox.critical(self, "Conexão", f"Falha ao ativar seleção: {e}")
            return False

    def on_connect(self):
        if self.factory is None:
            QMessageBox.critical(self, "ReactFactory", "Factory não disponível.")
            return

        u_table = self.cb_u_table.currentText()
        u_row   = self.cb_u_row.currentText()
        u_col   = self.cb_u_col.currentText()
        y_table = self.cb_y_table.currentText()
        y_row   = self.cb_y_row.currentText()
        y_col   = self.cb_y_col.currentText()

        # Valida se as células escolhidas são ReactVar
        if not self._cell_is_reactvar(u_table, u_row, u_col):
            QMessageBox.warning(self, "Seleção u", f"A célula ({u_table}, {u_row}, {u_col}) não é uma ReactVar válida.")
            return
        if not self._cell_is_reactvar(y_table, y_row, y_col):
            QMessageBox.warning(self, "Seleção y", f"A célula ({y_table}, {y_row}, {y_col}) não é uma ReactVar válida.")
            return

        try:
            self.rv_u = ReactVarAdapter(u_table, u_row, u_col, self.factory)
            self.rv_y = ReactVarAdapter(y_table, y_row, y_col, self.factory)
            self.rv_u.changed.connect(self._on_u_external)
            self.rv_y.changed.connect(self._on_y_external)
            self.statusBar().showMessage(
                f"Conectado: u=({u_table},{u_row},{u_col}) | y=({y_table},{y_row},{y_col})"
            )
        except Exception as e:
            QMessageBox.critical(self, "ReactVar", f"Erro criando ReactVars:\n{e}")

    # ---------------- Entrada (u) ----------------
    def _refresh_slider_mapping(self):
        umin = self.sb_umin.value()
        umax = self.sb_umax.value()
        step = self.sb_step.value()
        if umax <= umin:
            umax = umin + step
            self.sb_umax.blockSignals(True)
            self.sb_umax.setValue(umax)
            self.sb_umax.blockSignals(False)
        self._umin, self._umax, self._ustep = umin, umax, step
        try:
            v = float(self.le_u.text().replace(",", "."))
        except Exception:
            v = 0.0
        v = self._snap(v)
        self._set_text_u(v)
        self._sync_slider_from_value(v)

    def _snap(self, v: float) -> float:
        v = max(self._umin, min(self._umax, v))
        step = self._ustep if self._ustep > 0 else 0.0
        if step > 0:
            q = round((v - self._umin) / step)
            v = self._umin + q * step
        return float(v)

    def _value_from_slider(self, pos: int) -> float:
        frac = pos / UIConfig.SLIDER_STEPS
        v = self._umin + frac * (self._umax - self._umin)
        return self._snap(v)

    def _sync_slider_from_value(self, v: float):
        v = max(self._umin, min(self._umax, v))
        denom = (self._umax - self._umin) if (self._umax - self._umin) != 0 else 1.0
        pos = int(round((v - self._umin) / denom * UIConfig.SLIDER_STEPS))
        pos = max(0, min(UIConfig.SLIDER_STEPS, pos))
        self.slider.blockSignals(True)
        self.slider.setValue(pos)
        self.slider.blockSignals(False)

    def _set_text_u(self, v: float):
        self.le_u.blockSignals(True)
        self.le_u.setText(f"{v:.6g}")
        self.le_u.blockSignals(False)

    def _apply_u(self, v: float):
        if hasattr(self, "rv_u"):
            try:
                self.rv_u.write(v)
            except Exception as e:
                self.statusBar().showMessage(f"Falha ao escrever u: {e}")
        if self.running and self.t0 is not None:
            t = time.monotonic() - self.t0
            self.buff.append(t, y=None, u=v)
            self._auto_axes()
            self._redraw()

    def _on_slider_changed(self, pos: int):
        v = self._value_from_slider(pos)
        self._set_text_u(v)
        self._apply_u(v)

    def apply_u_from_text(self):
        try:
            v = float(self.le_u.text().replace(",", "."))
        except Exception:
            QMessageBox.warning(self, "Entrada (u)", "Valor inválido.")
            return
        v = self._snap(v)
        self._set_text_u(v)
        self._sync_slider_from_value(v)
        self._apply_u(v)

    def set_u(self, v: float):
        v = self._snap(v)
        self._set_text_u(v)
        self._sync_slider_from_value(v)
        self._apply_u(v)

    # ---------------- Callbacks ReactVar ----------------
    @Slot(float)
    def _on_u_external(self, value: float):
        if not self.running or self.t0 is None:
            return
        v = self._snap(value)
        self._set_text_u(v)
        self._sync_slider_from_value(v)
        t = time.monotonic() - self.t0
        self.buff.append(t, y=None, u=float(v))
        self._auto_axes()
        self._redraw()

    @Slot(float)
    def _on_y_external(self, value: float):
        if not self.running or self.t0 is None:
            return
        t = time.monotonic() - self.t0
        self.buff.append(t, y=float(value), u=None)
        self._auto_axes()
        self._redraw()
        self._update_cursor_annotation(None)

    # ---------------- Desenho ----------------
    def _auto_axes(self):
        if len(self.buff.t) < 2:
            return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        self.canvas.ax.set_xlim(tmin, tmax)
        y_all = self.buff.y + self.buff.u
        ymin, ymax = min(y_all), max(y_all)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        pad = 0.05 * (ymax - ymin)
        self.canvas.ax.set_ylim(ymin - pad, ymax + pad)

    def _redraw(self):
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        self.canvas.draw_idle()

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

    # ---------------- Identificação FOPDT ----------------
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
