
import tkinter as tk
from tkinter import ttk

class FuncDialog(tk.Toplevel):
    def __init__(self, parent, title='Dialog', label='Func:', initial=''):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.result = None
        self.minsize(500, 140)

        container = ttk.Frame(self, padding=10)
        container.pack(fill='both', expand=True)

        row = ttk.Frame(container)
        row.pack(fill='both', expand=True)
        ttk.Label(row, text=label).pack(side='left', anchor='n', pady=(2,0))
        self.text = tk.Text(row, height=4, wrap='word', undo=True)
        self.text.pack(side='left', fill='both', expand=True, padx=(6,0))
        self.text.insert('1.0', initial or '')

        btns = ttk.Frame(container)
        btns.pack(fill='x', pady=(8,0))
        ttk.Label(btns, text='Dica: use as sugestões definidas no seu autocomplete.', foreground='#666').pack(side='left')
        ttk.Button(btns, text='OK', command=self._ok).pack(side='right', padx=4)
        ttk.Button(btns, text='Cancelar', command=self._cancel).pack(side='right')

        self.bind('<Control-Return>', lambda e: self._ok())
        self.bind('<Escape>', lambda e: self._cancel())

        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.wait_visibility()
        self.focus()

    def _ok(self):
        self.result = self.text.get('1.0', 'end-1c')
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    @classmethod
    def ask(cls, parent=None, title='Dialog', label='Func:', initial=''):
        win = cls(parent or tk._default_root, title=title, label=label, initial=initial)
        win.wait_window()
        return win.result
