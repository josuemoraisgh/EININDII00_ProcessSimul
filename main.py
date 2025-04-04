from PySide6.QtWidgets import QApplication, QMainWindow, QSlider
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from react.react_db import ReactDB
from db.db_types import DBState
from ctrl.simul_tf import SimulTf
from functools import partial
from img.imgCaldeira import imagem_base64
from mb.mb_server import ModbusServerThread
import sys


class MainWindow(QMainWindow, Ui_MainWindow):
    # resizeEventSignal = Signal()  # 🔥 Declarando o sinal corretamente
    
    def __init__(self):
        super().__init__()
        self.ReactDB = ReactDB({"HART", "MODBUS"})  
        self.simulTf = SimulTf(500)
        self.ReactDB.isTFuncSignal.connect(self.simulTf.tfConnect)
        
        servidor_thread = ModbusServerThread(num_slaves=1, port=5020)
        servidor_thread.start()            

        self.resize(800, 500)  # Defina o tamanho desejado
        self.setupUi(self)  # Configura a interface do Qt Designer     
        self.radioButtonHex.clicked["bool"].connect(self.hrtDBTableWidget.changeType)         
        self.pushButtonStart.toggled.connect(self.simulTf.start)           
        self.hrtDBTableWidget.setBaseData(self.ReactDB,"HART")
        self.mbDBTableWidget.setBaseData(self.ReactDB,"MODBUS")        
        def resetTf():                    
            self.buttonGroupSimul.exclusive = False   # Desliga exclusividade temporariamente
            self.pushButtonStart.setChecked(False)   # marca o botão como "despressionado"
            self.pushButtonStop.setChecked(True)     # marca o botão como "pressionado"
            self.buttonGroupSimul.exclusive = True    # Religa a exclusividade                         
            self.simulTf.reset()            
        self.pushButtonReset.clicked.connect(resetTf)
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
        devices = ['FV100CA', 'FI100CA', 'FV100AR', 'FI100AR', 'TI100', 'FI100V', 'PI100V', 'LI100', 'PI100A', 'FV100A', 'FI100A']
        col = "CLP100"
        def atualizaDisplay(lcd_widget,var):
            lcd_widget.display(var.getValue(DBState.humanValue))
        for device in devices:
            lcd_widget = getattr(self, f'lcd{device}')
            slider_widget: QSlider  = getattr(self, f'slider{device}', None)                
            var: ReactDB = self.ReactDB.df["MODBUS"].loc[device, col]
            if slider_widget != None:
                if device == 'FI100V':
                    slider_widget.setMinimum(0)
                    slider_widget.setMaximum(100)
                    slider_widget.setValue(100) 
                    def vchanded(var,x):
                        var.setValue(float(x)*0.0035,DBState.humanValue)
                    slider_widget.valueChanged.connect(partial(vchanded, var))                   
                elif device == 'PI100A':
                    slider_widget.setMinimum(0)
                    slider_widget.setMaximum(600)
                    slider_widget.setValue(400)
                    slider_widget.valueChanged.connect(var.setValue)                   
                else:
                    slider_widget.setMinimum(0)
                    slider_widget.setMaximum(100)
                    slider_widget.setValue(50) 
                    slider_widget.valueChanged.connect(var.setValue)             
            atualizaDisplay(lcd_widget,var)
            var.valueChangedSignal.connect(partial(atualizaDisplay,lcd_widget))   
    
    def resizeEvent(self, event):
        parent_width = event.size().width()
        parent_height = event.size().height()
        # meu_botao = self.findChild(QWidget, "widgetCtrlLIC100")
        self.widgetLI100.move(parent_width * 0.58,parent_height * 0.02)
        self.widgetTI100.move(parent_width * 0.35, parent_height * 0.40)
        
        self.widgetPI100V.move(25, 10)
        self.widgetFI100V.move(-4, 80)

        self.widgetPI100A.move(-4, 300)
        self.widgetFI100A.move(parent_width -210, 10)
        self.widgetFV100A.move(parent_width - 248, 68)
        
        self.widgetFI100CA.move(parent_width * 0.20, parent_height * 0.75)
        self.widgetFV100CA.move(parent_width * 0.30, parent_height * 0.68)
        
        self.widgetFI100AR.move(parent_width * 0.54, parent_height * 0.75)
        self.widgetFV100AR.move(parent_width * 0.64, parent_height * 0.68)
        
        self.groupBoxSimul.move(parent_width - 190, parent_height - 220)        
        # self.resizeEventSignal.emit(event)
        super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())