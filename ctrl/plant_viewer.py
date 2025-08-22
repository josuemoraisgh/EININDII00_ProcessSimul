
"""
Plant Viewer (ReactVar) • PySide6

Regras implementadas:
• Se estiver em Start, o gráfico desenha imediatamente as variáveis selecionadas.
• Se a janela abrir com o sistema em Start, ela detecta e começa a pintar.
• Ao trocar a variável (u ou y) durante a execução, o traçado segue contínuo,
  sem apagar, com uma linha vertical suave marcando a troca.
• "Limpar Tela" replanta t=0 com os últimos valores reais de y e u (sem saltos).
• Modo Simulado usa atraso puro contínuo (histórico com timestamp + interpolação),
  agora com integração por Δt real (sem depender do período nominal do QTimer).
"""

from __future__ import annotations

import time
from typing import Optional
from collections import deque

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


# -------------------------- Conversões u: human (0..65535) <-> percent (0..100) --------------------------
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


class PlantViewerWindow(QMainWindow):
    simStartStop = QtCore.Signal(bool)
    simReset = QtCore.Signal()

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
        self.sb_sim_dt.valueChanged.connect(lambda v: self.real_timer.setInterval(int(max(1, v))))

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

    def on_clear_cursors_clicked(self):
        self.canvas.clear_cursors()

    def on_reset_toolbar(self):
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

    # ----------------------- Factory -> Combos -----------------------
    def _populate_from_factory(self):
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
        self.simStartStop.emit(False)
        try:
            self.real_timer.stop()
        except Exception:
            pass

    def on_reset_clicked(self):
        """
        Botão 'reset': limpa visuais e REPLANTA ponto inicial com y/u atuais.
        Mantém timers conforme estado (rodando ou parado).
        """
        try: self.canvas.clear_overlays()
        except Exception: pass
        self._seed_after_clear()
        self.simReset.emit()
        self.sim_t = 0.0

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

    def on_sim_start_clicked(self):
        self.sim_Kp = float(self.sb_sim_Kp.value())
        self.sim_tau = float(self.sb_sim_tau.value())
        self.sim_L   = float(self.sb_sim_L.value())
        self.sim_dt  = float(self.sb_sim_dt.value()) / 1000.0  # ms → s

        self._init_sim_delay_hist()  # atraso puro contínuo

        # reseta relógio do simulador (usa tempo absoluto para Δt)
        wall = time.monotonic()
        self._sim_wall_t0 = wall
        self._sim_last_wall_t = wall

        self.sim_running = True
        self.sim_t = 0.0
        self.sim_y = self.buff.y[-1] if self.buff.y else 0.0
        self.t0 = wall  # eixo x do gráfico alinha com o relógio do simulador
        self.buff.clear()
        self.canvas.ax_y.set_xlim(0, 10)
        self.canvas.ax_y.set_ylim(-1, 1)
        self.canvas.ax_u.set_ylim(-1, 1)
        self.sim_timer.start(int(max(1, self.sb_sim_dt.value())))
        self._on_sim_tick()  # tick imediato

    def on_sim_stop_clicked(self):
        self.sim_running = False
        self.sim_timer.stop()

    def _on_sim_tick(self):
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
        self.buff.append(self.sim_t, y=self.sim_y, u=self.sim_u)
        self._auto_axes(); self._safe_redraw()

    # -------------------------- Desenho --------------------------
    def _auto_axes(self):
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

    # ----------------------- Compatibilidade (espelhamento) -----------------------
    def sync_running_state(self, running: bool):
        """Se o main disser que está rodando, inicia; se disser que parou, para (e espelha visual)."""
        if running and not self.running:
            self._start_real_mode()
        elif (not running) and self.running:
            self._stop_real_mode()
        else:
            self._set_running_visual(running)

    def sync_reset(self):
        self.on_reset_clicked()


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
