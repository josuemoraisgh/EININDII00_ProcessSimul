from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Signal
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt.hrt_data import HrtData
from ctrl.simul_tf import SimulTf
import sys
import os

class MainWindow(QMainWindow, Ui_MainWindow):
    # resizeEventSignal = Signal()  # 🔥 Declarando o sinal corretamente
    
    def __init__(self, hrt_data: HrtData):
        super().__init__()
        self.resize(800, 500)  # Defina o tamanho desejado
        self.setupUi(self)  # Configura a interface do Qt Designer  
        # self.radioButtonHex.clicked["bool"].connect(self.oldDBTableWidget.changeType) 
        self.oldDBTableWidget.setBaseData(hrt_data)
        self.simulTf = SimulTf(hrt_data, 0.01)   
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
    
    def resizeEvent(self, event):
        parent_width = event.size().width()
        parent_height = event.size().height()
        # meu_botao = self.findChild(QWidget, "widgetCtrlLIC100")
        self.widgetLI100.move(parent_width * 0.58,parent_height * 0.02)
        self.widgetFI100V.move(parent_width * 0.02, parent_height * 0.02)
        self.widgetFI100A.move(parent_width * 0.48, parent_height * 0.58)
        self.widgetFV100A.move(parent_width * 0.78, parent_height * 0.02)
        self.widgetVI100CA.move(parent_width * 0.28, parent_height * 0.68)
        self.widgetVI100AR.move(parent_width * 0.54, parent_height * 0.68)
        self.widgetPI100.move(parent_width * 0.30, parent_height * 0.25)
        self.widgetTI100.move(parent_width * 0.35, parent_height * 0.40)
        # self.resizeEventSignal.emit(event)
        super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData()
    window = MainWindow(hrt_data)
    window.show()
    sys.exit(app.exec())