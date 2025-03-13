from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt.hrt_data import HrtData
from dbtablewidget import DBTableWidget
from ctrlglwidget import CtrlGLWidget
import sys
import os

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, hrt_data: HrtData):
        super().__init__()
        self.resize(800, 600)  # Defina o tamanho desejado
        self.setupUi(self)  # Configura a interface do Qt Designer        
        self.oldDBTableWidget.setBaseData(hrt_data)
        image_path = os.path.abspath("img/caldeira.jpg")
        self.oldCtrlGLWidget.setBackgroundImage(image_path)
        self.centralizar_janela()

    def centralizar_janela(self):
        # Obtém a tela primária
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        # Obtém a geometria da janela
        janela_geometry = self.frameGeometry()
        # Calcula o centro da tela e ajusta a posição da janela
        center_point = screen_geometry.center()
        janela_geometry.moveCenter(center_point)
        # Aplica a posição calculada
        self.move(janela_geometry.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData()
    window = MainWindow(hrt_data)
    window.show()
    sys.exit(app.exec())
