# ctrl/plotting/toolbar.py
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class PVToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.addSeparator()
        self.act_v = self.addAction("📏 V")
        self.act_h = self.addAction("📐 H")
        self.act_kp = self.addAction("🧭 Kp")
        self.act_clear = self.addAction("❌ Limpar Cursores")
        self.act_reset = self.addAction("🧹 Reset")

        for a in (self.act_v, self.act_h, self.act_kp):
            a.setCheckable(True)

        # exclusividade: ao ligar um, os outros desligam
        def _select(mode):
            if mode == "v":
                self.act_v.setChecked(True); self.act_h.setChecked(False); self.act_kp.setChecked(False)
                parent.set_cursor_mode("v");  parent.set_kp_mode(False)
            elif mode == "h":
                self.act_v.setChecked(False); self.act_h.setChecked(True); self.act_kp.setChecked(False)
                parent.set_cursor_mode("h");  parent.set_kp_mode(False)
            elif mode == "kp":
                self.act_v.setChecked(False); self.act_h.setChecked(False); self.act_kp.setChecked(True)
                parent.set_cursor_mode(None); parent.set_kp_mode(True)
            else:
                self.act_v.setChecked(False); self.act_h.setChecked(False); self.act_kp.setChecked(False)
                parent.set_cursor_mode(None); parent.set_kp_mode(False)

        self.act_v.triggered.connect(lambda checked: _select("v"  if checked else None))
        self.act_h.triggered.connect(lambda checked: _select("h"  if checked else None))
        self.act_kp.triggered.connect(lambda checked: _select("kp" if checked else None))

        self.act_clear.triggered.connect(parent.on_clear_cursors_clicked)
        self.act_reset .triggered.connect(parent.on_reset_toolbar)
