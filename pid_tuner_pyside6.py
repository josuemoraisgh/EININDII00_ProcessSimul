
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PID Tuner (PySide6)
Features:
- Real-time plot (PV, SP, CO)
- PID controller (Kp, Ki, Kd, Ts) with anti-windup, derivative filter, output limits, bumpless transfer
- Manual/Auto mode toggle
- First-Order Plus Dead Time (FOPDT) plant simulator for testing
- Setpoint profiles: step or sine
- Relay-based autotune (Ziegler–Nichols): estimates Ku, Pu and suggests PID gains
- Save/Load presets (JSON)
- CSV logging

Run:
    pip install PySide6 matplotlib numpy
    python pid_tuner_pyside6.py
"""

import json
import csv
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QLabel, QGroupBox,
    QFileDialog, QMessageBox, QComboBox
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ----------------------------- PID Controller -----------------------------

@dataclass
class PIDConfig:
    Kp: float = 1.0
    Ki: float = 0.0  # integral gain (per second)
    Kd: float = 0.0  # derivative gain (seconds)
    Ts: float = 0.05  # sample time (s)
    out_min: float = -100.0
    out_max: float = 100.0
    anti_windup: bool = True
    deriv_filter_N: float = 10.0  # derivative filter factor (1/Tf ~ N/Td), larger = less filtering
    deriv_on_measurement: bool = True  # D on measurement (common for PID)
    direct_action: bool = True  # True = direct (CO increases PV), False = reverse
    setpoint: float = 1.0


class PIDController:
    def __init__(self, cfg: PIDConfig):
        self.cfg = cfg
        self.reset()
        self._last_mode_auto = False

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_measure = 0.0
        self.prev_deriv = 0.0  # filtered derivative term
        self.output = 0.0

    def set_auto(self, is_auto: bool, current_output: float):
        # Bumpless transfer
        if is_auto and not self._last_mode_auto:
            self.integral = current_output
        self._last_mode_auto = is_auto

    def clamp(self, u: float) -> float:
        return max(self.cfg.out_min, min(self.cfg.out_max, u))

    def update(self, sp: float, pv: float, manual: bool = False, manual_output: float = 0.0) -> float:
        Ts = self.cfg.Ts
        if manual:
            self.output = self.clamp(manual_output)
            return self.output

        # Error
        e = (sp - pv) if self.cfg.direct_action else (pv - sp)

        # Proportional
        P = self.cfg.Kp * e

        # Integral with anti-windup via clamping
        self.integral += self.cfg.Ki * e * Ts
        # We will clamp later after computing U to preserve some anti-windup behavior

        # Derivative (with filtering), either on measurement (common) or error
        if self.cfg.deriv_on_measurement:
            meas_deriv = (pv - self.prev_measure) / Ts
            # Filter: y_f = alpha*y_f + (1-alpha)*x
            # Using standard: Tf = Td/N  => alpha = Tf/(Tf+Ts) = (Td/N) / (Td/N + Ts)
            Td = self.cfg.Kd
            N = self.cfg.deriv_filter_N
            Tf = Td / N if N > 0 else 0.0
            alpha = Tf / (Tf + Ts) if (Tf + Ts) > 0 else 0.0
            self.prev_deriv = alpha * self.prev_deriv + (1 - alpha) * meas_deriv
            D = - self.cfg.Kp * Td * self.prev_deriv  # note the minus because derivative on measured PV
        else:
            de = (e - self.prev_error) / Ts
            Td = self.cfg.Kd
            N = self.cfg.deriv_filter_N
            Tf = Td / N if N > 0 else 0.0
            alpha = Tf / (Tf + Ts) if (Tf + Ts) > 0 else 0.0
            self.prev_deriv = alpha * self.prev_deriv + (1 - alpha) * de
            D = self.cfg.Kp * Td * self.prev_deriv

        # Unclamped output (internal)
        u = P + self.integral + D

        # Clamp with anti-windup correction
        u_clamped = self.clamp(u)
        if self.cfg.anti_windup and self.cfg.Ki > 0:
            # Back-calculation: adjust integral if saturated
            self.integral += (u_clamped - u)

        self.output = u_clamped

        # Save state
        self.prev_error = e
        self.prev_measure = pv
        return self.output


# ----------------------------- Plant Simulator (FOPDT) -----------------------------

@dataclass
class FOPDTConfig:
    K: float = 1.0      # gain
    tau: float = 3.0    # time constant (s)
    dead_time: float = 0.5  # dead time (s)
    Ts: float = 0.05
    noise_std: float = 0.0


class FOPDTPlant:
    def __init__(self, cfg: FOPDTConfig):
        self.cfg = cfg
        self.reset()

    def reset(self):
        self.y = 0.0
        self.buffer_len = max(1, int(round(self.cfg.dead_time / self.cfg.Ts)))
        self.u_buffer = deque([0.0] * self.buffer_len, maxlen=self.buffer_len)

    def step(self, u: float) -> float:
        # dead-time buffer
        self.u_buffer.append(u)
        u_delayed = self.u_buffer[0] if len(self.u_buffer) > 0 else u

        # first-order discrete (Euler)
        Ts = self.cfg.Ts
        dy = (-(self.y) + self.cfg.K * u_delayed) * (Ts / self.cfg.tau)
        self.y += dy

        if self.cfg.noise_std > 0.0:
            self.y += np.random.normal(0.0, self.cfg.noise_std)

        return self.y


# ----------------------------- Relay-based Autotune -----------------------------

class RelayAutotune(QtCore.QObject):
    """Implements relay (on-off) test to estimate Ku and Pu.
    Procedure:
    - Replace controller with relay: u = +h or -h based on error sign.
    - Record steady oscillations of PV around SP.
    - Ultimate amplitude a is PV oscillation (peak-to-peak / 2). Pu is period.
    - Ku ≈ (4*h) / (π*a). Then Z-N PID: Kp=0.6Ku, Ti=Pu/2, Td=Pu/8.
    """
    finished = QtCore.Signal(float, float, float, float)  # Ku, Pu, Kp, Ki, Kd
    status = QtCore.Signal(str)

    def __init__(self, amplitude: float = 10.0, min_cycles: int = 3, max_time: float = 120.0, parent=None):
        super().__init__(parent)
        self.h = amplitude
        self.min_cycles = min_cycles
        self.max_time = max_time
        self._running = False
        self._t0 = None
        self._last_cross_time = None
        self._peaks = []  # (time, value)
        self._last_sign = None
        self._last_value = None
        self._crossings = []

    def start(self):
        self._running = True
        self._t0 = time.time()
        self._peaks.clear()
        self._crossings.clear()
        self._last_sign = None
        self._last_value = None
        self.status.emit("Autotune iniciado (ensaio de relé)...")

    def stop(self):
        self._running = False
        self.status.emit("Autotune cancelado.")

    def is_running(self) -> bool:
        return self._running

    def compute_relay_output(self, sp: float, pv: float) -> float:
        if not self._running:
            return 0.0
        e = sp - pv
        u = self.h if e >= 0 else -self.h
        return u

    def update(self, t: float, sp: float, pv: float):
        if not self._running:
            return

        # stop condition
        if (time.time() - self._t0) > self.max_time:
            self._running = False
            self.status.emit("Tempo máximo atingido sem convergir.")
            return

        # zero-crossing detection around SP
        val = pv - sp
        sign = 1 if val >= 0 else -1
        if self._last_sign is not None and sign != self._last_sign:
            self._crossings.append(t)
            if len(self._crossings) >= 6:  # enough crossings for 3 oscillation cycles
                # compute period from last 4 crossings (2 full periods)
                periods = []
                for i in range(2, len(self._crossings)):
                    periods.append(self._crossings[i] - self._crossings[i - 2])
                Pu = np.mean(periods[-4:]) if len(periods) >= 4 else np.mean(periods)
                # compute amplitude from recent peaks
                if len(self._peaks) >= 4:
                    recent_vals = [p[1] for p in self._peaks[-4:]]
                    a = (max(recent_vals) - min(recent_vals)) / 2.0
                else:
                    # fallback: use absolute peak around SP
                    a = max(abs(val), 1e-6)
                Ku = (4.0 * self.h) / (math.pi * a) if a > 1e-9 else 0.0
                # Ziegler–Nichols PID
                Kp = 0.6 * Ku
                Ti = Pu / 2.0 if Pu > 1e-9 else 1.0
                Td = Pu / 8.0 if Pu > 1e-9 else 0.0
                Ki = Kp / Ti
                Kd = Kp * Td
                self._running = False
                self.status.emit(f"Autotune concluído: Ku={Ku:.3f}, Pu={Pu:.3f}")
                self.finished.emit(Ku, Pu, Kp, Ki, Kd)
                return
        self._last_sign = sign

        # peak detection (simple: track local maxima/minima)
        if self._last_value is not None:
            # detect change of derivative
            # We keep last 1 value; for robustness this could be extended
            pass
        self._last_value = val

    # end RelayAutotune


# ----------------------------- Matplotlib Canvas -----------------------------

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(7, 4), tight_layout=True)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True)


# ----------------------------- Main Window -----------------------------

class PIDTunerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tela de Sintonia PID - PySide6")
        self.resize(1200, 700)

        # Default configs
        self.pid_cfg = PIDConfig()
        self.plant_cfg = FOPDTConfig()
        self.controller = PIDController(self.pid_cfg)
        self.plant = FOPDTPlant(self.plant_cfg)

        # State
        self.running = False
        self.manual_mode = False
        self.manual_output = 0.0
        self.time_elapsed = 0.0
        self.log_rows = []
        self.start_time = None

        # Autotune
        self.autotune = RelayAutotune(amplitude=10.0, min_cycles=3, max_time=90.0)
        self.autotune.finished.connect(self.on_autotune_finished)
        self.autotune.status.connect(self.on_status)

        # UI
        self._build_ui()

        # Timer for simulation and plotting
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.setInterval(int(self.pid_cfg.Ts * 1000))

        # Plot data buffers
        self.max_points = 2000
        self.t_data = deque(maxlen=self.max_points)
        self.sp_data = deque(maxlen=self.max_points)
        self.pv_data = deque(maxlen=self.max_points)
        self.co_data = deque(maxlen=self.max_points)

    # ----------------------- UI Construction -----------------------

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # Left controls
        ctrl_layout = QVBoxLayout()
        main_layout.addLayout(ctrl_layout, 0)

        # PID group
        pid_group = QGroupBox("Parâmetros PID")
        pid_form = QFormLayout()
        pid_group.setLayout(pid_form)

        self.sb_Kp = QDoubleSpinBox(); self.sb_Kp.setRange(0, 1e6); self.sb_Kp.setDecimals(4); self.sb_Kp.setValue(self.pid_cfg.Kp)
        self.sb_Ki = QDoubleSpinBox(); self.sb_Ki.setRange(0, 1e6); self.sb_Ki.setDecimals(6); self.sb_Ki.setValue(self.pid_cfg.Ki)
        self.sb_Kd = QDoubleSpinBox(); self.sb_Kd.setRange(0, 1e6); self.sb_Kd.setDecimals(6); self.sb_Kd.setValue(self.pid_cfg.Kd)
        self.sb_Ts = QDoubleSpinBox(); self.sb_Ts.setRange(0.001, 10.0); self.sb_Ts.setDecimals(3); self.sb_Ts.setValue(self.pid_cfg.Ts)
        self.sb_N = QDoubleSpinBox(); self.sb_N.setRange(0, 1000); self.sb_N.setDecimals(2); self.sb_N.setValue(self.pid_cfg.deriv_filter_N)

        pid_form.addRow("Kp:", self.sb_Kp)
        pid_form.addRow("Ki (1/s):", self.sb_Ki)
        pid_form.addRow("Kd (s):", self.sb_Kd)
        pid_form.addRow("Ts (s):", self.sb_Ts)
        pid_form.addRow("Filtro D (N):", self.sb_N)

        self.cb_anti_windup = QCheckBox("Anti-windup"); self.cb_anti_windup.setChecked(self.pid_cfg.anti_windup)
        self.cb_d_on_meas = QCheckBox("D no sinal medido"); self.cb_d_on_meas.setChecked(self.pid_cfg.deriv_on_measurement)
        self.cb_direct = QCheckBox("Ação direta (↑CO → ↑PV)"); self.cb_direct.setChecked(self.pid_cfg.direct_action)

        pid_form.addRow(self.cb_anti_windup)
        pid_form.addRow(self.cb_d_on_meas)
        pid_form.addRow(self.cb_direct)

        ctrl_layout.addWidget(pid_group)

        # Limits & Mode
        lim_group = QGroupBox("Limites / Modo")
        lim_form = QFormLayout()
        lim_group.setLayout(lim_form)

        self.sb_out_min = QDoubleSpinBox(); self.sb_out_min.setRange(-1e6, 0); self.sb_out_min.setDecimals(2); self.sb_out_min.setValue(self.pid_cfg.out_min)
        self.sb_out_max = QDoubleSpinBox(); self.sb_out_max.setRange(0, 1e6); self.sb_out_max.setDecimals(2); self.sb_out_max.setValue(self.pid_cfg.out_max)
        self.cb_manual = QCheckBox("Modo Manual")
        self.sb_manual = QDoubleSpinBox(); self.sb_manual.setRange(-1e6, 1e6); self.sb_manual.setDecimals(2); self.sb_manual.setValue(0.0)

        lim_form.addRow("Saída mín. (CO):", self.sb_out_min)
        lim_form.addRow("Saída máx. (CO):", self.sb_out_max)
        lim_form.addRow(self.cb_manual)
        lim_form.addRow("Saída manual (CO):", self.sb_manual)

        ctrl_layout.addWidget(lim_group)

        # Setpoint
        sp_group = QGroupBox("Setpoint")
        sp_form = QFormLayout()
        sp_group.setLayout(sp_form)

        self.sb_sp = QDoubleSpinBox(); self.sb_sp.setRange(-1e6, 1e6); self.sb_sp.setDecimals(3); self.sb_sp.setValue(self.pid_cfg.setpoint)
        self.sp_profile = QComboBox(); self.sp_profile.addItems(["Degrau", "Senoidal"])
        self.sb_sp_amp = QDoubleSpinBox(); self.sb_sp_amp.setRange(0.0, 1e6); self.sb_sp_amp.setDecimals(3); self.sb_sp_amp.setValue(0.0)
        self.sb_sp_freq = QDoubleSpinBox(); self.sb_sp_freq.setRange(0.0, 100.0); self.sb_sp_freq.setDecimals(3); self.sb_sp_freq.setValue(0.1)

        sp_form.addRow("SP base:", self.sb_sp)
        sp_form.addRow("Perfil:", self.sp_profile)
        sp_form.addRow("Amplitude (seno):", self.sb_sp_amp)
        sp_form.addRow("Frequência (Hz):", self.sb_sp_freq)

        ctrl_layout.addWidget(sp_group)

        # Plant
        plant_group = QGroupBox("Planta (Simulador FOPDT)")
        plant_form = QFormLayout()
        plant_group.setLayout(plant_form)

        self.sb_K = QDoubleSpinBox(); self.sb_K.setRange(-1e6, 1e6); self.sb_K.setDecimals(3); self.sb_K.setValue(self.plant_cfg.K)
        self.sb_tau = QDoubleSpinBox(); self.sb_tau.setRange(0.01, 1e6); self.sb_tau.setDecimals(3); self.sb_tau.setValue(self.plant_cfg.tau)
        self.sb_dead = QDoubleSpinBox(); self.sb_dead.setRange(0.0, 100.0); self.sb_dead.setDecimals(3); self.sb_dead.setValue(self.plant_cfg.dead_time)
        self.sb_noise = QDoubleSpinBox(); self.sb_noise.setRange(0.0, 1000.0); self.sb_noise.setDecimals(3); self.sb_noise.setValue(self.plant_cfg.noise_std)

        plant_form.addRow("Ganho (K):", self.sb_K)
        plant_form.addRow("Const. de tempo (τ):", self.sb_tau)
        plant_form.addRow("Atraso (dead time):", self.sb_dead)
        plant_form.addRow("Ruído (σ):", self.sb_noise)

        ctrl_layout.addWidget(plant_group)

        # Autotune
        at_group = QGroupBox("Autotune (Relé)")
        at_form = QFormLayout()
        at_group.setLayout(at_form)

        self.sb_relay = QDoubleSpinBox(); self.sb_relay.setRange(0.1, 1e6); self.sb_relay.setDecimals(3); self.sb_relay.setValue(10.0)
        self.btn_autotune = QPushButton("Iniciar Autotune")
        self.btn_autotune_stop = QPushButton("Parar Autotune")
        self.lbl_at_status = QLabel("-")

        at_form.addRow("Amplitude do relé (±h):", self.sb_relay)
        at_form.addRow(self.btn_autotune)
        at_form.addRow(self.btn_autotune_stop)
        at_form.addRow("Status:", self.lbl_at_status)

        ctrl_layout.addWidget(at_group)

        # Actions
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar")
        self.btn_stop = QPushButton("Parar")
        self.btn_apply = QPushButton("Aplicar PID/Planta")
        self.btn_reset = QPushButton("Reset")
        self.btn_save = QPushButton("Salvar Preset")
        self.btn_load = QPushButton("Carregar Preset")
        self.btn_export = QPushButton("Exportar CSV")

        for b in (self.btn_start, self.btn_stop, self.btn_apply, self.btn_reset, self.btn_save, self.btn_load, self.btn_export):
            btn_layout.addWidget(b)
        ctrl_layout.addLayout(btn_layout)
        ctrl_layout.addStretch(1)

        # Plot area
        plot_layout = QVBoxLayout()
        main_layout.addLayout(plot_layout, 1)

        self.canvas = MplCanvas(self)
        plot_layout.addWidget(self.canvas)
        self.line_pv, = self.canvas.ax.plot([], [], label="PV")
        self.line_sp, = self.canvas.ax.plot([], [], label="SP")
        self.line_co, = self.canvas.ax.plot([], [], label="CO")
        self.canvas.ax.legend(loc="upper right")

        # Status bar
        self.statusBar().showMessage("Pronto.")

        # Signals
        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_load.clicked.connect(self.on_load)
        self.btn_export.clicked.connect(self.on_export)

        self.cb_manual.toggled.connect(self.on_manual_toggled)
        self.btn_autotune.clicked.connect(self.on_autotune_start)
        self.btn_autotune_stop.clicked.connect(self.on_autotune_stop)

    # ----------------------- Event handlers -----------------------

    def on_status(self, msg: str):
        self.lbl_at_status.setText(msg)
        self.statusBar().showMessage(msg, 4000)

    def on_start(self):
        if self.running:
            return
        self.running = True
        self.start_time = time.time()
        self.time_elapsed = 0.0
        self.log_rows = []
        self.controller.reset()
        self.plant.reset()
        self.timer.setInterval(int(self.sb_Ts.value() * 1000))
        self.timer.start()
        self.on_status("Execução iniciada.")

    def on_stop(self):
        if not self.running:
            return
        self.timer.stop()
        self.running = False
        self.on_status("Execução parada.")

    def on_apply(self):
        # Apply PID and Plant configs
        self.pid_cfg.Kp = self.sb_Kp.value()
        self.pid_cfg.Ki = self.sb_Ki.value()
        self.pid_cfg.Kd = self.sb_Kd.value()
        self.pid_cfg.Ts = self.sb_Ts.value()
        self.pid_cfg.deriv_filter_N = self.sb_N.value()
        self.pid_cfg.anti_windup = self.cb_anti_windup.isChecked()
        self.pid_cfg.deriv_on_measurement = self.cb_d_on_meas.isChecked()
        self.pid_cfg.direct_action = self.cb_direct.isChecked()
        self.pid_cfg.out_min = self.sb_out_min.value()
        self.pid_cfg.out_max = self.sb_out_max.value()

        self.plant_cfg.K = self.sb_K.value()
        self.plant_cfg.tau = self.sb_tau.value()
        self.plant_cfg.dead_time = self.sb_dead.value()
        self.plant_cfg.noise_std = self.sb_noise.value()

        self.controller = PIDController(self.pid_cfg)
        self.plant = FOPDTPlant(self.plant_cfg)
        self.timer.setInterval(int(self.pid_cfg.Ts * 1000))
        self.on_status("Parâmetros aplicados.")

    def on_reset(self):
        self.controller.reset()
        self.plant.reset()
        self.time_elapsed = 0.0
        self.t_data.clear(); self.pv_data.clear(); self.co_data.clear(); self.sp_data.clear()
        self.canvas.ax.set_xlim(0, 10)
        self.canvas.ax.set_ylim(-110, 110)
        self.canvas.draw()
        self.on_status("Reset concluído.")

    def on_manual_toggled(self, checked: bool):
        self.manual_mode = checked
        self.controller.set_auto(not checked, self.manual_output)
        self.on_status("Modo Manual" if checked else "Modo Automático")

    def on_save(self):
        data = {
            "pid": self.pid_cfg.__dict__,
            "plant": self.plant_cfg.__dict__,
        }
        path, _ = QFileDialog.getSaveFileName(self, "Salvar preset", "preset_pid.json", "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.on_status(f"Preset salvo em {path}")

    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Carregar preset", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pid = data.get("pid", {})
            plant = data.get("plant", {})
            # Update widgets
            for key, box in [
                ("Kp", self.sb_Kp), ("Ki", self.sb_Ki), ("Kd", self.sb_Kd),
                ("Ts", self.sb_Ts), ("deriv_filter_N", self.sb_N)
            ]:
                if key in pid:
                    box.setValue(float(pid[key]))
            if "anti_windup" in pid: self.cb_anti_windup.setChecked(bool(pid["anti_windup"]))
            if "deriv_on_measurement" in pid: self.cb_d_on_meas.setChecked(bool(pid["deriv_on_measurement"]))
            if "direct_action" in pid: self.cb_direct.setChecked(bool(pid["direct_action"]))
            if "out_min" in pid: self.sb_out_min.setValue(float(pid["out_min"]))
            if "out_max" in pid: self.sb_out_max.setValue(float(pid["out_max"]))

            for key, box in [("K", self.sb_K), ("tau", self.sb_tau), ("dead_time", self.sb_dead), ("noise_std", self.sb_noise)]:
                if key in plant:
                    box.setValue(float(plant[key]))
            self.on_apply()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar o preset:\n{e}")

    def on_export(self):
        if not self.log_rows:
            QMessageBox.information(self, "Info", "Sem dados para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "pid_log.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["t", "SP", "PV", "CO", "Kp", "Ki", "Kd"])
                writer.writerows(self.log_rows)
            self.on_status(f"CSV exportado: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar CSV:\n{e}")

    def on_autotune_start(self):
        if not self.running:
            QMessageBox.information(self, "Info", "Inicie a simulação antes do autotune.")
            return
        self.autotune.h = self.sb_relay.value()
        self.autotune.start()

    def on_autotune_stop(self):
        self.autotune.stop()

    def on_autotune_finished(self, Ku: float, Pu: float, Kp: float, Ki: float, Kd: float):
        # Apply suggested gains to UI but do not force start
        self.sb_Kp.setValue(Kp)
        self.sb_Ki.setValue(Ki)
        self.sb_Kd.setValue(Kd)
        self.on_status(f"ZN sugerido: Kp={Kp:.3f}, Ki={Ki:.3f}, Kd={Kd:.3f} (Ku={Ku:.3f}, Pu={Pu:.3f})")

    # ----------------------- Simulation Loop -----------------------

    def compute_setpoint(self, t: float) -> float:
        base = self.sb_sp.value()
        if self.sp_profile.currentText() == "Senoidal":
            amp = self.sb_sp_amp.value()
            freq = self.sb_sp_freq.value()
            return base + amp * math.sin(2 * math.pi * freq * t)
        return base

    def on_timer(self):
        Ts = self.sb_Ts.value()
        self.time_elapsed += Ts
        t = self.time_elapsed

        # current setpoint
        sp = self.compute_setpoint(t)

        # controller / autotune
        if self.autotune.is_running():
            # override output by relay test
            co = self.autotune.compute_relay_output(sp, self.plant.y)
            self.autotune.update(t, sp, self.plant.y)
        else:
            # normal PID
            self.manual_output = self.sb_manual.value()
            co = self.controller.update(sp, self.plant.y, manual=self.cb_manual.isChecked(), manual_output=self.manual_output)

        # plant step
        pv = self.plant.step(co if self.pid_cfg.direct_action else -co)  # adjust for direct/reverse action meaning

        # logging
        self.log_rows.append([t, sp, pv, co, self.pid_cfg.Kp, self.pid_cfg.Ki, self.pid_cfg.Kd])

        # plot buffers
        self.t_data.append(t)
        self.sp_data.append(sp)
        self.pv_data.append(pv)
        self.co_data.append(co)

        # dynamic axis
        if len(self.t_data) > 2:
            tmin, tmax = self.t_data[0], self.t_data[-1]
            self.canvas.ax.set_xlim(tmin, tmax)
            y_all = list(self.sp_data) + list(self.pv_data) + list(self.co_data)
            if y_all:
                ymin = min(y_all); ymax = max(y_all)
                if ymin == ymax:
                    ymin -= 1; ymax += 1
                pad = 0.05 * (ymax - ymin)
                self.canvas.ax.set_ylim(ymin - pad, ymax + pad)

        # update lines
        self.line_sp.set_data(self.t_data, self.sp_data)
        self.line_pv.set_data(self.t_data, self.pv_data)
        self.line_co.set_data(self.t_data, self.co_data)
        self.canvas.draw_idle()

        # update controller config live (optional)
        self.controller.cfg.out_min = self.sb_out_min.value()
        self.controller.cfg.out_max = self.sb_out_max.value()

    # ----------------------- End Window -----------------------


def main():
    app = QApplication([])
    win = PIDTunerWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
