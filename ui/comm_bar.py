
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

class CommBar(ttk.Frame):
    """Barra de comunicação: Modbus + HART.
       - Entry Modbus (porta)
       - Combobox HART COM
       - Ativar/Desativar
       - Desabilita widgets quando conectado
    """
    def __init__(self, master, controller, *, initial_modbus_port="502"):
        super().__init__(master)
        self.controller = controller
        self.modbus_port_var = tk.StringVar(value=str(initial_modbus_port))
        self.hart_com_var    = tk.StringVar(value="")

        ttk.Label(self, text="Modbus porta:").grid(row=0, column=0, sticky="w")
        self.e_modbus = ttk.Entry(self, textvariable=self.modbus_port_var, width=8)
        self.e_modbus.grid(row=0, column=1, padx=(4, 12), sticky="w")

        self.btn_start = ttk.Button(self, text="Ativar", command=self._start)
        self.btn_stop  = ttk.Button(self, text="Desativar", command=self._stop)
        self.btn_start.grid(row=0, column=2, padx=2)
        self.btn_stop.grid(row=0, column=3, padx=2)

        ttk.Label(self, text="HART COM:").grid(row=0, column=4, padx=(16, 4), sticky="e")
        self.cb_hart = ttk.Combobox(self, textvariable=self.hart_com_var,
                                    state="readonly", width=10, values=[])
        self.cb_hart.grid(row=0, column=5, sticky="w", padx=(0,4))

        self.btn_refresh = ttk.Button(self, text="↻", width=3, command=self._refresh_hart_ports)
        self.btn_refresh.grid(row=0, column=6, sticky="w")

        self.columnconfigure(7, weight=1)
        self._refresh_hart_ports()
        self._sync_widgets(disconnected=True)

    def _refresh_hart_ports(self):
        try:
            ports = self.controller.hart.list_ports()
        except Exception:
            ports = []
        self.cb_hart["values"] = ports
        try:
            cfg = self.controller.hart.load_config() or {}
            pref = cfg.get("port")
        except Exception:
            pref = None
        if pref and pref in ports:
            self.hart_com_var.set(pref)
        elif ports and not self.hart_com_var.get():
            self.hart_com_var.set(ports[0])

    def _start(self):
        modbus_port = self.modbus_port_var.get().strip()
        hart_port   = (self.hart_com_var.get() or "").strip() or None
        try:
            if hart_port:
                self.controller.hart.set_port(hart_port)
        except Exception:
            pass
        self.controller.start(modbus_port=modbus_port, hart_port=hart_port)
        self._sync_widgets(connected=True)

    def _stop(self):
        self.controller.stop()
        self._sync_widgets(disconnected=True)

    def _sync_widgets(self, connected=False, disconnected=False):
        running = connected or (getattr(self.controller, "running", False) and not disconnected)
        self.btn_start.configure(state="disabled" if running else "normal")
        self.btn_stop.configure(state="normal" if running else "disabled")
        self.e_modbus.configure(state="disabled" if running else "normal")
        self.cb_hart.configure(state="disabled" if running else "readonly")
        self.btn_refresh.configure(state="disabled" if running else "normal")
