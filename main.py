import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from uis.ui_main import Ui_MainWindow
from react.react_factory import ReactFactory
from db.db_types import DBState, DBModel
from ctrl.simul_tf import SimulTf
from functools import partial
from img.imgCaldeira import imagem_base64
from mb.mb_server import ModbusServerThread

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Cria ReactFactory assincronamente
        self.reactFactory = asyncio.run(
            ReactFactory.create(["HART", "MODBUS"])
        )

        # Configura simulador
        self.simulTf = SimulTf(500)
        # Conecta sinal de tFunc
        self.reactFactory.isTFuncSignal.connect(self.simulTf.tfConnect)
        # Registra manualmente variáveis já com tFunc
        for tbl in self.reactFactory.df:
            for row in self.reactFactory.df[tbl].index:
                for col in self.reactFactory.df[tbl].columns:
                    var = self.reactFactory.df[tbl].at[row, col]
                    if var.model == DBModel.tFunc:
                        self.simulTf.tfConnect(var, True)

        # Inicia servidor Modbus
        self.servidor_thread = ModbusServerThread(self.reactFactory, num_slaves=1, port=502)

        # Setup UI
        self.resize(800, 500)
        self.setupUi(self)

        # Hex view
        self.radioButtonHex.clicked[bool].connect(self.hrtDBTableWidget.changeType)

        # Start/Stop simulação
        def startSimul(state: bool):
            if state:
                self.servidor_thread.start()
            else:
                self.servidor_thread.stop()
            self.simulTf.start(state)

        self.pushButtonStart.toggled.connect(startSimul)

        # Carrega tabelas
        self.hrtDBTableWidget.setBaseData(self.reactFactory, "HART")
        self.mbDBTableWidget.setBaseData(self.reactFactory, "MODBUS")

        # Botão reset
        def resetTf():
            self.buttonGroupSimul.exclusive = False
            self.pushButtonStart.setChecked(False)
            self.pushButtonStop.setChecked(True)
            self.buttonGroupSimul.exclusive = True
            self.simulTf.reset()

        self.pushButtonReset.clicked.connect(resetTf)

        # Imagem de fundo
        self.processTab1.setBackgroundImageFromBase64(imagem_base64)

        # Configura LCDs e sliders
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
            lcd = getattr(self, f'lcd{device}')
            var = self.reactFactory.df["HART"].at[rowRead, device]
            var.valueChangedSignal.connect(partial(atualizaDisplay, lcd))
            lcd.display(self._sync(var.getValue(DBState.humanValue)))

        def atualizaValue(varWrite, x):
            varWrite.setValue(x, DBState.humanValue)

        for device in devices_hr:
            slider = getattr(self, f'slider{device}', None)
            if slider:
                slider.setMinimum(0)
                slider.setMaximum(65535)
                varW = self.reactFactory.df["MODBUS"].at[device, "CLP100"]
                slider.setValue(int(self._sync(varW.getValue(DBState.humanValue))))
                slider.valueChanged.connect(partial(atualizaValue, varW))

    def centralizar_janela(self):
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        center = geo.center()
        frame = self.frameGeometry()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def resizeEvent(self, event):
        w, h = event.size().width(), event.size().height()
        self.widgetLIT100.move(w*0.58, h*0.02)
        self.widgetTIT100.move(w*0.35, h*0.40)
        self.widgetPIT100V.move(25, 10)
        self.widgetFIT100V.move(-4, 80)
        self.widgetPIT100A.move(-4, 300)
        self.widgetFIT100A.move(w-210, 10)
        self.widgetFV100A.move(w-248, 68)
        self.widgetFIT100CA.move(w*0.20, h*0.75)
        self.widgetFV100CA.move(w*0.30, h*0.68)
        self.widgetFIT100AR.move(w*0.54, h*0.75)
        self.widgetFV100AR.move(w*0.64, h*0.68)
        self.groupBoxSimul.move(w-190, h-220)
        super().resizeEvent(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Sair", "Tem certeza?", QMessageBox.Yes|QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.simulTf.start(False)
            print("🔒 Salvando dados...")
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())