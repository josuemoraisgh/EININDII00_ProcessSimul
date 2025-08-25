
from typing import Optional, Any, Tuple

# Qt compat
# Qt compat
try:
    from PySide6.QtCore import Qt, Signal, Slot
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
        QGroupBox, QPushButton, QTabWidget
    )
except Exception:
    # Fallback para PyQt5 (opcional)
    from PyQt5.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
        QGroupBox, QPushButton, QTabWidget
    )


from .ui_config import UIConfig
from .plotting.canvas import MplCanvas, PVToolbar
from .model import PlantModel
from .controller import PlantController

class PlantViewerWindow(QMainWindow):
    """VIEW: constrói UI e delega lógica ao Controller e Model."""
    simStartStop = Signal(bool)
    simReset = Signal()

    # ---- Toolbar hooks usados pela PVToolbar ----
    def set_cursor_mode(self, mode: Optional[str]):
        try: self.canvas.set_cursor_mode(mode)
        except Exception: pass

    def set_kp_mode(self, enabled: bool):
        try: self.canvas.set_kp_mode(bool(enabled))
        except Exception: pass

    def on_clear_cursors_clicked(self):
        try: self.canvas.clear_cursors()
        except Exception: pass

    def on_reset_toolbar(self):
        try: self.canvas.clear_overlays()
        except Exception: pass
        try: self.canvas.clear_cursors()
        except Exception: pass
        self.sync_reset()

    def __init__(self, react_factory=None, factory=None, simul_tf=None, parent=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("Planta (ReactVar) — Viewer")
        self.resize(1200, 700)

        self.factory = react_factory or factory
        self.simul_tf = simul_tf
        self.mb_port = kwargs.get("mb_port", kwargs.get("MB_PORT", 502))

        # MVC
        self.model = PlantModel(self.factory)
        self.canvas = MplCanvas(self)
        self.ctrl = PlantController(self.model, self.canvas, self)

        # sinais passthrough
        self.ctrl.simStartStop.connect(self.simStartStop)
        self.ctrl.simReset.connect(self.simReset)

        self._build_ui()
        self._configure_axis_formatters()
        self._populate_from_factory()
        self.model.restore_selection(self.cb_u_row, self.cb_y_col)
        self.on_connect_clicked()  # auto-connect + seed
        self._set_running_visual(False)

    # ======================= UI =======================
    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        main = QHBoxLayout(central)

        # Plot e toolbar (TOP)
        left = QVBoxLayout()
        self._ensure_lines()
        try: self.canvas.ax_u.set_ylabel('Entrada (u)')
        except Exception: pass
        self.toolbar = PVToolbar(self.canvas, self)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas, 1)

        # Painel lateral
        right_container = QWidget(self); right_container.setFixedWidth(UIConfig.CONTROL_PANEL_WIDTH)
        right = QVBoxLayout(right_container)

        # Ajuste (colapsado)
        g_adj = QGroupBox("Ajuste")
        g_adj.setCheckable(True)
        g_adj.setChecked(True)
        lay_adj = QVBoxLayout(g_adj); 
        self._adj_inner = QWidget(g_adj); 
        adj_form = QFormLayout(self._adj_inner)

        self.sb_sim_dt = QSpinBox(); self.sb_sim_dt.setRange(1, 5000); self.sb_sim_dt.setValue(50)
        adj_form.addRow("StepTimer [ms]:", self.sb_sim_dt)

        self.tabs_adj = QTabWidget(); adj_form.addRow(self.tabs_adj)

        # Aba Real
        self.tab_real = QWidget(); real_lay = QVBoxLayout(self.tab_real)
        from PySide6.QtWidgets import QLabel as _QLabel
        row_port = QHBoxLayout(); row_port.addWidget(_QLabel("MB_PORT:"))
        self.cb_mb_port = QComboBox(); self.cb_mb_port.addItems([str(self.mb_port)])
        row_port.addWidget(self.cb_mb_port, 1)
        real_lay.addLayout(row_port)

        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop")
        self.btn_start.setCheckable(True); self.btn_stop.setCheckable(True)
        self.btn_reset = QPushButton("reset"); self._style_btn_reset_idle()

        self.btn_start.pressed.connect(lambda: self.btn_start.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_stop.pressed.connect(lambda: self.btn_stop.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.pressed.connect(lambda: self.btn_reset.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.btn_reset.released.connect(self._style_btn_reset_idle)

        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)

        real_lay.addWidget(self.btn_start); real_lay.addWidget(self.btn_stop); real_lay.addWidget(self.btn_reset)
        
        g_sel = QGroupBox("Seleção de Variáveis Reais", self.tab_real)
        lay_sel = QFormLayout(g_sel)
        self.cb_u_row = QComboBox(); self.cb_y_col = QComboBox()
        lay_sel.addRow("Entrada (u):", self.cb_u_row)
        lay_sel.addRow("Saída (y):",   self.cb_y_col)
        self.lbl_conn = QLabel("Conexão: —")
        lay_sel.addRow(self.lbl_conn)
        real_lay.addWidget(g_sel)

        self.tabs_adj.addTab(self.tab_real, "Real")

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
        self.tabs_adj.addTab(self.tab_sim, "Simulado")

        lay_adj.addWidget(self._adj_inner)
        right.addWidget(g_adj)

        # Entrada (u): A, +A, -A
        g_u = QGroupBox("Entrada (u)"); ly_u = QFormLayout(g_u)
        row = QHBoxLayout()
        self.ds_A = QDoubleSpinBox(); self.ds_A.setDecimals(3); self.ds_A.setRange(-1e6, 1e6); self.ds_A.setValue(1.000)
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
        self._adj_inner.setVisible(g_adj.isChecked())
        # self._adj_inner.setVisible(False)

        # Interações
        self.cb_u_row.currentIndexChanged.connect(lambda *_: self.on_connect_clicked())
        self.cb_y_col.currentIndexChanged.connect(lambda *_: self.on_connect_clicked())
        self.sb_sim_dt.valueChanged.connect(self._on_dt_changed)

    def _style_btn_reset_idle(self):
        self.btn_reset.setStyleSheet("background:yellow; color:black; font-weight:bold;")

    # ======================= Formatter/axes =======================
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
    def _populate_from_factory(self):
        u_items, y_items = self.model.list_candidates()
        self.cb_u_row.blockSignals(True); self.cb_y_col.blockSignals(True)
        self.cb_u_row.clear(); self.cb_u_row.addItems(u_items)
        self.cb_y_col.clear(); self.cb_y_col.addItems(y_items)
        self.cb_u_row.blockSignals(False); self.cb_y_col.blockSignals(False)

    def on_connect_clicked(self):
        u_name = self.cb_u_row.currentText().strip()
        y_name = self.cb_y_col.currentText().strip()
        self.rv_u, self.rv_y = self.model.connect_vars(u_name, y_name)

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
        self.model.persist_selection(u_name, y_name)

        # Seed initial buffer if already running
        if self.ctrl.running:
            try:
                cur_h = self._read_sync(self.rv_u)
                cur_y = self._read_sync(self.rv_y)
                if cur_h is not None: self.ctrl._last_u_percent = self.model.human_to_percent(cur_h)
                if cur_y is not None: self.ctrl._last_y = float(cur_y)
            except Exception:
                pass
            if self.ctrl.t0 is None or len(self.ctrl.buff.t) == 0:
                import time
                self.ctrl.t0 = time.monotonic()
                self.ctrl.buff.clear()
                y0 = 0.0 if self.ctrl._last_y is None else float(self.ctrl._last_y)
                u0 = 0.0 if self.ctrl._last_u_percent is None else float(self.ctrl._last_u_percent)
                self.ctrl.buff.append(0.0, y=y0, u=u0)
            self.ctrl._auto_axes(); self.ctrl._redraw()

    # proxy for controller's private read (kept for compat)
    def _read_sync(self, rv): 
        return self.ctrl._read_sync(rv)

    # ======================= Start/Stop/Reset (Real) =======================
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
        if self.ctrl.running: return
        self.ctrl.start_real(self.sb_sim_dt.value(), self.rv_u, self.rv_y)
        self._set_running_visual(True)

    def on_stop_clicked(self):
        self.ctrl.stop_real()
        self._set_running_visual(False)

    def on_reset_clicked(self):
        self.on_stop_clicked()
        self.ctrl.reset()

    # ======================= Simulador =======================
    def _on_dt_changed(self, v):
        iv = int(max(1, v))
        if self.ctrl.running: self.ctrl.real_timer.setInterval(iv)
        if self.ctrl.sim.running: self.ctrl.sim_timer.setInterval(iv)

    def on_sim_start_clicked(self):
        Kp = float(self.sb_sim_Kp.value())
        tau= float(self.sb_sim_tau.value())
        L  = float(self.sb_sim_L.value())
        dt = float(self.sb_sim_dt.value()) / 1000.0
        y0 = self.ctrl.buff.y[-1] if self.ctrl.buff.y else 0.0
        self.ctrl.sim_start(Kp, tau, L, dt, self.sb_sim_dt.value(), y0)

    def on_sim_stop_clicked(self):
        self.ctrl.sim_stop()

    def _on_plus_minus_A(self, sgn: int):
        A = float(self.ds_A.value()); delta = sgn * A
        self.ctrl.sim_plus_minus_A(delta, rv_u=self.rv_u, is_sim_tab=(self.tabs_adj.currentWidget() is self.tab_sim))

    # ======================= Leituras & callbacks =======================
    def _on_u_external(self, *args, **kwargs):
        val = self._read_sync(self.rv_u)
        if val is not None: self.ctrl.cache_external_u(val)

    def _on_y_external(self, *args, **kwargs):
        val = self._read_sync(self.rv_y)
        if val is not None: self.ctrl.cache_external_y(val)

    # ======================= Eventos de janela =======================
    def showEvent(self, e):
        super().showEvent(e)
        if self.ctrl.running:
            self.sync_running_state(True)

    def hideEvent(self, e):
        try: self.ctrl.real_timer.stop()
        except Exception: pass
        super().hideEvent(e)

    # ======================= Desenho (compat) =======================
    def _ensure_lines(self):
        try:
            if getattr(self.canvas, "line_y", None) is None:
                self.canvas.line_y, = self.canvas.ax_y.plot([], [], label="PV (y)")
            if getattr(self.canvas, "line_u", None) is None:
                self.canvas.line_u, = self.canvas.ax_u.plot([], [], label="Entrada (u)", color="orange")
            self.canvas.ax_y.legend(loc="upper right")
        except Exception:
            pass

    # ======================= Compat com MAIN antigo =======================
    def sync_running_state(self, running: bool):
        self.ctrl.running = bool(running)
        self._set_running_visual(self.ctrl.running)
        if self.ctrl.running:
            try: self.on_connect_clicked()
            except Exception: pass
            if self.ctrl.t0 is None or len(self.ctrl.buff.t) == 0:
                cur_h_u = self._read_sync(self.rv_u)
                cur_y   = self._read_sync(self.rv_y)
                if cur_h_u is None: cur_h_u = self.ctrl._last_u_percent if self.ctrl._last_u_percent is not None else 0.0
                if cur_y   is None: cur_y   = self.ctrl._last_y if self.ctrl._last_y is not None else 0.0
                self.ctrl._last_u_percent = self.model.human_to_percent(cur_h_u)
                self.ctrl._last_y = float(cur_y)
                import time
                self.ctrl.t0 = time.monotonic()
                self.ctrl.buff.clear()
                self.ctrl.buff.append(0.0, y=self.ctrl._last_y, u=self.ctrl._last_u_percent)
                self.ctrl._auto_axes(); self.ctrl._redraw()
            try:
                self.ctrl.real_timer.start(int(max(1, self.sb_sim_dt.value())))
            except Exception:
                self.ctrl.real_timer.start(50)
        else:
            try: self.ctrl.real_timer.stop()
            except Exception: pass

    def sync_reset(self):
        y0 = 0.0 if self.ctrl._last_y is None else float(self.ctrl._last_y)
        u0 = 0.0 if self.ctrl._last_u_percent is None else float(self.ctrl._last_u_percent)
        self.ctrl.buff.clear(); import time; self.ctrl.t0 = time.monotonic()
        self.ctrl.buff.append(0.0, y=y0, u=u0)
        self.ctrl._auto_axes(); self.ctrl._redraw()
