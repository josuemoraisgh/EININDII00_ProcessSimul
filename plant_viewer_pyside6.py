
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plant Viewer with Horizontal Slider and Value Entry
- Horizontal slider for u(t)
- Textbox + "Aplicar u" button to set u
- Configurable u min/max and step
- Quick step buttons: +A and -A (amplitude A configurable)
- FOPDT plant simulation, zoom/pan, crosshair, locked cursor
- Draw/clear line feature
"""

import math
from collections import deque
from dataclasses import dataclass

import numpy as np

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFormLayout, QHBoxLayout, QVBoxLayout,
    QDoubleSpinBox, QSlider, QLabel, QGroupBox,
    QPushButton, QLineEdit, QSpinBox
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


@dataclass
class FOPDTConfig:
    K: float = 1.0
    tau: float = 3.0
    dead_time: float = 0.5
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
        self.u_buffer.append(u)
        u_delayed = self.u_buffer[0] if self.u_buffer else u
        Ts = self.cfg.Ts
        dy = (-(self.y) + self.cfg.K * u_delayed) * (Ts / self.cfg.tau)
        self.y += dy
        if self.cfg.noise_std > 0.0:
            self.y += np.random.normal(0.0, self.cfg.noise_std)
        return self.y


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(7, 4), tight_layout=True)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True)

        self.hline = self.ax.axhline(0, lw=0.8, ls="--", alpha=0.5)
        self.vline = self.ax.axvline(0, lw=0.8, ls="--", alpha=0.5)
        self.hline.set_visible(False)
        self.vline.set_visible(False)

        self.locked_vline = None
        self.annot = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)

        self.draw_line_artist = None
        self.enable_click_cursor = True

        self.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.mpl_connect("axes_leave_event", self.on_axes_leave)
        self.mpl_connect("button_press_event", self.on_click)

    def on_mouse_move(self, event):
        if not event.inaxes:
            self.hline.set_visible(False)
            self.vline.set_visible(False)
            self.draw_idle()
            return
        self.hline.set_visible(True)
        self.vline.set_visible(True)
        self.hline.set_ydata([event.ydata])
        self.vline.set_xdata([event.xdata])
        self.draw_idle()

    def on_axes_leave(self, event):
        self.hline.set_visible(False)
        self.vline.set_visible(False)
        self.draw_idle()

    def on_click(self, event):
        if not self.enable_click_cursor:
            return
        if event.button == 1 and event.inaxes:
            x = event.xdata
            if self.locked_vline is None:
                self.locked_vline = self.ax.axvline(x, lw=1.2, ls="-.", alpha=0.7)
            else:
                self.locked_vline.set_xdata([x])
            self.annot.xy = (x, self.ax.get_ybound()[1])
            self.annot.set_visible(True)
            self.draw_idle()
        elif event.button == 3:
            if self.locked_vline is not None:
                self.locked_vline.remove()
                self.locked_vline = None
            self.annot.set_visible(False)
            self.draw_idle()

    def clear_drawn_line(self):
        if self.draw_line_artist is not None:
            try:
                self.draw_line_artist.remove()
            except Exception:
                pass
            self.draw_line_artist = None
            self.draw_idle()

    def set_drawn_line(self, x1, y1, x2, y2):
        self.clear_drawn_line()
        self.draw_line_artist, = self.ax.plot([x1, x2], [y1, y2], lw=1.6, ls='-', alpha=0.85)
        self.draw_idle()


class PlantViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planta FOPDT - Visualizador")
        self.resize(1150, 680)

        self.cfg = FOPDTConfig()
        self.plant = FOPDTPlant(self.cfg)
        self.running = False
        self.time_elapsed = 0.0
        self.u_input = 0.0

        self.drawing_line = False
        self.first_point = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.setInterval(int(self.cfg.Ts * 1000))

        self.max_points = 4000
        self.t_data = deque(maxlen=self.max_points)
        self.y_data = deque(maxlen=self.max_points)
        self.u_data = deque(maxlen=self.max_points)

        self._build_ui()

    def _build_ui(self):
        central = QWidget(self); self.setCentralWidget(central)
        main = QHBoxLayout(central)

        plot_layout = QVBoxLayout()
        self.canvas = MplCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, stretch=1)

        self.line_y, = self.canvas.ax.plot([], [], label="PV (y)")
        self.line_u, = self.canvas.ax.plot([], [], label="Entrada (u)")
        self.canvas.ax.legend(loc="upper right")

        ctrl_layout = QVBoxLayout()

        plant_group = QGroupBox("Parâmetros da Planta (FOPDT)")
        plant_form = QFormLayout(plant_group)
        self.sb_K = QDoubleSpinBox(); self.sb_K.setRange(-1e6, 1e6); self.sb_K.setValue(self.cfg.K)
        self.sb_tau = QDoubleSpinBox(); self.sb_tau.setRange(0.01, 1e6); self.sb_tau.setValue(self.cfg.tau)
        self.sb_dead = QDoubleSpinBox(); self.sb_dead.setRange(0.0, 100.0); self.sb_dead.setValue(self.cfg.dead_time)
        self.sb_Ts = QDoubleSpinBox(); self.sb_Ts.setRange(0.001, 10.0); self.sb_Ts.setValue(self.cfg.Ts)
        self.sb_noise = QDoubleSpinBox(); self.sb_noise.setRange(0.0, 1000.0); self.sb_noise.setValue(self.cfg.noise_std)
        plant_form.addRow("K:", self.sb_K)
        plant_form.addRow("τ:", self.sb_tau)
        plant_form.addRow("Dead time:", self.sb_dead)
        plant_form.addRow("Ts:", self.sb_Ts)
        plant_form.addRow("Ruído σ:", self.sb_noise)
        ctrl_layout.addWidget(plant_group)

        # Input control group
        input_group = QGroupBox("Entrada (u)")
        input_layout = QVBoxLayout(input_group)

        range_layout = QHBoxLayout()
        self.sb_u_min = QDoubleSpinBox(); self.sb_u_min.setRange(-1e6, 0); self.sb_u_min.setValue(-100.0)
        self.sb_u_max = QDoubleSpinBox(); self.sb_u_max.setRange(0, 1e6); self.sb_u_max.setValue(100.0)
        self.sb_u_step = QDoubleSpinBox(); self.sb_u_step.setRange(0.001, 100); self.sb_u_step.setValue(0.1)
        range_layout.addWidget(QLabel("Min:")); range_layout.addWidget(self.sb_u_min)
        range_layout.addWidget(QLabel("Max:")); range_layout.addWidget(self.sb_u_max)
        range_layout.addWidget(QLabel("Step:")); range_layout.addWidget(self.sb_u_step)
        input_layout.addLayout(range_layout)

        self.slider_u = QSlider(Qt.Horizontal)
        self.slider_u.valueChanged.connect(self.on_slider_u)

        self.le_u = QLineEdit("0.0")
        self.btn_u_apply = QPushButton("Aplicar u")
        self.btn_u_apply.clicked.connect(self.on_apply_u)

        val_layout = QHBoxLayout()
        val_layout.addWidget(self.le_u)
        val_layout.addWidget(self.btn_u_apply)

        amp_layout = QHBoxLayout()
        self.sb_amp = QDoubleSpinBox(); self.sb_amp.setRange(0.0, 1000.0); self.sb_amp.setValue(10.0)
        btn_plusA = QPushButton("+A")
        btn_minusA = QPushButton("-A")
        btn_plusA.clicked.connect(lambda: self.quick_step(self.sb_amp.value()))
        btn_minusA.clicked.connect(lambda: self.quick_step(-self.sb_amp.value()))
        amp_layout.addWidget(QLabel("A:")); amp_layout.addWidget(self.sb_amp)
        amp_layout.addWidget(btn_plusA); amp_layout.addWidget(btn_minusA)

        input_layout.addWidget(self.slider_u)
        input_layout.addLayout(val_layout)
        input_layout.addLayout(amp_layout)

        ctrl_layout.addWidget(input_group)

        # Buttons
        btns1 = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar")
        self.btn_stop = QPushButton("Parar")
        self.btn_reset = QPushButton("Resetar")
        self.btn_apply = QPushButton("Aplicar Planta")
        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_apply.clicked.connect(self.on_apply)
        for b in (self.btn_start, self.btn_stop, self.btn_reset, self.btn_apply):
            btns1.addWidget(b)
        ctrl_layout.addLayout(btns1)

        btns2 = QHBoxLayout()
        self.btn_line_draw = QPushButton("Reta: Desenhar")
        self.btn_line_clear = QPushButton("Reta: Apagar")
        self.btn_line_draw.clicked.connect(self.on_line_draw)
        self.btn_line_clear.clicked.connect(self.on_line_clear)
        btns2.addWidget(self.btn_line_draw)
        btns2.addWidget(self.btn_line_clear)
        ctrl_layout.addLayout(btns2)

        main.addLayout(plot_layout, stretch=2)
        main.addLayout(ctrl_layout, stretch=1)

        self.statusBar().showMessage("Pronto.")

        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self.canvas.mpl_connect("button_press_event", self.update_locked_cursor_annotation)

    # --- Input handling ---
    def sync_slider_range(self):
        self.slider_u.blockSignals(True)
        min_val = self.sb_u_min.value()
        max_val = self.sb_u_max.value()
        step = self.sb_u_step.value()
        self.slider_u.setMinimum(0)
        self.slider_u.setMaximum(int((max_val - min_val)/step))
        self.slider_u.blockSignals(False)

    def on_slider_u(self, idx_val: int):
        min_val = self.sb_u_min.value()
        step = self.sb_u_step.value()
        val = min_val + idx_val * step
        self.u_input = val
        self.le_u.setText(f"{val:.3f}")

    def on_apply_u(self):
        try:
            val = float(self.le_u.text())
        except ValueError:
            return
        self.u_input = val
        min_val = self.sb_u_min.value()
        step = self.sb_u_step.value()
        idx_val = int(round((val - min_val) / step))
        self.slider_u.blockSignals(True)
        self.slider_u.setValue(idx_val)
        self.slider_u.blockSignals(False)

    def quick_step(self, delta: float):
        self.on_apply_u()
        self.u_input += delta
        self.le_u.setText(f"{self.u_input:.3f}")
        self.on_apply_u()

    # --- Simulation control ---
    def on_start(self):
        if self.running:
            return
        self.running = True
        self.time_elapsed = 0.0
        self.t_data.clear(); self.y_data.clear(); self.u_data.clear()
        self.plant.reset()
        self.timer.setInterval(int(self.cfg.Ts * 1000))
        self.sync_slider_range()
        self.timer.start()

    def on_stop(self):
        self.timer.stop()
        self.running = False

    def on_reset(self):
        self.on_stop()
        self.time_elapsed = 0.0
        self.t_data.clear(); self.y_data.clear(); self.u_data.clear()
        self.plant.reset()
        self.canvas.ax.set_xlim(0, 10)
        self.canvas.ax.set_ylim(-110, 110)
        if self.canvas.locked_vline is not None:
            self.canvas.locked_vline.remove()
            self.canvas.locked_vline = None
        self.canvas.annot.set_visible(False)
        self.canvas.clear_drawn_line()
        self.redraw()

    def on_apply(self):
        self.cfg.K = float(self.sb_K.value())
        self.cfg.tau = float(self.sb_tau.value())
        self.cfg.dead_time = float(self.sb_dead.value())
        self.cfg.Ts = float(self.sb_Ts.value())
        self.cfg.noise_std = float(self.sb_noise.value())
        self.plant = FOPDTPlant(self.cfg)
        if self.running:
            self.timer.setInterval(int(self.cfg.Ts * 1000))

    def on_timer(self):
        Ts = self.cfg.Ts
        self.time_elapsed += Ts
        t = self.time_elapsed
        y = self.plant.step(self.u_input)
        self.t_data.append(t)
        self.y_data.append(y)
        self.u_data.append(self.u_input)
        if len(self.t_data) > 2:
            tmin, tmax = self.t_data[0], self.t_data[-1]
            self.canvas.ax.set_xlim(tmin, tmax)
            y_all = list(self.y_data) + list(self.u_data)
            ymin, ymax = min(y_all), max(y_all)
            if ymin == ymax:
                ymin -= 1; ymax += 1
            pad = 0.05 * (ymax - ymin)
            self.canvas.ax.set_ylim(ymin - pad, ymax + pad)
        self.redraw()
        self.update_locked_cursor_annotation(None)

    def redraw(self):
        self.line_y.set_data(self.t_data, self.y_data)
        self.line_u.set_data(self.t_data, self.u_data)
        self.canvas.draw_idle()

    # --- Line drawing ---
    def on_line_draw(self):
        if self.drawing_line:
            return
        self.drawing_line = True
        self.first_point = None
        self.canvas.enable_click_cursor = False

    def on_line_clear(self):
        self.canvas.clear_drawn_line()

    def on_canvas_click(self, event):
        if not self.drawing_line:
            return
        if not event.inaxes:
            return
        if event.button == 3:
            self.drawing_line = False
            self.first_point = None
            self.canvas.enable_click_cursor = True
            return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata
        if self.first_point is None:
            self.first_point = (x, y)
        else:
            x1, y1 = self.first_point
            self.canvas.set_drawn_line(x1, y1, x, y)
            self.drawing_line = False
            self.first_point = None
            self.canvas.enable_click_cursor = True

    def update_locked_cursor_annotation(self, event):
        if self.canvas.locked_vline is None:
            return
        if not self.t_data:
            return
        x = self.canvas.locked_vline.get_xdata()[0]
        t_list = list(self.t_data)
        idx = min(range(len(t_list)), key=lambda i: abs(t_list[i] - x))
        t_near = t_list[idx]
        y_near = list(self.y_data)[idx]
        u_near = list(self.u_data)[idx]
        self.canvas.annot.xy = (t_near, y_near)
        self.canvas.annot.set_text(f"t={t_near:.2f}s\nPV={y_near:.3f}\nu={u_near:.3f}")
        self.canvas.annot.set_visible(True)
        self.canvas.draw_idle()


def main():
    app = QApplication([])
    w = PlantViewerWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
