
import tkinter as tk
from tkinter import ttk

class ValueDialog(tk.Toplevel):
    def __init__(self, parent, title='Dialog', label='Value:', initial=''):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=label).grid(row=0, column=0, padx=(10, 6), pady=10, sticky='w')
        self.entry = ttk.Entry(self)
        self.entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky='ew')
        if initial is not None:
            self.entry.insert(0, str(initial))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky='e')
        ok = ttk.Button(btns, text='OK', command=self._ok)
        cancel = ttk.Button(btns, text='Cancelar', command=self._cancel)
        ok.grid(row=0, column=0, padx=4)
        cancel.grid(row=0, column=1)

        self.bind('<Return>', lambda e: self._ok())
        self.bind('<Escape>', lambda e: self._cancel())

        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.wait_visibility()
        self.focus()

    def _ok(self):
        self.result = self.entry.get()
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    @classmethod
    def ask(cls, parent=None, title='Dialog', label='Value:', initial=''):
        win = cls(parent or tk._default_root, title=title, label=label, initial=initial)
        win.wait_window()
        return win.result
