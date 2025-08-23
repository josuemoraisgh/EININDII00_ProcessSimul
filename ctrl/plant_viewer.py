<<<<<<< HEAD
=======

"""
Plant Viewer (ReactVar) • PySide6

Correções/recursos:
• Timer do modo Real conectado ao método _on_real_tick (presente nesta classe).
• StepTimer [ms] sincroniza gráfico, simulador local (Sim) e SimulTf global.
• "Limpar Tela" replanta t=0 com o último ponto (y,u) e segue contínuo.
• A janela abre já lendo o step do SimulTf, se disponível.
"""
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

# -*- coding: utf-8 -*-
"""
Plant Viewer — estável (sem perda de funcionalidades) — PyQt5/PySide6
- Toolbar do Matplotlib no TOPO (V/H/Kp/Limpar/🧹 Limpar Tela).
- Auto-seleção por combobox; persistência em storage PV_CFG/SELECTION.
- Start/Stop com cores (press = azul; final: Start=verde, Stop=vermelho).
- Ajuste COLAPSADO por padrão; StepTimer [ms]=500 governa Real e Simulado.
- Simulado (FOPDT: Kp, tau, L) com +A/-A em sim_u.
- Real: +A/-A escreve em u (0..65535); reset/🧹 recomeça em t=0 com últimos valores.
- Eixos com 5% de margem e sem offset científico (+1.63e4 removido).
- Abre com MAIN já rodando → semeia e desenha imediatamente.
- Combobox y filtra BYTE_SIZE/TYPE (não aparecem).
"""
from __future__ import annotations

import time
import inspect
import asyncio
from collections import deque
from typing import Any, List, Tuple, Optional

<<<<<<< HEAD
# Qt compat
try:
    from PySide6.QtCore import Qt, QTimer, Signal, Slot
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
        QGroupBox, QPushButton, QTabWidget
    )
    PYSIDE = True
except Exception:
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal, pyqtSlot as Slot
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
        QGroupBox, QPushButton, QTabWidget
    )
    PYSIDE = False
=======
from PySide6 import QtCore
from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QMainWindow, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QComboBox, QGroupBox, QPushButton, QSpinBox, QLabel, QTabWidget
)

# Importa o canvas/toolbar utilitário do projeto.
try:
    from ctrl.mpl_canvas import *  # UIConfig, MplCanvas, PVToolbar, ReactVarAdapter, DataBuffers, ReactVarClass
except Exception:  # pragma: no cover
    from mpl_canvas import *

>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

from ctrl.mpl_canvas import (
    MplCanvas, PVToolbar, UIConfig,
    ReactVarAdapter, DataBuffers,
)

# --------- Conversão u: human (0..65535) <-> percent (0..100) ---------
def _u_human_to_percent(h: float) -> float:
    try:
        return float(h) * 100.0 / 65535.0
    except Exception:
        return 0.0

def _u_percent_to_human(p: float) -> float:
    try:
        return round(float(p) * 65535.0 / 100.0)
    except Exception:
        return 0.0

<<<<<<< HEAD
=======

>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
class PlantViewerWindow(QMainWindow):
    simStartStop = Signal(bool)
    simReset = Signal()

<<<<<<< HEAD
    # ---------------- Toolbar hooks exigidos pela PVToolbar ----------------
    def set_cursor_mode(self, mode: Optional[str]):
        try:
            self.canvas.set_cursor_mode(mode)
        except Exception:
            pass

    def set_kp_mode(self, enabled: bool):
        try:
            self.canvas.set_kp_mode(bool(enabled))
        except Exception:
            pass

