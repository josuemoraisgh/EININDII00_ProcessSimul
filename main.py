<<<<<<< HEAD

"""
db_app_tk.py
------------
Tkinter main window equivalent to the PySide6 bootstrap the user provided.

It:
- creates ReactFactory (async) for ["HART", "MODBUS"]
- configures SimulTf and connects isTFuncSignal
- registers preexisting tFunc variables
- starts/stops a ModbusServer thread on demand
- offers UI controls:
    * Human/Hex view (applies to both tables)
    * Start/Stop simulation and Modbus server (with port field)
    * Notebook with two tabs (HART, MODBUS) showing DBTableWidgetTk tables
"""

from __future__ import annotations
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
# --- project imports (expected to exist in your environment) ---
from db.db_types import DBModel, DBState
from react.react_factory import ReactFactory
from ctrl.simul_tf import SimulTf    # adjust path if different in your project
from mb.mb_server import ModbusServer  # adjust path if different in your project
from utils.safe_async import run_async
# our Tk table widget
from utils.dbtablewidget_tk import DBTableWidgetTk
# usar o seu gerenciador HART (preferível)
from hrt.hrt_comm import HrtComm
from hrt.hrt_transmitter import HrtTransmitter
from hrt.hrt_frame import HrtFrame

# --- HOTFIX: adiciona _fmt_machine_hex se a classe não tiver (monkey-patch) ---
if not hasattr(DBTableWidgetTk, "_fmt_machine_hex"):
    def _fmt_machine_hex(self, value, byte_size: int):
        try:
            if isinstance(value, (bytes, bytearray)):
                return " ".join(f"{b:02X}" for b in value)
            if isinstance(value, (list, tuple)) and all(isinstance(b, int) for b in value):
                return " ".join(f"{b:02X}" for b in value)
            if isinstance(value, int):
                width = max(1, int(byte_size))
                bs = value.to_bytes(width, byteorder="big", signed=False)
                return " ".join(f"{b:02X}" for b in bs)
            return str(value)
        except Exception:
            return str(value)
    DBTableWidgetTk._fmt_machine_hex = _fmt_machine_hex
# -------------------------------------------------------------------------------

class MainWindowTk(tk.Tk):
=======
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
from img.imgCaldeira import imagem_base64
from mb.mb_server import ModbusServer
from react.react_var import ReactVar
from ctrl.view import PlantViewerWindow
from db.db_types import DBState

STYLE_AM = """
QPushButton {}
QPushButton:checked { background:#2980b9; color:white; font-weight:bold; }
"""

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
        
class MainWindow(QMainWindow, Ui_MainWindow):
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775
    def __init__(self):
        super().__init__()
        print("🚀 Iniciando MainWindow...")

        self.title("HART/MODBUS – Tk UI")
        self.geometry("1100x650")

        # --- internal state/refs ---
        self.plantViewer = None  # se você tiver um viewer externo, conecte aqui
        self._running = False

        # --- create backend ---
        print("🔄 Criando ReactFactory...")
        self.reactFactory = run_async(ReactFactory.create(["HART", "MODBUS"]))
        self.HrtTransmitter = HrtTransmitter(self.reactFactory,"HART")
        print("✅ ReactFactory criado com sucesso!")

        # --- simulator wiring ---
        print("🔄 Configurando Simulador...")
        self.simulTf = SimulTf(50)
        print("✅ Simulador configurado.")

        print("🔄 Conectando sinais de tFunc...")
        # espera que isTFuncSignal tenha um .connect(callable)
        self.reactFactory.isTFuncSignal.connect(self.simulTf.tfConnect)
        print("✅ Sinais de tFunc conectados.")

        print("🔄 Registrando variáveis com tFunc...")
        for tbl in self.reactFactory.df:
            for row in self.reactFactory.df[tbl].index:
                for col in self.reactFactory.df[tbl].columns:
                    var = self.reactFactory.df[tbl].at[row, col]
                    if getattr(var, "model", None) == DBModel.tFunc:
                        self.simulTf.tfConnect(var, True)
        print("✅ Variáveis registradas com tFunc.")

        # --- Modbus server (thread controller) ---
        print("🔄 Iniciando servidor Modbus...")
        self.servidor_thread = ModbusServer(self.reactFactory)  # não inicia ainda
        # HART communication
        self.hart_comm = HrtComm(func_read=self._on_hart_frame)

        # --- UI ---
        print("🔄 Configurando UI...")
        self._build_ui()
        print("✅ UI configurada.")

