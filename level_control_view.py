import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QPixmap, QPainter, QColor


class TankWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.current_level = 0

    def set_level(self, level):
        self.current_level = level
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor('skyblue'))
        width = self.width()
        height = self.height()
        fill_height = height * (self.current_level / 100.0)
        painter.drawRect(0, height - fill_height, width, fill_height)

class MockController(QObject):
    level_changed = Signal(float)

    def __init__(self):
        super().__init__()
        self.plantInputValue = 5.0
        self.tankOutputValue = 2.5
        self.current_level = 0.0

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_level)
        self.timer.start(1000)

    def simulate_level(self):
        self.current_level += 5.0
        if self.current_level > 100:
            self.current_level = 0.0
        self.level_updated.emit(self.current_level)

class LevelControlView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUI()
        self.controller.timer.timeout.connect(self.update_ui)

    def initUI(self):
        self.setWindowTitle("Teste LevelControlView")
        self.resize(400, 400)

        main_layout = QVBoxLayout(self)

        # Tank Widget
        self.tank_widget = TankWidget()
        main_layout.addWidget(self.tank_widget, stretch=3)

        # Imagens
        img_layout = QHBoxLayout()

        self.bomba_widget = QLabel()
        bomba_pix = QPixmap("assets/bomba.png")
        self.bomba_widget.setPixmap(bomba_pix.scaled(80, 80, Qt.KeepAspectRatio))

        self.trans_nivel = QLabel()
        trans_pix = QPixmap("assets/trans_nivel.png")
        self.trans_nivel.setPixmap(trans_pix.scaled(80, 80, Qt.KeepAspectRatio))

        img_layout.addWidget(self.bomba_widget)
        img_layout.addStretch()
        img_layout.addWidget(self.trans_nivel)

        main_layout.addLayout(img_layout, stretch=1)

        # Indicador
        self.indicador_label = QLabel("0%")
        self.indicador_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.indicador_label)

        # Sliders
        sliders_layout = QHBoxLayout()
        sliders = QWidget()
        sliders_layout = QHBoxLayout(sliders)

        self.slider_bomba = QSlider(Qt.Orientation.Horizontal)
        self.slider_bomba.setRange(0, 10)
        self.slider_bomba.setValue(int(self.controller.plantInputValue))
        sliders_layout.addWidget(QLabel("Vazão da Bomba"))
        sliders_layout.addWidget(self.slider_bomba)

        self.slider_saida = QSlider(Qt.Orientation.Horizontal)
        self.slider_bomba.setRange(0, 10)
        sliders_layout.addWidget(QLabel("Vazão de Saída"))
        sliders_layout.addWidget(self.slider_bomba)

        main_layout.addLayout(sliders_layout, stretch=1)

        self.setLayout(main_layout)

        # conexão ao controlador
        self.controller.timer.timeout.connect(self.update_ui)

    def update_ui(self):
        level = self.controller.current_level
        self.tank_widget.set_level(level)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = MockController()

    window = LevelControlView(controller)
    window.show()

    sys.exit(app.exec())
