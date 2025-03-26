from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Signal
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from react.reactDB import ReactDataBase
from inter.ireactvar import DBReactiveVariable
from inter.istate import DBState
from ctrl.simul_tf import SimulTf
from functools import partial
from img.imgCaldeira import imagem_base64
import sys

class MainWindow(QMainWindow, Ui_MainWindow):
    # resizeEventSignal = Signal()  # 🔥 Declarando o sinal corretamente
    
    def __init__(self):
        super().__init__()
        self.resize(800, 500)  # Defina o tamanho desejado
        self.setupUi(self)  # Configura a interface do Qt Designer  
        # self.radioButtonHex.clicked["bool"].connect(self.oldDBTableWidget.changeType) 
        self.reactDataBase = ReactDataBase()
        self.hrtDBTableWidget.setBaseData(self.reactDataBase,"HART")
        self.mbDBTableWidget.setBaseData(self.reactDataBase,"HART")        
        self.simulTf = SimulTf(self.reactDataBase, 1000)
        self.pushButtonStart.toggled.connect(self.simulTf.start)
        self.pushButtonReset.toggled.connect(self.simulTf.reset)
        # image_path = os.path.abspath("img/caldeira.jpg")
        self.processTab1.setBackgroundImageFromBase64(imagem_base64)
        self.connectLCDs()
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
    
    def connectLCDs(self):
        lcd_names = ["lcdLI100", "lcdFI100V", "lcdFI100A", "lcdFV100A","lcdPI100V","lcdTI100"] #,"lcdVI100CA","lcdVI100AR"]
        db_indices = [("percent_of_range", "LI100"), ("percent_of_range", "FI100V"), ("percent_of_range", "FI100A"),("percent_of_range", "FV100A"), ("percent_of_range", "PI100V"),("percent_of_range", "TI100")] #, ("idx4", "VI100CA"), ("idx4", "VI100AR")]
        def atualizaDisplay(lcd_widget,var):
            lcd_widget.display(var.value(DBState.humanValue))
        for lcd_name, (row, col) in zip(lcd_names, db_indices):
            lcd_widget = getattr(self, lcd_name)
            var: DBReactiveVariable = self.reactDataBase.dfhrt.loc[row, col]
            var.valueChanged.connect(
                partial(atualizaDisplay,lcd_widget,var)
            )   
    
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
        self.widgetPI100V.move(parent_width * 0.30, parent_height * 0.25)
        self.widgetTI100.move(parent_width * 0.35, parent_height * 0.40)
        self.groupBoxSimul.move(parent_width - 190, parent_height - 220)        
        # self.resizeEventSignal.emit(event)
        super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())