<<<<<<< HEAD
=======
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
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775
        print("🔄 Carregando tabelas...")
        self.hrtTable.setBaseData(self.reactFactory, "HART")
        self.mbTable.setBaseData(self.reactFactory, "MODBUS")
        print("✅ Tabelas carregadas.")

<<<<<<< HEAD
    # --------------------- UI construction ---------------------
    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(side="top", fill="x")

        # Human/Hex selector
        view_lbl = ttk.Label(top, text="Visualização:")
        view_lbl.pack(side="left")
=======
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

        # Imagem de fundo (mantido)
        print("🔄 Configurando imagem de fundo...")
        self.processTab1.setBackgroundImageFromBase64(imagem_base64)
        print("✅ Imagem de fundo configurada.")
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775

        self.view_var = tk.StringVar(value="human")
        rb_human = ttk.Radiobutton(top, text="Humano", value="human", variable=self.view_var,
                                   command=self._on_view_change)
        rb_hex = ttk.Radiobutton(top, text="Hex", value="hex", variable=self.view_var,
                                 command=self._on_view_change)
        rb_human.pack(side="left", padx=(6, 2))
        rb_hex.pack(side="left")

<<<<<<< HEAD
        # spacing
        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)
=======
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

        # Aplica estilos visuais (igual ao View Real)
        self._wire_main_button_styles()

    # ----- estilos VISUAIS dos botões do MAIN -----
    def _wire_main_button_styles(self):
        # efeito azul enquanto pressionado
        self.pushButtonStart.pressed.connect(lambda: self.pushButtonStart.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.pushButtonStop.pressed.connect(lambda: self.pushButtonStop.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        self.pushButtonReset.pressed.connect(lambda: self.pushButtonReset.setStyleSheet("background:#2980b9; color:white; font-weight:bold;"))
        # reset volta ao amarelo quando solta
        self.pushButtonReset.released.connect(lambda: self.pushButtonReset.setStyleSheet("background:yellow; color:black; font-weight:bold;"))
        # estado inicial: parado
        self._set_main_running_visual(False)

    def _set_main_running_visual(self, running: bool):
        if running:
            # Start verde, Stop default
            self.pushButtonStart.setStyleSheet("background:#2ecc71; color:white; font-weight:bold;")
            self.pushButtonStop.setStyleSheet("")  # default
        else:
            # Stop vermelho, Start default
            self.pushButtonStart.setStyleSheet("")
            self.pushButtonStop.setStyleSheet("background:#ff2d2d; color:white; font-weight:bold;")
        # Reset permanece amarelo quando não pressionado
        if "background:yellow" not in self.pushButtonReset.styleSheet():
            self.pushButtonReset.setStyleSheet("background:yellow; color:black; font-weight:bold;")

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
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775

        # Modbus port + Start/Stop
        ttk.Label(top, text="Porta Modbus:").pack(side="left")
        self.port_var = tk.StringVar(value="502")
        self.port_entry = ttk.Entry(top, width=8, textvariable=self.port_var)
        self.port_entry.pack(side="left", padx=(4, 8))

<<<<<<< HEAD
        self.btn_start = ttk.Button(top, text="Start", command=lambda: self._startStop(True))
        self.btn_stop = ttk.Button(top, text="Stop", command=lambda: self._startStop(False))
        self.btn_start.pack(side="left", padx=(0, 4))
        self.btn_stop.pack(side="left")
        # --- objetos de backend (ajuste se já existirem) ---
        self.hart_comm = HrtComm(func_read=self._on_hart_frame)
=======
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
            # A/M button binding (sempre fora do if slider)
            botao = getattr(self, f'pbAM{device}', None)
            if botao:
                varAM = self.reactFactory.df["MODBUS"].at[f'AM_{device}', "CLP100"]
                varAM.setValue("True", DBState.humanValue, True)
                botao.clicked.connect(partial(atualizaBotao, botao, varAM))
                botao.setChecked(bool(self._sync(varAM.getValue(DBState.humanValue))))
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775

        # self.server já deve existir; se não, crie como você faz hoje
        # --- variáveis de UI ---
        self.modbus_port_var = tk.StringVar(value=self.modbus_port_var.get() if hasattr(self, "modbus_port_var") else "5020")
        self.hart_com_var    = tk.StringVar(value="")

        # --- referência à sua barra existente ---
        topbar = self.topbar if hasattr(self, "topbar") else ttk.Frame(self)   # use a mesma onde estão Start/Stop
        if not hasattr(self, "topbar"):
            topbar.pack(fill="x", padx=8, pady=6)

<<<<<<< HEAD
        # supondo que você já criou:
        # self.e_modbus  -> Entry da Porta Modbus
        # self.btn_start -> Botão Start  |  self.btn_stop -> Botão Stop
=======
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
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775

        # ====== PORTA COM (HART) — label + combobox + refresh ======
        # coloque AO LADO dos botões: usamos a próxima coluna livre
        next_col = topbar.grid_size()[0]

        ttk.Label(topbar, text="Porta COM:").grid(row=0, column=next_col,   padx=(16, 4), sticky="e")
        self.cb_hart = ttk.Combobox(topbar, textvariable=self.hart_com_var,
                                    width=10, state="readonly", values=[])
        self.cb_hart.grid(row=0, column=next_col+1, sticky="w", padx=(0,4))

        self.btn_refresh_hart = ttk.Button(topbar, text="↻", width=3, command=self._refresh_hart_ports)
        self.btn_refresh_hart.grid(row=0, column=next_col+2, sticky="w")

        # popula a lista de COMs e seleciona a preferida do config (se existir)
        self._refresh_hart_ports()

        # garanta que o estado inicial dos widgets reflita “desconectado”
        self._sync_comm_widgets(disconnected=True)

        # status text
        self.status_var = tk.StringVar(value="Parado")
        ttk.Label(top, textvariable=self.status_var).pack(side="right")

        # Notebook with two tables
        nb = ttk.Notebook(self)
        nb.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # HART tab
        tab_hart = ttk.Frame(nb)
        nb.add(tab_hart, text="HART")
        self.hrtTable = DBTableWidgetTk(tab_hart)
        self.hrtTable.pack(fill="both", expand=True)

        # MODBUS tab
        tab_mb = ttk.Frame(nb)
        nb.add(tab_mb, text="MODBUS")
        self.mbTable = DBTableWidgetTk(tab_mb)
        self.mbTable.pack(fill="both", expand=True)

    # ------------------- Callbacks & helpers -------------------
    def _on_view_change(self):
        isHuman = (self.view_var.get() == "human")
        # espelha nas duas tabelas
        self.hrtTable.changeType(isHuman)
        self.mbTable.changeType(isHuman)
        
    def _refresh_hart_ports(self):
        """Atualiza a lista de COMs usando HrtComm.available_ports."""
        try:
            ports = list(self.hart_comm.available_ports)
        except Exception:
            ports = []
        if not ports:
            ports = [f"COM{i}" for i in range(1, 33)]
        self.cb_hart["values"] = ports
        if ports and not self.hart_com_var.get():
            self.hart_com_var.set(ports[0])


    def _sync_comm_widgets(self, connected=False, disconnected=False):
        """Habilita/desabilita controles de acordo com o estado da comunicação."""
        # defina “running” como o seu critério de conexão atual
        running = connected or (getattr(self, "server", None) and getattr(self.server, "running", False) and not disconnected)

        # botões
        self.btn_start.configure(state="disabled" if running else "normal")
        self.btn_stop.configure(state="normal" if running else "disabled")

        # Porta Modbus (Entry) travada quando conectado
        if hasattr(self, "e_modbus"):
            self.e_modbus.configure(state="disabled" if running else "normal")

        # Porta COM (Combobox) travada quando conectado
        if hasattr(self, "cb_hart"):
            self.cb_hart.configure(state="disabled" if running else "readonly")
        if hasattr(self, "btn_refresh_hart"):
            self.btn_refresh_hart.configure(state="disabled" if running else "normal")

    def _on_hart_frame(self, hex_str: str):
        def process_on_ui(hrt_comm):
            print(hex_str)
            frame_to_write: str = (self.HrtTransmitter.response(HrtFrame(hex_str))).frame
            if frame_to_write != "" and hrt_comm.write_frame(frame_to_write):
                print(f"Wrote frame: {frame_to_write}")
            else:
                print("Failed to write frame")
        self.after(0, process_on_ui, self.hart_comm)  # joga para a main thread do Tk
        
    def _toggle_comm_inputs(self, disable: bool):
        """Habilita/desabilita os controles de entrada durante a conexão."""
        # Porta Modbus (Entry)
        try:
            self.port_entry.configure(state="disabled" if disable else "normal")
        except Exception:
            pass
        # Porta COM (Combobox) + botão refresh
        try:
            self.cb_hart.configure(state="disabled" if disable else "readonly")
        except Exception:
            pass
        try:
            self.btn_refresh_hart.configure(state="disabled" if disable else "normal")
        except Exception:
            pass

    def _startStop(self, state: bool):
        if state:
            try:
                port = int(self.port_var.get().strip())
            except ValueError:
                messagebox.showerror("Porta inválida", "Informe um número de porta válido, ex.: 5020", parent=self)
                return
            try:
                self.servidor_thread.start(port=port)
            except Exception as e:
                messagebox.showerror("Erro ao iniciar Modbus", str(e), parent=self)
                return

            hart_port = (self.hart_com_var.get() or "").strip()
            try:
                if hart_port:
                    self.hart_comm.port = hart_port
                ok = self.hart_comm.connect(port=hart_port, func_read=self._on_hart_frame)
            except Exception as e:
                ok = False
                err = str(e)
            if not ok:
                try:
                    self.servidor_thread.stop()
                except Exception:
                    pass
                detail = err if 'err' in locals() else getattr(getattr(self.hart_comm, "_comm_serial", None), "last_error", "") or ""
                messagebox.showerror(
                    "Erro ao iniciar HART",
                    f"Não foi possível abrir a porta HART {hart_port or '(config)'}."
                    f" Verifique a COM e tente novamente. Detalhes: {detail}",
                    parent=self
                )
                return

<<<<<<< HEAD
            self._toggle_comm_inputs(True)
        else:
            try:
                self.servidor_thread.stop()
            except Exception:
                pass
            try:
                self.hart_comm.disconnect()
            except Exception:
                pass
            self._toggle_comm_inputs(False)

        try:
            self.simulTf.start(state)
        except Exception:
            pass
        self._set_main_running_visual(state)
        if getattr(self, "plantViewer", None) and hasattr(self.plantViewer, "sync_running_state"):
            try:
                self.plantViewer.sync_running_state(state)
            except Exception:
                pass

    def _set_main_running_visual(self, running: bool):
        self._running = running
        if running:
            self.status_var.set("Rodando")
            self.btn_start.state(["disabled"])
            self.btn_stop.state(["!disabled"])
        else:
            self.status_var.set("Parado")
            self.btn_start.state(["!disabled"])
            self.btn_stop.state(["disabled"])
            
if __name__ == "__main__":
    app = MainWindowTk()
    app.mainloop()
=======

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
>>>>>>> 00d4c1443074401b5152a1f726c9a82a1e096775
