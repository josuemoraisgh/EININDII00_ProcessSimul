from PySide6.QtCore import QObject, Signal, Slot
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from
from db.db_types import DBState, DBModel
from asteval import Interpreter
from numpy import exp, log
import random, math, re

class ReactVar(QObject):
    valueChangedSignal = Signal(QObject)
    isTFuncSignal      = Signal(QObject, bool)

    def __init__(self, tableName: str, rowName: str, colName: str, reactDB):
        super().__init__()
        self.tableName  = tableName
        self.rowName    = rowName
        self.colName    = colName
        self.reactDB    = reactDB
        self._evaluator = Interpreter()
        self._value     = None
        self.inputValue = None
        self.model      = None
        self._func      = None
        self._tFunc     = None
        self._tokens    = []

    def type(self, tableName=None, rowName=None):
        if tableName is None or rowName is None:
            tableName, rowName = self.tableName, self.rowName
        return self.reactDB.storage.getData(tableName, rowName, 'TYPE')

    def byteSize(self, tableName=None, rowName=None):
        if tableName is None or rowName is None:
            tableName, rowName = self.tableName, self.rowName
        return int(self.reactDB.storage.getData(tableName, rowName, 'BYTE_SIZE'))

    @staticmethod
    def translate(value, type_: str, byteSize: int, desiredState: DBState, currentState: DBState = DBState.humanValue):
        if desiredState == currentState or \
           (desiredState == DBState.originValue and currentState == DBState.machineValue) or \
           (desiredState == DBState.machineValue and currentState == DBState.originValue):
            return value
        if desiredState == DBState.humanValue:
            return hrt_type_hex_to(value, type_)
        return hrt_type_hex_from(value, type_, byteSize)

    def getModel(self, rawValue=None) -> DBModel:
        if rawValue is None:
            rawValue = self.reactDB.storage.getData(self.tableName, self.rowName, self.colName)
        if isinstance(rawValue, str):
            if rawValue.startswith('@'):
                return DBModel.Func
            elif rawValue.startswith('$'):
                return DBModel.tFunc
        return DBModel.Value

    def getValue(self, desiredState: DBState = DBState.humanValue):
        if self._value is None:
            self._start_from_db()
        if self._value is None:
            # ainda sem valor após buscar do banco -> devolve zero
            return 0
        if self.colName in ('NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS'):
            return self._value
        return self.translate(self._value, self.type(), self.byteSize(), desiredState)


    def setValue(self, value, currentState: DBState = DBState.humanValue):
        if self.colName in ('NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS'):
            converted = value
        else:
            self._ensure_model(DBModel.Value)
            converted = self.translate(value, self.type(), self.byteSize(), DBState.humanValue, currentState)
        self._func  = None
        self._tFunc = None
        changed = (self._value != converted)
        self._value = converted
        self.model  = DBModel.Value
        if changed:
            self.valueChangedSignal.emit(self)

    def getFunc(self):
        if self._func is None:
            self._start_from_db()
        return self._func

    def setFunc(self, func: str):
        if func != self._func:
            self._ensure_model(DBModel.Func)
            self._tFunc = None
            self.model  = DBModel.Func
            self._init_func(func)

    def getTFunc(self):
        if self._tFunc is None:
            self._start_from_db()
        return self._tFunc

    def setTFunc(self, tfunc: str):
        if tfunc != self._tFunc:
            self._ensure_model(DBModel.tFunc)
            self.model  = DBModel.tFunc
            self._value = 0.0
            self._tFunc = tfunc
            _, _, _, inp = tfunc.split(',')
            self._init_func(inp.strip()[1:])
            self.isTFuncSignal.emit(self, True)

    def _ensure_model(self, newModel: DBModel):
        old = self.model
        if old is not None and old != newModel:
            self._disconnect_tokens()
            if old == DBModel.tFunc:
                self.isTFuncSignal.emit(self, False)

    def _start_from_db(self):
        raw   = self.reactDB.storage.getData(self.tableName, self.rowName, self.colName)
        model = self.getModel(raw)
        if model == DBModel.Value:
            self.setValue(raw, DBState.machineValue)
        elif model == DBModel.Func:
            self.setFunc(raw[1:])
        else:
            self.setTFunc(raw[1:])

    def _init_func(self, func: str):
        self._func = func
        tokens  = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', func)
        if tokens != self._tokens:
            self._evaluator.symtable.clear()
            self._evaluator.symtable.update({
                'math': math, 'exp': exp, 'random': random, 'log': log, 'abs': abs
            })
            self._tokens = tokens
            self._connect_tokens(tokens)

    def _connect_tokens(self, tokens: list[str]):
        for tok in tokens:
            tbl, col, row = tok.split('.')
            other: ReactVar = self.reactDB.df[tbl].at[row, col]
            key = f'{tbl}_{col}_{row}'
            # tenta obter valor; se for None ou lançar, pula este token
            try:
                v = other.getValue()
            except Exception:
                continue
            if v is None:
                continue
            self._evaluator.symtable[key] = v
            other.valueChangedSignal.connect(self._on_other_changed)
        result = self._evaluate(self._func)
        if self.model == DBModel.tFunc:
            self.inputValue = result
        else:
            self._value = result
            self.valueChangedSignal.emit(self)

    def _disconnect_tokens(self):
        for tok in self._tokens:
            tbl, col, row = tok.split('.')
            other: ReactVar = self.reactDB.df[tbl].at[row, col]
            other.valueChangedSignal.disconnect(self._on_other_changed)
        self._tokens = []

    def _evaluate(self, expr: str) -> float:
        expression_sanitized = re.sub(r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2_\3', expr)
        result = self._evaluator(expression_sanitized)
        if result is None:
            # Erro mais claro: veja qual expressão falhou
            raise RuntimeError(
                f"[ReactVar] Falha ao avaliar '{expr}': "
                "Interpreter retornou None"
            )
        try:
            return float(result)
        except (ValueError, TypeError):
            raise RuntimeError(
                f"[ReactVar] Resultado inválido para '{expr}': {result!r}"
            )

    @Slot(object)
    def _on_other_changed(self, var):
        key = f'{var.tableName}_{var.colName}_{var.rowName}'
        self._evaluator.symtable[key] = var.getValue()
        val = self._evaluate(self._func)
        if self.model == DBModel.tFunc:
            self.inputValue = val
        else:
            self._value = val
            self.valueChangedSignal.emit(self)