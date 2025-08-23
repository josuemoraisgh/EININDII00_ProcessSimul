import sys
import traceback
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton
from PySide6.QtCore import Qt
from uis.ui_main import Ui_MainWindow
from react.react_factory import ReactFactory
from db.db_types import DBState, DBModel
from ctrl.simul_tf import SimulTf
from functools import partial

from db.db_types import DBState

def bind_slider_to_reactvar(slider, reactVar, sync_call):
    """Vínculo bidirecional entre slider e ReactVar em humanValue (0..100%).
    - Slider -> ReactVar via setValue(..., DBState.humanValue, True)
    - ReactVar -> Slider via valueChangedSignal (bloqueando sinais para evitar loop)
    sync_call: função que executa corotinas (ex.: self._sync)
    """
    # Slider -> ReactVar
    def _on_slider(val: int):
        try:
            reactVar.setValue(val, stateAtual=DBState.humanValue, isWidgetValueChanged=True)
        except Exception as e:
            print(f"[bind] setValue failed: {e}")
    if hasattr(slider, 'valueChanged'):
        slider.valueChanged.connect(_on_slider)

    # ReactVar -> Slider
    def _on_var_changed(data):
        if data is not reactVar:
            return
        try:
            hv = sync_call(reactVar.getValue(DBState.humanValue))
        except Exception:
            try:
                hv = int(getattr(reactVar, '_value', 0))
            except Exception:
                return
        try:
            if hasattr(slider, 'blockSignals'):
                prev = slider.blockSignals(True)
            slider.setValue(int(hv))
        finally:
            if hasattr(slider, 'blockSignals'):
                slider.blockSignals(prev if 'prev' in locals() else False)
    try:
        reactVar.valueChangedSignal.connect(_on_var_changed)
    except Exception as e:
        print(f"[bind] connect valueChangedSignal failed: {e}")
from img.imgCaldeira import imagem_base64
from mb.mb_server import ModbusServer
from react.react_var import ReactVar
from ctrl.plant_viewer import PlantViewerWindow

