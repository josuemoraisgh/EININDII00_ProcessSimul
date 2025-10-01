
import tkinter as tk
from tkinter import ttk

class TFuncDialog(tk.Toplevel):
    def __init__(self, parent, title='Dialog', num='', den='', input_='', delay=''):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.result = None
        self.minsize(600, 180)

        outer = ttk.Frame(self, padding=10)
        outer.pack(fill='both', expand=True)

        row1 = ttk.Frame(outer)
        row1.pack(fill='x')
        ttk.Label(row1, text='Num:').pack(side='left')
        self.e_num = ttk.Entry(row1)
        self.e_num.pack(side='left', fill='x', expand=True, padx=(6,10))
        self.e_num.insert(0, str(num or ''))

        ttk.Label(row1, text='Den:').pack(side='left')
        self.e_den = ttk.Entry(row1)
        self.e_den.pack(side='left', fill='x', expand=True, padx=(6,0))
        self.e_den.insert(0, str(den or ''))

        row2 = ttk.Frame(outer)
        row2.pack(fill='both', expand=True, pady=(8,0))

        left = ttk.Frame(row2)
        left.pack(side='left', fill='both', expand=True)
        ttk.Label(left, text='input:').pack(anchor='w')
        self.t_input = tk.Text(left, height=4, wrap='word', undo=True)
        self.t_input.pack(fill='both', expand=True, pady=(2,0))
        self.t_input.insert('1.0', input_ or '')

        right = ttk.Frame(row2)
        right.pack(side='left', fill='y', padx=(10,0))
        ttk.Label(right, text='Atraso:').pack(anchor='w')
        self.e_delay = ttk.Entry(right, width=8)
        self.e_delay.pack(anchor='w', pady=(2,0))
        self.e_delay.insert(0, str(delay or ''))

        btns = ttk.Frame(outer)
        btns.pack(fill='x', pady=(8,0))
        ttk.Button(btns, text='OK', command=self._ok).pack(side='right', padx=4)
        ttk.Button(btns, text='Cancelar', command=self._cancel).pack(side='right')

        self.bind('<Control-Return>', lambda e: self._ok())
        self.bind('<Escape>', lambda e: self._cancel())

        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.wait_visibility()
        self.focus()

    def _ok(self):
        self.result = (
            self.e_num.get(),
            self.e_den.get(),
            self.e_delay.get(),
            self.t_input.get('1.0', 'end-1c'),
        )
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    @classmethod
    def ask(cls, parent=None, title='Dialog', num='', den='', input_='', delay=''):
        win = cls(parent or tk._default_root, title=title, num=num, den=den, input_=input_, delay=delay)
        win.wait_window()
        return win.result