=======
    def __init__(self, react_factory=None, simul_tf=None):
        super().__init__()
        self.setWindowTitle("Planta (ReactVar) — Viewer")
        self.resize(1200, 700)

        self.factory = react_factory
        self.simul_tf = simul_tf

        # ----------------- Estado Real -----------------
        self.running = False                   # estado lógico (start/stop)
        self.t0: Optional[float] = None        # referência de tempo do modo Real
        self.buff = DataBuffers(200_000)

        # Cache dos últimos valores (consumidos no timer)
        self._last_u_percent: Optional[float] = None
        self._last_y: Optional[float] = None

        # Flag de pintura segura
        self._ready_to_paint = False

        # Timer do modo Real
        self.real_timer = QtCore.QTimer(self)
        self.real_timer.timeout.connect(self._on_real_tick)

        # ----------------- Estado Simulado -----------------
        self.sim_running = False
        self.sim_Kp = 1.0
        self.sim_tau = 1.0
        self.sim_L = 0.0
        self.sim_dt = 0.05  # s (passo nominal; a integração usa Δt real)
        self.sim_t = 0.0
        self.sim_y = 0.0
        self.sim_u = 0.0

        # relógio do simulador (pareado ao monotonic): garante Δt real
        self._sim_wall_t0: Optional[float] = None
        self._sim_last_wall_t: Optional[float] = None

        # Atraso puro contínuo no modo Simulado: histórico (t,u) + interpolação
        self.sim_hist = deque(maxlen=4096)
        self.sim_timer = QtCore.QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_tick)

        self._build_ui()
        self._populate_from_factory()

        # Inicializa StepTimer com o valor do simulador global (se houver)
        try:
            if self.simul_tf is not None and hasattr(self.simul_tf, 'stepTime'):
                self.sb_sim_dt.setValue(int(self.simul_tf.stepTime))
        except Exception:
            pass

    # Ativa pintura segura após a janela estar visível
    def showEvent(self, ev):
        super().showEvent(ev)
        self._ready_to_paint = True
        QTimer.singleShot(0, self._redraw)

    # -------------------------- UI --------------------------
    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Plot
        left = QVBoxLayout()
        self.canvas = MplCanvas(self)
        try:
            self.canvas.ax_u.set_ylabel('u [%]')
        except Exception:
            pass
        self.toolbar = PVToolbar(self.canvas, self)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, 1)

        # Painel lateral
        right_container = QWidget(self); right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # Seleção de variáveis (2 combos)
        g_sel = QGroupBox("Seleção de Variáveis Reais")
        lay_sel = QFormLayout(g_sel)
        self.cb_u_row = QComboBox()  # Entrada (u): MODBUS rows
        self.cb_y_col = QComboBox()  # Saída (y):  HART columns
        lay_sel.addRow("Entrada (u):", self.cb_u_row)
        lay_sel.addRow("Saída (y):", self.cb_y_col)
        right.addWidget(g_sel)

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
        real_lay.addWidget(self.btn_start); real_lay.addWidget(self.btn_stop); real_lay.addWidget(self.btn_reset)

        # Aba Simulado
        self.tab_sim = QWidget(); sim_lay = QFormLayout(self.tab_sim)
        self.sb_sim_Kp = QDoubleSpinBox(); self.sb_sim_Kp.setDecimals(4); self.sb_sim_Kp.setRange(-1e6, 1e6); self.sb_sim_Kp.setValue(1.0)
        self.sb_sim_tau = QDoubleSpinBox(); self.sb_sim_tau.setDecimals(4); self.sb_sim_tau.setRange(1e-6, 1e6); self.sb_sim_tau.setValue(1.0)
        self.sb_sim_L   = QDoubleSpinBox(); self.sb_sim_L.setDecimals(4); self.sb_sim_L.setRange(0.0, 1e6); self.sb_sim_L.setValue(0.0)
        self.btn_sim_start = QPushButton("Start (Sim)")
        self.btn_sim_stop  = QPushButton("Stop (Sim)")
        self.btn_sim_start.clicked.connect(self.on_sim_start_clicked)
        self.btn_sim_stop.clicked.connect(self.on_sim_stop_clicked)
        sim_lay.addRow("Kp:", self.sb_sim_Kp)
        sim_lay.addRow("τ (tau):", self.sb_sim_tau)
        sim_lay.addRow("Atraso (L) [s]:", self.sb_sim_L)
        sim_lay.addRow(self.btn_sim_start)
        sim_lay.addRow(self.btn_sim_stop)

        self.tabs_adj.addTab(self.tab_real, "Real")
        self.tabs_adj.addTab(self.tab_sim, "Simulado")

        # StepTimer global fora das abas
        w_dt = QWidget(self); lay_dt = QFormLayout(w_dt)
        self.sb_sim_dt = QSpinBox(); self.sb_sim_dt.setRange(1, 2000); self.sb_sim_dt.setValue(50)  # ms
        lay_dt.addRow("StepTimer [ms]:", self.sb_sim_dt)
        info = QLabel("Atualização do gráfico (Real) e passo de integração (Sim).")
        info.setWordWrap(True)
        lay_dt.addRow(info)

        adj_lay.addWidget(w_dt)
        adj_lay.addWidget(self.tabs_adj)

        # Entrada (u): A, +A, -A
        g_u = QGroupBox("Entrada (u)")
        lay_u = QHBoxLayout(g_u)
        self.sb_A = QDoubleSpinBox(); self.sb_A.setDecimals(3); self.sb_A.setRange(-1e9, 1e9); self.sb_A.setValue(1.0); self.sb_A.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.btn_step_pos = QPushButton("+A"); self.btn_step_neg = QPushButton("-A")
        self.btn_step_pos.clicked.connect(lambda: self._inc_u(+self.sb_A.value()))
        self.btn_step_neg.clicked.connect(lambda: self._inc_u(-self.sb_A.value()))
        lay_u.addWidget(QLabel("A:")); lay_u.addWidget(self.sb_A, 1); lay_u.addWidget(self.btn_step_pos); lay_u.addWidget(self.btn_step_neg)

        for w in (g_sel, g_adj, g_u):
            right.addWidget(w)
        right.addStretch(1)

        main.addLayout(left, 1)
        main.addWidget(right_container)

        self._set_running_visual(False)
        # Conecta StepTimer ao handler que sincroniza todos os relógios
        self.sb_sim_dt.valueChanged.connect(self._on_step_timer_changed)

    # ----------------------- Exclusividade dos modos -----------------------
    def set_cursor_mode(self, mode: Optional[str]):
        if mode == 'v':
            self.toolbar.act_h.blockSignals(True); self.toolbar.act_h.setChecked(False); self.toolbar.act_h.blockSignals(False)
        elif mode == 'h':
            self.toolbar.act_v.blockSignals(True); self.toolbar.act_v.setChecked(False); self.toolbar.act_v.blockSignals(False)
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

    # ----------------------- Limpar / Reset -----------------------
    def _seed_after_clear(self):
        """
        Replanta t=0 com os últimos valores conhecidos de y e u.
        Se cache estiver vazio, tenta leitura síncrona das ReactVars.
        """
        y0 = self._last_y
        u0 = self._last_u_percent

        if y0 is None and hasattr(self, "rv_y"):
            try:
                cur_y = self.rv_y.read_sync()
                if cur_y is not None:
                    y0 = float(cur_y)
            except Exception:
                pass
        if u0 is None and hasattr(self, "rv_u"):
            try:
                cur_h = self.rv_u.read_sync()
                if cur_h is not None:
                    u0 = _u_human_to_percent(cur_h)
            except Exception:
                pass

        if y0 is None: y0 = 0.0
        if u0 is None: u0 = 0.0

        self.t0 = time.monotonic()
        self.buff.clear()
        self.buff.append(0.0, y=float(y0), u=float(u0))
        self._auto_axes()
        self._safe_redraw()