import os
import shutil
import platform

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        print("🚀 Iniciando MainWindow...")

        # Cria ReactFactory assincronamente
        print("🔄 Criando ReactFactory...")
        self.reactFactory = asyncio.run(ReactFactory.create(["HART", "MODBUS"]))
        print("✅ ReactFactory criado com sucesso!")

        # Configura simulador
        print("🔄 Configurando Simulador...")
        self.simulTf = SimulTf(50)
        print("✅ Simulador configurado.")

        # Conecta sinal de tFunc
        print("🔄 Conectando sinais de tFunc...")
        self.reactFactory.isTFuncSignal.connect(self.simulTf.tfConnect)
        print("✅ Sinais de tFunc conectados.")

        # Registra manualmente variáveis já com tFunc
        print("🔄 Registrando variáveis com tFunc...")
        for tbl in self.reactFactory.df:
            for row in self.reactFactory.df[tbl].index:
                for col in self.reactFactory.df[tbl].columns:
                    var = self.reactFactory.df[tbl].at[row, col]
                    if var.model == DBModel.tFunc:
                        self.simulTf.tfConnect(var, True)
        print("✅ Variáveis registradas com tFunc.")

        # Inicia servidor Modbus
        print("🔄 Iniciando servidor Modbus...")
        self.servidor_thread = ModbusServer(self.reactFactory)

        # Setup UI
        print("🔄 Configurando UI...")
        self.resize(800, 500)
        self.setupUi(self)

        # Hex view
        print("🔄 Conectando hex view...")
        self.radioButtonHex.clicked[bool].connect(self.hrtDBTableWidget.changeType)

        # Start/Stop simulação
        print("🔄 Conectando Start/Stop simulação...")
        def startSimul(state: bool):
            if state:
                print("🔄 Iniciando servidor Modbus...")
                self.servidor_thread.start(port=int(self.lineEditMBPort.text().strip()))
            else:
                print("🔄 Parando servidor Modbus...")
                self.servidor_thread.stop()
            self.simulTf.start(state)

            # VISUAL do MAIN (fonte da verdade)
            self._set_main_running_visual(state)

            # Espelha VISUAL no viewer (se aberto)
            if self.plantViewer:
                self.plantViewer.sync_running_state(state)

        # Quando Start é pressionado/solto
        self.pushButtonStart.toggled.connect(startSimul)

        # Quando Stop é pressionado, força estado "parado"
        def stopSimul(checked: bool):
            if checked:           # reage quando Stop fica selecionado
                startSimul(False) # reusa a mesma lógica de parar
        self.pushButtonStop.toggled.connect(stopSimul)
        print("✅ Start/Stop simulação configurado.")

        # Carrega tabelas
        print("🔄 Carregando tabelas...")
        self.hrtDBTableWidget.setBaseData(self.reactFactory, "HART")
        self.mbDBTableWidget.setBaseData(self.reactFactory, "MODBUS")
        print("✅ Tabelas carregadas.")

        # Botão reset
        print("🔄 Configurando botão de reset...")
        def resetTf():
            self.buttonGroupSimul.exclusive = False
            self.pushButtonStart.setChecked(False)
            self.pushButtonStop.setChecked(True)
            self.buttonGroupSimul.exclusive = True
            self.simulTf.reset()

            # VISUAL parado
            self._set_main_running_visual(False)
            if self.plantViewer:
                self.plantViewer.sync_reset()
        self.pushButtonReset.clicked.connect(resetTf)
        print("✅ Botão de reset configurado.")

        # Imagem de fundo
        print("🔄 Configurando imagem de fundo...")
        self.processTab1.setBackgroundImageFromBase64(imagem_base64)
        print("✅ Imagem de fundo configurada.")

        # Configura LCDs e sliders
        print("🔄 Conectando LCDs e sliders...")
        self._sync = lambda coro: asyncio.run(coro)
        self.connectLCDs()
        self.centralizar_janela()
        print("✅ LCDs e sliders configurados.")

        # ---------- Plant Viewer ----------
        self.plantViewer = None
        self.btnOpenPlantViewer = QPushButton("Abrir Plant Viewer", self.groupBoxSimul)
        _layout = self.groupBoxSimul.layout()
        if _layout is not None:
            _layout.addWidget(self.btnOpenPlantViewer)
        else:
            # se não tiver layout, posiciona abaixo do Reset (fallback)
            y = self.pushButtonReset.y() + self.pushButtonReset.height() + 6
            self.btnOpenPlantViewer.move(self.pushButtonReset.x(), y)
        self.btnOpenPlantViewer.clicked.connect(self._openPlantViewer)

        # Espelhamento VISUAL para o viewer (sem lógica)
        self.pushButtonStart.toggled.connect(self._mirror_start_visual_to_viewer)
        self.pushButtonStop.toggled.connect(self._mirror_stop_visual_to_viewer)
        self.pushButtonReset.clicked.connect(self._mirror_reset_visual_to_viewer)
        # ----------------------------------

        # Fecha o PlantViewer quando a aplicação encerrar (extra segurança)
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(lambda: (self.plantViewer and self.plantViewer.close()))

    # ----- estilos VISUAIS dos botões do MAIN -----
    def _set_main_running_visual(self, running: bool):
        if running:
            # Start verde, Stop default
            self.pushButtonStart.setStyleSheet("background:#2ecc71; color:white; font-weight:bold;")
            self.pushButtonStop.setStyleSheet("")  # default
        else:
            # Stop vermelho, Start default
            self.pushButtonStart.setStyleSheet("")
            self.pushButtonStop.setStyleSheet("background:#ff2d2d; color:white; font-weight:bold;")

    # ----- espelhamento VISUAL para o viewer (sem lógica) -----
    def _mirror_start_visual_to_viewer(self, checked: bool):
        if self.plantViewer:
            self.plantViewer.sync_running_state(checked)

    def _mirror_stop_visual_to_viewer(self, checked: bool):
        if self.plantViewer and checked:
            self.plantViewer.sync_running_state(False)

    def _mirror_reset_visual_to_viewer(self, *args):
        if self.plantViewer:
            self.plantViewer.sync_reset()
    # ----------------------------------------------------------

    def _openPlantViewer(self):
        if self.plantViewer is None:
            self.plantViewer = PlantViewerWindow(
                react_factory=self.reactFactory,
                simul_tf=self.simulTf,   # <- mesma simulação da tela principal
            )
            # Viewer -> MAIN: quando o usuário clica lá, o MAIN aplica a lógica padrão
            self.plantViewer.simStartStop.connect(self._apply_running_from_viewer)  # bool
            self.plantViewer.simReset.connect(lambda: self.pushButtonReset.click())

            # Limpa a referência quando fechar a janela
            self.plantViewer.setAttribute(Qt.WA_DeleteOnClose)
            self.plantViewer.destroyed.connect(lambda *_: setattr(self, "plantViewer", None))

            # Espelha estado atual no viewer
            self.plantViewer.sync_running_state(self.pushButtonStart.isChecked())

        self.plantViewer.show()
        self.plantViewer.raise_()
        self.plantViewer.activateWindow()

    # Viewer pediu start/stop -> aciona fluxo "padrão" do MAIN (liga Modbus, etc.)
    def _apply_running_from_viewer(self, running: bool):
        if self.pushButtonStart.isChecked() != running:
            # isso aciona startSimul/stopSimul via toggled
            self.pushButtonStart.setChecked(running)
            if not running:
                self.pushButtonStop.setChecked(True)
        else:
            # já coerente; só garante visual
            self._set_main_running_visual(running)

    def connectLCDs(self):
        print("🔄 Conectando LCDs...")
        self.isSliderChangeValue = False
        sliders = ['FV100CA', 'FV100AR', 'FV100A', 'FIT100V', 'PIT100A']
        displays = ['PIT100V', 'FIT100V','PIT100A', 'FIT100CA','FV100CA', 'TIT100', 'LIT100', 'FIT100AR', 'FV100AR', 'FIT100A', 'FV100A']

        def atualizaDisplay(lcd_widget, varRead):
            lcd_widget.display(self._sync(varRead.getValue(DBState.humanValue)))

        for display in displays:
            lcd = getattr(self, f'lcd{display}')
            varR = self.reactFactory.df["HART"].at["PROCESS_VARIABLE", display]
            varR.valueChangedSignal.connect(partial(atualizaDisplay, lcd))
            lcd.display(self._sync(varR.getValue(DBState.humanValue)))

        def atualizaValue(varWrite, value):
            varWrite.setValue(value, DBState.humanValue, True)

        def atualizaBotao(botao, varWrite):
            value = botao.isChecked()
            varWrite.setValue(str(value), DBState.humanValue, True)
            botao.setText("M" if value is True else "A")

        for device in sliders:
            slider = getattr(self, f'slider{device}', None)
            if slider:
                slider.setMinimum(0)
                slider.setMaximum(65535)
                varW = self.reactFactory.df["MODBUS"].at[f'W_{device}', "CLP100"]
                slider.setValue(int(self._sync(varW.getValue(DBState.humanValue))))
                slider.valueChanged.connect(partial(atualizaValue, varW))
                # Bind ReactVar -> Slider
                try:
                    bind_slider_to_reactvar(slider, varW, self._sync)
                except Exception as e:
                    print(f"[bind] Failed to bind slider {device}: {e}")
                botao = getattr(self, f'pbAM{device}', None)
            if botao:
                varAM = self.reactFactory.df["MODBUS"].at[f'AM_{device}', "CLP100"]
                botao.setChecked(bool(self._sync(varAM.getValue(DBState.humanValue))))
                botao.clicked.connect(partial(atualizaBotao, botao, varAM))

    def centralizar_janela(self):
        print("🔄 Centralizando janela...")
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        center = geo.center()
        frame = self.frameGeometry()
        frame.moveCenter(center)
        self.move(frame.topLeft())
        print("✅ Janela centralizada.")

    def resizeEvent(self, event):
        w, h = event.size().width(), event.size().height()
        print(f"🔄 Redimensionando janela para {w}x{h}...")
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
        print("✅ Redimensionamento concluído.")

    def closeEvent(self, event):
        print("🔄 Verificando se deseja sair...")
        reply = QMessageBox.question(
            self, "Sair", "Tem certeza?", QMessageBox.Yes|QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Para simulação / servidor
            try:
                self.simulTf.start(False)
            except Exception as e:
                print("⚠️ simulTf.start(False) falhou:", e)
            try:
                self.servidor_thread.stop()
            except Exception as e:
                print("⚠️ servidor_thread.stop() falhou:", e)

            # Fecha o Plant Viewer se estiver aberto
            try:
                if self.plantViewer:
                    self.plantViewer.blockSignals(True)
                    self.plantViewer.close()
                    self.plantViewer = None
            except Exception as e:
                print("⚠️ Falha ao fechar PlantViewer:", e)

            print("🔒 Salvando dados...")
            event.accept()
        else:
            event.ignore()
        print("✅ Evento de fechamento concluído.")

    def debug_modbus_vars(self, react_factory):
        print("\n🔍 [DEBUG] Mapas MODBUS:")
        df = react_factory.df.get("MODBUS")
        if df is None:
            print("❌ Tabela MODBUS não encontrada.")
            return

        for row_key in df.index:
            for col_key in df.columns:
                try:
                    var = df.at[row_key, col_key]
                    if isinstance(var, ReactVar):
                        addr = react_factory.df["MODBUS"].at[row_key, "ADDRESS"]._value
                        mb_point = react_factory.df["MODBUS"].at[row_key, "MB_POINT"]._value
                        print(f"[{row_key}][{col_key}] -> ADDR={addr} | MB_POINT={mb_point} | TYPE={var.type()} | VALUE={var._value}")
                except Exception as e:
                    print(f"[ERRO] Ao processar {row_key}.{col_key}: {e}")


if __name__ == '__main__':
    try:
        print("🚀 Iniciando a aplicação...")
        app = QApplication(sys.argv)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()
        input("Erro ocorrido. Pressione Enter para sair...")