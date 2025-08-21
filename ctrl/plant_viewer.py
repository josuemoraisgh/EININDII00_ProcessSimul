""""
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
• Seleção de Variáveis Reais: apenas dois seletores visíveis:
    - Entrada (u): linha/dispositivo da tabela MODBUS (coluna fixa: CLP100)
    - Saída (y):   coluna/variável da tabela HART (linha fixa: PROCESS_VARIABLE)
"""

from __future__ import annotations

import time
from typing import Optional
from collections import deque

from PySide6 import QtCore

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

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QMainWindow, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QComboBox, QGroupBox, QPushButton, QSpinBox, QLabel, QTabWidget
from ctrl.mpl_canvas import *
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


        # >>> NOVO: Modo Real — cache e timer de polling
        self._last_u_percent: Optional[float] = None
        self._last_y: Optional[float] = None
        self.real_timer = QtCore.QTimer(self)
        self.real_timer.timeout.connect(self._on_real_tick)
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

        # Seleção de variáveis (apenas 2 seletores visíveis)
        g_sel = QGroupBox("Seleção de Variáveis Reais")
        lay = QFormLayout(g_sel)
        self.cb_u_row = QComboBox()  # Entrada (u): MODBUS rows
        self.cb_y_col = QComboBox()  # Saída (y):  HART columns
        lay.addRow("Entrada (u):", self.cb_u_row)
        lay.addRow("Saída (y):", self.cb_y_col)
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

        # >>> NOVO: Período global (Real & Sim) fora das abas
        w_dt = QWidget(self); lay_dt = QFormLayout(w_dt)
        self.sb_sim_dt = QSpinBox(); self.sb_sim_dt.setRange(1, 2000); self.sb_sim_dt.setValue(50)  # ms
        lay_dt.addRow("Período de atualização [ms] (Real & Sim):", self.sb_sim_dt)
        adj_lay.addWidget(w_dt)

        adj_lay.addWidget(self.tabs_adj)
        # Entrada (u): A, +A, -A (último bloco)
        g_u = QGroupBox("Entrada (u)")
        lay_u = QHBoxLayout(g_u)
        self.sb_A = QDoubleSpinBox(); self.sb_A.setDecimals(3); self.sb_A.setRange(-1e9, 1e9); self.sb_A.setValue(1.0); self.sb_A.setButtonSymbols(QAbstractSpinBox.NoButtons)
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


        # >>> NOVO: manter timer do Real sincronizado ao SpinBox
        try:
            self.sb_sim_dt.valueChanged.connect(lambda v: self.real_timer.setInterval(int(max(1, v))))
        except Exception:
            pass
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
        # Limpar Tela: apenas limpa os traçados e sobreposições; não para a simulação nem reseta eixos.
        # 1) Limpa buffers e linhas
        self.buff.clear()
        self.canvas.line_y.set_data([], [])
        self.canvas.line_u.set_data([], [])
        # 2) Limpa overlays/cursores/Kp
        try:
            self.canvas.clear_overlays()
        except Exception:
            pass
        try:
            self.canvas.clear_cursors()
        except Exception:
            pass
        # 3) Mantém limites atuais: não altera ax.set_xlim/ylim; apenas redesenha
        self._redraw()

        # Desmarca botões de V/H/Kp (modo de edição), pois os overlays foram limpos
        self.toolbar.act_v.setChecked(False)
        self.toolbar.act_h.setChecked(False)
        self.toolbar.act_kp.setChecked(False)

        self.t0 = time.monotonic()
        self.sim_t = 0.0

    # ----------------------- Factory -> Combos -----------------------
    def _populate_from_factory(self):
        """Carrega apenas dois seletores:
        - Entrada (u): linhas de MODBUS (coluna fixa 'CLP100')
        - Saída (y): colunas de HART (linha fixa 'PROCESS_VARIABLE'), PULANDO as 2 primeiras colunas.
        """
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
                # >>> Ajuste pedido: começar a lista a partir do 3º termo
                if len(cols) > 2:
                    cols = cols[2:]
                else:
                    cols = cols[:]  # fallback caso haja 2 ou menos
                self.cb_y_col.addItems([str(c) for c in cols])
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
        if self.running:
            return
        if not hasattr(self, "rv_u") or not hasattr(self, "rv_y"):
            self.on_connect_clicked()
            if not (hasattr(self, "rv_u") and hasattr(self, "rv_y")):
                return

        # Ler valores atuais e semear t=0 com y0/u0
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

        self.t0 = time.monotonic()
        self.buff.clear()
        self.buff.append(0.0, y=self._last_y, u=self._last_u_percent)
        self._auto_axes(); self._redraw()

        self.running = True
        self._set_running_visual(True)
        self.simStartStop.emit(True)

        # Inicia polling do modo Real com período = sb_sim_dt
        try:
            self.real_timer.start(int(max(1, self.sb_sim_dt.value())))
        except Exception:
            self.real_timer.start(50)

    def on_stop_clicked(self):
        self.running = False
        self._set_running_visual(False)
        self.simStartStop.emit(False)
        try:
            self.real_timer.stop()
        except Exception:
            pass

    def on_reset_clicked(self):
        self.on_stop_clicked()
        try:
            self.real_timer.stop()
        except Exception:
            pass
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
            # Fixos conforme pedido
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
        except Exception as e:
            print("[PV] ERRO CONNECT:", e)
            return

    # -------------------------- Entrada u (A, +A, -A) --------------------------
    def _inc_u(self, delta: float):
        if self.tabs_adj.currentWidget() is self.tab_sim:
            # Simulado: step em porcentagem diretamente
            self.sim_u = float(self.sim_u) + float(delta)
        else:
            # Real: ler human (0..65535) -> converter para percent -> somar delta(%) -> converter para human -> escrever
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
        # Cache apenas; desenho via _on_real_tick()
        self._last_u_percent = _u_human_to_percent(value)

    @Slot(float)
    def _on_y_external(self, value: float):
        # Cache apenas; desenho via _on_real_tick()
        self._last_y = float(value)
    def _on_real_tick(self):
        if not self.running or self.t0 is None:
            return
        # Se ainda não chegaram valores, tenta leitura síncrona
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
        self._auto_axes(); self._redraw()

    # -------------------------- Simulador FOPDT --------------------------
    def _init_sim_delay_buf(self):
        N = max(1, int(round(self.sim_L / self.sim_dt))) if self.sim_dt > 0 else 1
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
        # atraso puro via buffer circular
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