>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
    def on_clear_cursors_clicked(self):
        try:
            self.canvas.clear_cursors()
        except Exception:
            pass

    def on_reset_toolbar(self):
<<<<<<< HEAD
        try:
            self.canvas.clear_overlays()
        except Exception:
            pass
        try:
            self.canvas.clear_cursors()
        except Exception:
            pass
        self.sync_reset()

    def __init__(self, react_factory=None, factory=None, simul_tf=None, parent=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("Planta (ReactVar) — Viewer")
        self.resize(1200, 700)

        self.factory = react_factory or factory
        self.simul_tf = simul_tf
        self.mb_port = kwargs.get("mb_port", kwargs.get("MB_PORT", 502))

        # Estados
        self.running = False
        self.t0: Optional[float] = None
        self.buff = DataBuffers(200_000)
        self._last_u_percent: Optional[float] = None
        self._last_y: Optional[float] = None

        self.real_timer = QTimer(self)
        self.real_timer.timeout.connect(self._on_real_tick)

        # Simulador
        self.sim_running = False
        self.sim_Kp = 1.0; self.sim_tau = 1.0; self.sim_L = 0.0
        self.sim_dt = 0.05
        self.sim_t = 0.0; self.sim_y = 0.0; self.sim_u = 0.0
        self.sim_delay_buf = deque([0.0], maxlen=1)
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_tick)

        # UI
        self._build_ui()
        self._configure_axis_formatters()
        self._populate_from_factory()
        self._restore_selection()
        self.on_connect_clicked()

    # ======================= UI =======================
    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Plot e toolbar
        left = QVBoxLayout()
        self.canvas = MplCanvas(self)
        self._ensure_lines()
        try:
            self.canvas.ax_u.set_ylabel('Entrada (u)')
        except Exception:
            pass
        self.toolbar = PVToolbar(self.canvas, self)  # topo
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, 1)

        # Painel lateral
        right_container = QWidget(self); right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # Seleção de variáveis
        g_sel = QGroupBox("Seleção de Variáveis Reais"); lay_sel = QFormLayout(g_sel)
        self.cb_u_row = QComboBox(); self.cb_y_col = QComboBox()
        lay_sel.addRow("Entrada (u):", self.cb_u_row)
        lay_sel.addRow("Saída (y):", self.cb_y_col)
        self.lbl_conn = QLabel("Conexão: —"); lay_sel.addRow(self.lbl_conn)
        right.addWidget(g_sel)

        # Ajuste (colapsado por padrão)
        g_adj = QGroupBox("Ajuste"); g_adj.setCheckable(True); g_adj.setChecked(False)
        lay_adj = QVBoxLayout(g_adj)
        self._adj_inner = QWidget(g_adj); adj_form = QFormLayout(self._adj_inner)

        self.sb_sim_dt = QSpinBox(); self.sb_sim_dt.setRange(1, 5000); self.sb_sim_dt.setValue(500)
        adj_form.addRow("StepTimer [ms]:", self.sb_sim_dt)

        self.tabs_adj = QTabWidget(); adj_form.addRow(self.tabs_adj)

        # Aba Real
        self.tab_real = QWidget(); real_lay = QVBoxLayout(self.tab_real)
        row_port = QHBoxLayout()
        row_port.addWidget(QLabel("MB_PORT:"))
        self.cb_mb_port = QComboBox(); self.cb_mb_port.addItems([str(self.mb_port)])
        row_port.addWidget(self.cb_mb_port, 1)
        real_lay.addLayout(row_port)

        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop")
        self.btn_start.setCheckable(True); self.btn_stop.setCheckable(True)
        self.btn_reset = QPushButton("reset"); self._style_btn_reset_idle()
        # press = azul
        self.btn_start.pressed.connect(lambda: self.btn_start.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_stop.pressed.connect(lambda: self.btn_stop.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.pressed.connect(lambda: self.btn_reset.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.released.connect(self._style_btn_reset_idle)

        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)

        real_lay.addWidget(self.btn_start); real_lay.addWidget(self.btn_stop); real_lay.addWidget(self.btn_reset)
        self.tabs_adj.addTab(self.tab_real, "Real")

        # Aba Simulado (FOPDT)
        self.tab_sim = QWidget(); sim_lay = QFormLayout(self.tab_sim)
        self.sb_sim_Kp = QDoubleSpinBox(); self.sb_sim_Kp.setDecimals(4); self.sb_sim_Kp.setRange(-1e6, 1e6); self.sb_sim_Kp.setValue(1.0)
        self.sb_sim_tau = QDoubleSpinBox(); self.sb_sim_tau.setDecimals(4); self.sb_sim_tau.setRange(1e-6, 1e6); self.sb_sim_tau.setValue(1.0)
        self.sb_sim_L   = QDoubleSpinBox(); self.sb_sim_L.setDecimals(4); self.sb_sim_L.setRange(0.0, 1e6); self.sb_sim_L.setValue(0.0)
        self.btn_sim_start = QPushButton("Start (Sim)")
        self.btn_sim_stop  = QPushButton("Stop (Sim)")
        self.btn_sim_start.clicked.connect(self.on_sim_start_clicked)
        self.btn_sim_stop.clicked.connect(self.on_sim_stop_clicked)
        sim_lay.addRow("Kp:", self.sb_sim_Kp)
        sim_lay.addRow("τ (tau):", self.sb_sim_tau)
        sim_lay.addRow("Atraso (L) [s]:", self.sb_sim_L)
        sim_lay.addRow(self.btn_sim_start)
        sim_lay.addRow(self.btn_sim_stop)
        self.tabs_adj.addTab(self.tab_sim, "Simulado")

        lay_adj.addWidget(self._adj_inner)
        right.addWidget(g_adj)

        # Entrada (u): A, +A, -A
        g_u = QGroupBox("Entrada (u)"); ly_u = QFormLayout(g_u)
        row = QHBoxLayout(); self.ds_A = QDoubleSpinBox(); self.ds_A.setDecimals(3); self.ds_A.setRange(-1e6, 1e6); self.ds_A.setValue(1.000)
        self.btn_plusA = QPushButton("+A"); self.btn_minusA = QPushButton("-A")
        self.btn_plusA.clicked.connect(lambda: self._on_plus_minus_A(+1))
        self.btn_minusA.clicked.connect(lambda: self._on_plus_minus_A(-1))
        row.addWidget(QLabel("A:")); row.addWidget(self.ds_A); row.addWidget(self.btn_plusA); row.addWidget(self.btn_minusA)
        ly_u.addRow(row)
        right.addWidget(g_u)

        right.addStretch(1)

        main.addLayout(left, 1)
        main.addWidget(right_container)

        g_adj.toggled.connect(self._adj_inner.setVisible)
        self._adj_inner.setVisible(False)

        # Interações
        self.cb_u_row.currentIndexChanged.connect(lambda *_: self.on_connect_clicked())
        self.cb_y_col.currentIndexChanged.connect(lambda *_: self.on_connect_clicked())
        self.sb_sim_dt.valueChanged.connect(self._on_dt_changed)

        self._set_running_visual(False)

    def _style_btn_reset_idle(self):
        self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;")

    # ======================= Eixos/formatters =======================
    def _configure_axis_formatters(self):
        try:
            from matplotlib.ticker import ScalarFormatter
            for ax in (self.canvas.ax_y, self.canvas.ax_u):
                ax.ticklabel_format(axis='both', style='plain', useOffset=False, useMathText=False)
                fmt = ScalarFormatter(useOffset=False); fmt.set_scientific(False)
                ax.yaxis.set_major_formatter(fmt)
                try: ax.yaxis.get_offset_text().set_visible(False)
                except Exception: pass
                try: ax.xaxis.get_offset_text().set_visible(False)
                except Exception: pass
        except Exception:
            pass

    # ======================= Populate/Persist =======================
    def _get_df_maps(self) -> Tuple[Optional[Any], Optional[Any]]:
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

    def _list_candidate_vars(self) -> Tuple[List[str], List[str]]:
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
=======
        """
        🧹 Limpar Tela: limpa overlays/cursores e REPLANTA ponto inicial com y/u atuais.
        Não para timers, não mexe no estado Start/Stop.
        """
        try: self.canvas.clear_overlays()
        except Exception: pass
        try: self.canvas.clear_cursors()
        except Exception: pass
        self._seed_after_clear()
        self.sim_t = 0.0  # sim: reinicia tempo relativo apenas
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

    def _populate_from_factory(self):
<<<<<<< HEAD
        u_items, y_items = self._list_candidate_vars()
        self.cb_u_row.blockSignals(True); self.cb_y_col.blockSignals(True)
        self.cb_u_row.clear(); self.cb_u_row.addItems(u_items)
        self.cb_y_col.clear(); self.cb_y_col.addItems(y_items)
        self.cb_u_row.blockSignals(False); self.cb_y_col.blockSignals(False)

    def _restore_selection(self):
        try:
            st = getattr(self.factory, "storage", None)
            if st is None: return
            u_saved = st.getRawData("PV_CFG", "SELECTION", "u_row") or ""
            y_saved = st.getRawData("PV_CFG", "SELECTION", "y_col") or ""
            if u_saved:
                i = self.cb_u_row.findText(str(u_saved))
                if i >= 0: self.cb_u_row.setCurrentIndex(i)
            if y_saved:
                j = self.cb_y_col.findText(str(y_saved))
                if j >= 0: self.cb_y_col.setCurrentIndex(j)
        except Exception:
            pass

    def _persist_selection(self, u_name: str, y_name: str):
        try:
            st = getattr(self.factory, "storage", None)
            if st is not None:
                st.setRawData("PV_CFG", "SELECTION", "u_row", u_name)
                st.setRawData("PV_CFG", "SELECTION", "y_col", y_name)
        except Exception:
            pass

    # ======================= Conexão de RVs =======================
    def _get_rv_from_df(self, u_name: str, y_name: str):
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

    def on_connect_clicked(self):
        u_name = self.cb_u_row.currentText().strip()
        y_name = self.cb_y_col.currentText().strip()
        rv_u, rv_y = self._get_rv_from_df(u_name, y_name)
        self.rv_u = ReactVarAdapter(rv_u) if rv_u is not None else self._get_react_var(u_name)
        self.rv_y = ReactVarAdapter(rv_y) if rv_y is not None else self._get_react_var(y_name)

        def _safe_connect(rv, slot):
            if rv is None: return
            for sig_name in ("changed", "valueChangedSignal", "onChanged"):
                sig = getattr(rv, sig_name, None)
                if sig is not None:
                    try: sig.connect(slot); break
                    except Exception: pass
        _safe_connect(self.rv_y, self._on_y_external)
        _safe_connect(self.rv_u, self._on_u_external)

        self.lbl_conn.setText(f"Conexão: u={u_name} | y={y_name}")
        self._persist_selection(u_name, y_name)

        # Se já estiver rodando, atualiza hold e garante semente/redesenho
        if self.running:
            try:
                cur_h = self._read_sync(self.rv_u)
                cur_y = self._read_sync(self.rv_y)
                if cur_h is not None: self._last_u_percent = _u_human_to_percent(cur_h)
                if cur_y is not None: self._last_y = float(cur_y)
            except Exception:
                pass
            if self.t0 is None or len(self.buff.t) == 0:
                self.t0 = time.monotonic()
                self.buff.clear()
                y0 = 0.0 if self._last_y is None else float(self._last_y)
                u0 = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
                self.buff.append(0.0, y=y0, u=u0)
            self._auto_axes(); self._redraw()

    # ======================= Start/Stop/Reset (Real) =======================
=======
        self._df = getattr(self.factory, "df", None)
        if not self._df:
            return
        try:
            df_u = self._df.get("MODBUS")
            self.cb_u_row.clear()
            if df_u is not None:
                w_rows = [str(x) for x in df_u.index if isinstance(x, str) and x.startswith('W_')]
                w_rows.sort()
                self.cb_u_row.addItems(w_rows)
        except Exception:
            pass
        try:
            df_y = self._df.get("HART")
            self.cb_y_col.clear()
            if df_y is not None:
                cols = list(df_y.columns)
                if len(cols) > 2:
                    cols = cols[2:]
                self.cb_y_col.addItems([str(c) for c in cols])
        except Exception:
            pass

        try:
            self.cb_u_row.currentIndexChanged.connect(lambda _: self.on_connect_clicked())
            self.cb_y_col.currentIndexChanged.connect(lambda _: self.on_connect_clicked())
        except Exception:
            pass

    # -------------------------- Start/Stop/Reset (Real) --------------------------
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
    def _set_running_visual(self, running: bool):
        self.btn_start.blockSignals(True); self.btn_stop.blockSignals(True)
        self.btn_start.setChecked(running); self.btn_stop.setChecked(not running)
        if running:
            self.btn_start.setStyleSheet("background:#2ecc71; color:white; font-weight:bold;")   # verde
            self.btn_stop.setStyleSheet("")
        else:
            self.btn_start.setStyleSheet("")
            self.btn_stop.setStyleSheet("background:#ff2d2d; color:white; font-weight:bold;")     # vermelho
        self.btn_start.blockSignals(False); self.btn_stop.blockSignals(False)

    def on_start_clicked(self):
<<<<<<< HEAD
        if self.running: return
        cur_h_u = self._read_sync(self.rv_u); cur_y = self._read_sync(self.rv_y)
        if cur_h_u is None: cur_h_u = 0.0
        if cur_y   is None: cur_y   = 0.0
        self._last_u_percent = _u_human_to_percent(cur_h_u); self._last_y = float(cur_y)
        self.t0 = time.monotonic(); self.buff.clear()
        self.buff.append(0.0, y=self._last_y, u=self._last_u_percent)
        self._auto_axes(); self._redraw()
        self.running = True; self._set_running_visual(True)
        self.simStartStop.emit(True); self.real_timer.start(int(max(1, self.sb_sim_dt.value())))

    def on_stop_clicked(self):
        self.running = False; self._set_running_visual(False)
=======
        self._start_real_mode()

    def on_stop_clicked(self):
        self._stop_real_mode()

    def _start_real_mode(self):
        if self.running:
            return
        if not hasattr(self, "rv_u") or not hasattr(self, "rv_y"):
            self.on_connect_clicked()
            if not (hasattr(self, "rv_u") and hasattr(self, "rv_y")):
                return

        try:
            cur_h_u = self.rv_u.read_sync()
        except Exception:
            cur_h_u = None
        try:
            cur_y = self.rv_y.read_sync()
        except Exception:
            cur_y = None
        if cur_h_u is None: cur_h_u = 0.0
        if cur_y   is None: cur_y   = 0.0
        self._last_u_percent = _u_human_to_percent(cur_h_u)
        self._last_y = float(cur_y)

        self._seed_after_clear()  # t0 novo + ponto inicial

        self.running = True
        self._set_running_visual(True)
        self.simStartStop.emit(True)

        self.real_timer.start(int(max(1, self.sb_sim_dt.value())))
        self._on_real_tick()  # tick imediato

    def _stop_real_mode(self):
        if not self.running:
            return
        self.running = False
        self._set_running_visual(False)
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
        self.simStartStop.emit(False)
        try: self.real_timer.stop()
        except Exception: pass

    def on_reset_clicked(self):
<<<<<<< HEAD
        self.on_stop_clicked()
        self.buff.clear()
        y0 = 0.0 if self._last_y is None else float(self._last_y)
        u0 = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        self.t0 = time.monotonic(); self.buff.append(0.0, y=y0, u=u0)
        self._auto_axes(); self._redraw()
=======
        """
        Botão 'reset': limpa visuais e REPLANTA ponto inicial com y/u atuais.
        Mantém timers conforme estado (rodando ou parado).
        """
        try: self.canvas.clear_overlays()
        except Exception: pass
        self._seed_after_clear()
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
        self.simReset.emit()
        self.sim_t = 0.0

    # ======================= Simulador FOPDT =======================
    def _on_dt_changed(self, v):
        iv = int(max(1, v))
        if self.running: self.real_timer.setInterval(iv)
        if self.sim_running: self.sim_timer.setInterval(iv)

<<<<<<< HEAD
    def _init_sim_delay_buf(self):
        N = max(1, int(round(self.sim_L / self.sim_dt))) if self.sim_dt > 0 else 1
        self.sim_delay_buf = deque([self.sim_u]*N, maxlen=N)
=======
    def on_connect_clicked(self):
        """Troca de variáveis em voo; mantém traçado e timers.
           Se estiver rodando, marca a troca com vline suave (alpha=0.25).
        """
        if ReactVarClass is None or self._df is None:
            return
        t_now = time.monotonic()
        t_rel = (t_now - self.t0) if (self.t0 is not None) else 0.0

        self._disconnect_current()
        try:
            t_u = 'MODBUS'
            r_u = self.cb_u_row.currentText()
            c_u = 'CLP100'
            t_y = 'HART'
            r_y = 'PROCESS_VARIABLE'
            c_y = self.cb_y_col.currentText()

            rv_u_obj = self._df[t_u].at[r_u, c_u]
            rv_y_obj = self._df[t_y].at[r_y, c_y]

            self.rv_u = ReactVarAdapter(rv_u_obj)
            self.rv_y = ReactVarAdapter(rv_y_obj)

            self.rv_u.changed.connect(self._on_u_external)
            self.rv_y.changed.connect(self._on_y_external)

            if self.running:
                if not self.real_timer.isActive():
                    self.real_timer.start(int(max(1, self.sb_sim_dt.value())))

                try:
                    cur_h_u = self.rv_u.read_sync()
                    if cur_h_u is not None:
                        self._last_u_percent = _u_human_to_percent(cur_h_u)
                except Exception:
                    pass
                try:
                    cur_y = self.rv_y.read_sync()
                    if cur_y is not None:
                        self._last_y = float(cur_y)
                except Exception:
                    pass

                self.buff.append(t_rel,
                                 y=self._last_y if self._last_y is not None else 0.0,
                                 u=self._last_u_percent if self._last_u_percent is not None else 0.0)
                try:
                    self.canvas.add_vline(t_rel, color='k', ls=':', lw=1.0, alpha=0.25)
                except Exception:
                    pass

                self._auto_axes(); self._safe_redraw()
                self._on_real_tick()

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
            cur_h = self.rv_u.read_sync()  # human 0..65535
            if cur_h is None:
                cur_h = 0.0
            cur_p = _u_human_to_percent(cur_h)
            new_p = float(cur_p) + float(delta)  # delta em %
            new_h = _u_percent_to_human(new_p)
            self.rv_u.write(new_h)

    # -------------------------- Callbacks (Real) --------------------------
    @Slot(float)
    def _on_u_external(self, value: float):
        self._last_u_percent = _u_human_to_percent(value)

    @Slot(float)
    def _on_y_external(self, value: float):
        self._last_y = float(value)

    def _on_real_tick(self):
        if not self.running or self.t0 is None:
            return
        if self._last_u_percent is None and hasattr(self, "rv_u"):
            try:
                cur_h_u = self.rv_u.read_sync()
                if cur_h_u is not None:
                    self._last_u_percent = _u_human_to_percent(cur_h_u)
            except Exception:
                pass
        if self._last_y is None and hasattr(self, "rv_y"):
            try:
                cur_y = self.rv_y.read_sync()
                if cur_y is not None:
                    self._last_y = float(cur_y)
            except Exception:
                pass

        u_val = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        y_val = 0.0 if self._last_y is None else float(self._last_y)

        t = time.monotonic() - self.t0
        self.buff.append(t, y=y_val, u=u_val)
        self._auto_axes(); self._safe_redraw()

    # -------------------------- Simulador FOPDT (com atraso contínuo e Δt real) --------------------------
    def _init_sim_delay_hist(self):
        """Semeia histórico (t,u) do simulador para atraso puro contínuo."""
        self.sim_hist.clear()
        self.sim_hist.append((0.0, float(self.sim_u)))

    def _u_sim_at(self, t_query: float) -> float:
        """u(t_query) por interpolação no histórico do simulador (robusto a jitter)."""
        if not self.sim_hist:
            return float(self.sim_u)

        # mantém a deque curta, removendo amostras MUITO antigas (não subtrai L de novo)
        keep_after = t_query - 2.0 * max(self.sim_dt, 1e-6)
        while len(self.sim_hist) >= 3 and self.sim_hist[1][0] < keep_after:
            self.sim_hist.popleft()

        if t_query <= self.sim_hist[0][0]:
            return float(self.sim_hist[0][1])
        if t_query >= self.sim_hist[-1][0]:
            return float(self.sim_hist[-1][1])

        for i in range(len(self.sim_hist) - 1):
            t0, u0 = self.sim_hist[i]
            t1, u1 = self.sim_hist[i + 1]
            if t0 <= t_query <= t1:
                if t1 == t0: return float(u1)
                a = (t_query - t0) / (t1 - t0)
                return float((1 - a) * u0 + a * u1)
        return float(self.sim_hist[-1][1])
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

    def on_sim_start_clicked(self):
        self.sim_Kp = float(self.sb_sim_Kp.value())
        self.sim_tau = float(self.sb_sim_tau.value())
        self.sim_L   = float(self.sb_sim_L.value())
<<<<<<< HEAD
        self.sim_dt  = float(self.sb_sim_dt.value()) / 1000.0
        self._init_sim_delay_buf()
=======
        self.sim_dt  = float(self.sb_sim_dt.value()) / 1000.0  # ms → s

        self._init_sim_delay_hist()  # atraso puro contínuo

        # reseta relógio do simulador (usa tempo absoluto para Δt)
        wall = time.monotonic()
        self._sim_wall_t0 = wall
        self._sim_last_wall_t = wall

>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
        self.sim_running = True
        self.sim_t = 0.0
        self.sim_y = self.buff.y[-1] if self.buff.y else 0.0
        self.t0 = wall  # eixo x do gráfico alinha com o relógio do simulador
        self.buff.clear()
<<<<<<< HEAD
        self._auto_axes(); self._redraw()
        self.sim_timer.start(int(max(1, self.sb_sim_dt.value())))
=======
        self.canvas.ax_y.set_xlim(0, 10)
        self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self.sim_timer.start(int(max(1, self.sb_sim_dt.value())))
        self._on_sim_tick()  # tick imediato
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

    def on_sim_stop_clicked(self):
        self.sim_running = False
        try: self.sim_timer.stop()
        except Exception: pass

    def _on_sim_tick(self):
<<<<<<< HEAD
        if not self.sim_running: return
        dt = self.sim_dt
        if len(self.sim_delay_buf) == 0:
            u_delay = self.sim_u
        else:
            u_delay = self.sim_delay_buf[0]
            self.sim_delay_buf.append(self.sim_u)
            self.sim_delay_buf.popleft()
        dydt = (-self.sim_y + self.sim_Kp * u_delay) / self.sim_tau if self.sim_tau > 0 else 0.0
        self.sim_y += dydt * dt; self.sim_t += dt
=======
        if not self.sim_running:
            return

        # Δt REAL do simulador
        wall_now = time.monotonic()
        if self._sim_last_wall_t is None:
            self._sim_last_wall_t = wall_now
        dt = wall_now - self._sim_last_wall_t
        # proteção contra hibernação/pausas longas
        if dt < 0.0: dt = self.sim_dt
        if dt > 2.0: dt = self.sim_dt
        self._sim_last_wall_t = wall_now

        # tempo simulado relativo
        if self._sim_wall_t0 is None:
            self._sim_wall_t0 = wall_now
        self.sim_t = wall_now - self._sim_wall_t0

        # registra amostra atual em (t,u)
        if not self.sim_hist or self.sim_t >= self.sim_hist[-1][0]:
            self.sim_hist.append((self.sim_t, float(self.sim_u)))
        else:
            self.sim_hist.append((self.sim_hist[-1][0] + 1e-12, float(self.sim_u)))

        # atraso puro contínuo para u
        u_delay = self._u_sim_at(self.sim_t - self.sim_L) if self.sim_L > 0 else float(self.sim_u)

        # FOPDT: dy/dt = (-y + Kp*u_delay) / tau  (integra com Δt REAL)
        dydt = 0.0 if self.sim_tau <= 0 else (-self.sim_y + self.sim_Kp * u_delay) / self.sim_tau
        self.sim_y += dydt * dt

        # plota
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642
        self.buff.append(self.sim_t, y=self.sim_y, u=self.sim_u)
        self._auto_axes(); self._safe_redraw()

    # +A/-A
    def _on_plus_minus_A(self, sgn: int):
        A = float(self.ds_A.value()); delta = sgn * A
        if self.tabs_adj.currentWidget() is self.tab_sim:
            self.sim_u = float(self.sim_u) + float(delta)
        else:
            if not hasattr(self, "rv_u") or self.rv_u is None: return
            cur_h = self._read_sync(self.rv_u)
            if cur_h is None: cur_h = 0.0
            cur_p = _u_human_to_percent(cur_h)
            new_p = float(cur_p) + float(delta)
            new_h = _u_percent_to_human(new_p)
            self._write_sync(self.rv_u, new_h)

    # ======================= Leituras & callbacks =======================
    def _read_sync(self, rv):
        if rv is None: return None
        for m in ("read_sync", "read", "value", "getValue"):
            f = getattr(rv, m, None)
            if not callable(f): continue
            if inspect.iscoroutinefunction(f):  # não criar coroutine
                continue
            try:
                if m == "getValue":
                    try: val = f(None)
                    except TypeError: val = f()
                else:
                    val = f()
            except Exception:
                continue
            if inspect.isawaitable(val):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running(): return None
                    return float(loop.run_until_complete(val))
                except Exception:
                    return None
            try: return float(val)
            except Exception: pass
        for attr in ("humanValue", "value", "_value"):
            try:
                val = getattr(rv, attr)
                return float(val)
            except Exception: pass
        return None

    def _write_sync(self, rv, value: float) -> bool:
        if rv is None: return False
        candidates = [
            ("setValue", (value, True)),
            ("setValue", (value,)),
            ("write", (value,)),
            ("write_sync", (value,)),
            ("set", (value,)),
            ("update", (value,)),
            ("setHumanValue", (value,)),
            ("set_value", (value,)),
            ("put", (value,)),
        ]
        for name, args in candidates:
            f = getattr(rv, name, None)
            if callable(f) and not inspect.iscoroutinefunction(f):
                try: f(*args); return True
                except Exception: continue
        for attr in ("humanValue", "value", "_value"):
            try: setattr(rv, attr, float(value)); return True
            except Exception: pass
        return False

    def _on_u_external(self, *args, **kwargs):
        val = self._read_sync(self.rv_u)
        if val is not None:
            self._last_u_percent = _u_human_to_percent(val)

    def _on_y_external(self, *args, **kwargs):
        val = self._read_sync(self.rv_y)
        if val is not None:
            self._last_y = float(val)

    def _on_real_tick(self):
        if not self.running or self.t0 is None: return
        if self._last_u_percent is None and hasattr(self, "rv_u"):
            cur_h = self._read_sync(self.rv_u)
            if cur_h is not None: self._last_u_percent = _u_human_to_percent(cur_h)
        if self._last_y is None and hasattr(self, "rv_y"):
            cur_y = self._read_sync(self.rv_y)
            if cur_y is not None: self._last_y = float(cur_y)
        u_val = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        y_val = 0.0 if self._last_y is None else float(self._last_y)
        t = time.monotonic() - self.t0
        self.buff.append(t, y=y_val, u=u_val)
        self._auto_axes(); self._redraw()

    # ======================= Eventos de janela =======================
    def showEvent(self, e):
        super().showEvent(e)
        if self.running:
            self.sync_running_state(True)

    def hideEvent(self, e):
        try:
            if hasattr(self, "real_timer"):
                self.real_timer.stop()
        except Exception:
            pass
        super().hideEvent(e)

    # ======================= Desenho =======================
    def _ensure_lines(self):
        try:
            if getattr(self.canvas, "line_y", None) is None:
                self.canvas.line_y, = self.canvas.ax_y.plot([], [], label="PV (y)")
            if getattr(self.canvas, "line_u", None) is None:
                self.canvas.line_u, = self.canvas.ax_u.plot([], [], label="Entrada (u)", color="orange")
            self.canvas.ax_y.legend(loc="upper right")
        except Exception:
            pass

    def _compute_padded_limits(self, vmin: float, vmax: float, min_span: float = 1.0, pad_ratio: float = 0.05):
        if vmax < vmin: vmin, vmax = vmax, vmin
        span = vmax - vmin
        if span < 1e-9:
            span = max(min_span, abs(vmax) if abs(vmax) > 0 else 1.0)
            vmin = vmin - span * 0.5; vmax = vmax + span * 0.5
        pad = max(1e-12, pad_ratio * (vmax - vmin))
        return vmin - pad, vmax + pad

    def _auto_axes(self):
<<<<<<< HEAD
        if len(self.buff.t) < 2: return
        tmin, tmax = self.buff.t[0], self.buff.t[-1]
        xmin, xmax = self._compute_padded_limits(tmin, tmax, min_span=1.0, pad_ratio=0.05)
        if xmin < 0: xmin = 0.0
        self.canvas.ax_y.set_xlim(xmin, xmax)
=======
        n = len(self.buff.t)
        if n == 0:
            return
        if n == 1:
            t0 = self.buff.t[0]
            self.canvas.ax_y.set_xlim(t0, t0 + 1e-6)  # evita singularidade
        else:
            tmin, tmax = self.buff.t[0], self.buff.t[-1]
            if tmax <= tmin:
                tmax = tmin + 1e-6
            self.canvas.ax_y.set_xlim(tmin, tmax)
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642

        y_min, y_max = min(self.buff.y), max(self.buff.y)
        y_lo, y_hi = self._compute_padded_limits(y_min, y_max, min_span=1.0, pad_ratio=0.05)
        self.canvas.ax_y.set_ylim(y_lo, y_hi)

        u_min, u_max = min(self.buff.u), max(self.buff.u)
        u_lo, u_hi = self._compute_padded_limits(u_min, u_max, min_span=1.0, pad_ratio=0.05)
        self.canvas.ax_u.set_ylim(u_lo, u_hi)

    def _safe_redraw(self):
        if not self._ready_to_paint:
            return
        try:
            self._redraw()
        except Exception:
            pass

    def _redraw(self):
        self.canvas.line_y.set_data(self.buff.t, self.buff.y)
        self.canvas.line_u.set_data(self.buff.t, self.buff.u)
        if hasattr(self.canvas, "request_draw"):
            self.canvas.request_draw()
        else:
            self.canvas.draw_idle()

    # ======================= Compatibilidade MAIN =======================
    def sync_running_state(self, running: bool):
<<<<<<< HEAD
        """Mantém o viewer em sincronia com o MAIN.
        Se running=True e a janela abriu depois do Start, semeia e começa a desenhar imediatamente.
        """
        self.running = bool(running)
        self._set_running_visual(self.running)
        if self.running:
            try:
                self.on_connect_clicked()
            except Exception:
                pass
            if self.t0 is None or len(self.buff.t) == 0:
                cur_h_u = self._read_sync(self.rv_u)
                cur_y   = self._read_sync(self.rv_y)
                if cur_h_u is None: cur_h_u = self._last_u_percent if self._last_u_percent is not None else 0.0
                if cur_y   is None: cur_y   = self._last_y if self._last_y is not None else 0.0
                self._last_u_percent = _u_human_to_percent(cur_h_u)
                self._last_y = float(cur_y)
                self.t0 = time.monotonic()
                self.buff.clear()
                self.buff.append(0.0, y=self._last_y, u=self._last_u_percent)
                self._auto_axes(); self._redraw()
            try:
                self.real_timer.start(int(max(1, self.sb_sim_dt.value())))
            except Exception:
                self.real_timer.start(50)
        else:
            try:
                self.real_timer.stop()
            except Exception:
                pass

    def sync_reset(self):
        y0 = 0.0 if self._last_y is None else float(self._last_y)
        u0 = 0.0 if self._last_u_percent is None else float(self._last_u_percent)
        self.buff.clear(); self.t0 = time.monotonic()
        self.buff.append(0.0, y=y0, u=u0)
        self._auto_axes(); self._redraw()
=======
        """Se o main disser que está rodando, inicia; se disser que parou, para (e espelha visual)."""
        if running and not self.running:
            self._start_real_mode()
        elif (not running) and self.running:
            self._stop_real_mode()
        else:
            self._set_running_visual(running)

    def sync_reset(self):
        self.on_reset_clicked()

    # -------------------------- StepTimer sincronizado --------------------------
    def _on_step_timer_changed(self, v: int):
        """Mantém todos os relógios sincronizados ao StepTimer [ms]."""
        ms = int(max(1, v))
        try:
            self.real_timer.setInterval(ms)
        except Exception:
            pass
        try:
            if self.sim_running:
                self.sim_dt = ms / 1000.0
                self.sim_timer.setInterval(ms)
                self._sim_last_wall_t = time.monotonic()
        except Exception:
            pass
        try:
            if self.simul_tf is not None and hasattr(self.simul_tf, 'set_step_time_ms'):
                self.simul_tf.set_step_time_ms(ms)
        except Exception as e:
            print("[PV] set_step_time_ms falhou:", e)


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()
>>>>>>> 5bedd0c01be58f68c39f517353d2b37827975642


# Exec isolado desativado
if __name__ == "__main__":
    pass
