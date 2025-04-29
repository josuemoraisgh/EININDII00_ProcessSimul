import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from react.react_factory import ReactFactory
from db.db_types import DBState
from ctrl.simul_tf import SimulTf
from functools import partial
from img.imgCaldeira import imagem_base64
from mb.mb_server import ModbusServerThread

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Inicializa ReactFactory de forma assíncrona usando asyncio.run
        self.reactFactory = asyncio.run(
            ReactFactory.create(["HART", "MODBUS"])
        )

        self.simulTf = SimulTf(500)
        self.reactFactory.isTFuncSignal.connect(self.simulTf.tfConnect)

        servidor_thread = ModbusServerThread(self.reactFactory, num_slaves=1, port=502)

        self.resize(800, 500)
        self.setupUi(self)

        # Configurações de botões
        self.radioButtonHex.clicked[bool].connect(self.hrtDBTableWidget.changeType)
        def startSimul(state: bool):
            if state:
                servidor_thread.start()
            else:
                servidor_thread.stop()
            self.simulTf.start(state)
        self.pushButtonStart.toggled.connect(startSimul)

        # Inicializa tabelas
        self.hrtDBTableWidget.setBaseData(self.reactFactory, "HART")
        self.mbDBTableWidget.setBaseData(self.reactFactory, "MODBUS")

        # Botão de reset
        def resetTf():
            self.buttonGroupSimul.exclusive = False
            self.pushButtonStart.setChecked(False)
            self.pushButtonStop.setChecked(True)
            self.buttonGroupSimul.exclusive = True
            self.simulTf.reset()
        self.pushButtonReset.clicked.connect(resetTf)

        # Imagem de fundo
        self.processTab1.setBackgroundImageFromBase64(imagem_base64)

        # Conecta displays e sliders
        # Usa asyncio.run para sincronizar coroutines
        self._sync = lambda coro: asyncio.run(coro)
        self.connectLCDs()
        self.centralizar_janela()

    def connectLCDs(self):
        devices_hr = ['FV100CA','FV100AR','FIT100V','PIT100A','FV100A']
        devices_ir = ['FIT100CA','FIT100AR','TIT100','PIT100V','LIT100','FIT100A'] 
        devices = devices_hr + devices_ir     
        rowRead = "PROCESS_VARIABLE"

        def atualizaDisplay(lcd_widget, varRead):
            value = self._sync(varRead.getValue(DBState.humanValue))
            lcd_widget.display(value)
        for device in devices:
            lcd_widget = getattr(self, f'lcd{device}')             
            varRead = self.reactFactory.df["HART"].at[rowRead, device]
            varRead.valueChangedSignal.connect(partial(atualizaDisplay,lcd_widget))
            lcd_widget.display(self._sync(varRead.getValue(DBState.humanValue)))

        def atualizaValue(varWrite, x):
            varWrite.setValue(x,DBState.humanValue)            
        for device in devices_hr:
            slider_widget = getattr(self, f'slider{device}', None)   
            if slider_widget != None:
                slider_widget.setMinimum(0)
                slider_widget.setMaximum(65535)
                varWrite = self.reactFactory.df["MODBUS"].at[device,"CLP100"]
                slider_widget.setValue(int(self._sync(varWrite.getValue(DBState.humanValue)))) 
                slider_widget.valueChanged.connect(partial(atualizaValue, varWrite))
            
    def centralizar_janela(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        janela_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        janela_geometry.moveCenter(center_point)
        self.move(janela_geometry.topLeft())   

    def resizeEvent(self, event):
        parent_width = event.size().width()
        parent_height = event.size().height()
        # Reposiciona dispositivos conforme o tamanho
        self.widgetLIT100.move(parent_width * 0.58,parent_height * 0.02)
        self.widgetTIT100.move(parent_width * 0.35, parent_height * 0.40)
        self.widgetPIT100V.move(25, 10)
        self.widgetFIT100V.move(-4, 80)
        self.widgetPIT100A.move(-4, 300)
        self.widgetFIT100A.move(parent_width -210, 10)
        self.widgetFV100A.move(parent_width - 248, 68)
        self.widgetFIT100CA.move(parent_width * 0.20, parent_height * 0.75)
        self.widgetFV100CA.move(parent_width * 0.30, parent_height * 0.68)
        self.widgetFIT100AR.move(parent_width * 0.54, parent_height * 0.75)
        self.widgetFV100AR.move(parent_width * 0.64, parent_height * 0.68)
        self.groupBoxSimul.move(parent_width - 190, parent_height - 220)        
        super().resizeEvent(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Sair",
            "Tem certeza que deseja sair?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.simulTf.start(False)  
            print("🔒 Salvando dados antes de sair...")                      
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
