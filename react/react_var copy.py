from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from PySide6.QtCore import QObject, Signal, Slot
from react.referencia import RefVar
from db.db_types import DBState, DBModel
from db.db_storage import DBStorage
from asteval import Interpreter
import numpy as np
import math
import random
import re

class ReactVar(QObject):
    valueChanged    = Signal()  # Sinal emitido quando o valor muda
    funcToken       = Signal(list,bool)
    tFuncToken      = Signal(list,bool)
    _value          = 0.0  # Valor em DBState.humanValue
    _func           = ""   # Func que precisa ser resolvida
    _tFunc          = ""   # tFunc que precisa ser resolvida
    _model          = DBModel.Value
    _tokens         = ""   # Armazena de quais variaveis ele depende

    def __init__(self, tableName: str, rowName: str, colName: str, storage: DBStorage, tf_ref: RefVar):
        super().__init__()
        self._tableName = tableName
        self._rowName   = rowName
        self._colName   = colName
        self.storage    = storage
        self.model      = self.getDataModel(tableName, rowName, colName)

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
 
    def type(self):
        return self.storage.getData(self._tableName, self._rowName, 'TYPE')
 
    def getValue(self, state : DBState = DBState.originValue):
        return self._value

    def setValue(self, value, state : DBState = DBState.originValue):
        if self._rowName == self._colName or self._colName == 'NAME':
            self.storage.dataFrame(self._tableName).loc[self._rowName,0] = value
        else:
            modelAntes = self.model
            modelAgora = self.getModel(value)
            
            if modelAntes == DBModel.Func and modelAgora != DBModel.Func: # Se antes era Func e agora não é mais 
                self._func = value
                self.funcToken.emit(self.tokens, False)
            if modelAntes != DBModel.Func and modelAgora == DBModel.Func: # Se antes era Func e agora não é mais 
                self._func   = value
                self._tokens = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', value)
                self.funcToken.emit(self.tokens, True)
                
            if modelAntes == DBModel.tFunc and modelAgora != DBModel.tFunc: # Se antes era tF e agora não é 
                self._func = value
                self.funcToken.emit(self.tokens, False)
            if modelAntes != DBModel.tFunc and modelAgora == DBModel.tFunc: # Se antes não era tF e agora é
                self._tFunc = value
                _, __, self._func, ___, ____ = value.split(",")
                self._tokens = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', self._func)
                self.funcToken.emit(self.tokens, True)
                self.tFuncToken.emit(self._tableName, self._rowName, self._colName)
                
            if state == DBState.humanValue and modelAgora != DBModel.tFunc:
                value = hrt_type_hex_from(value, self.storage.getData(self._tableName, self._rowName, "TYPE"), int(self.storage.getData(self._tableName, self._rowName, "BYTE_SIZE")))
                self.storage.setData(self._tableName, self._rowName, self._colName, value)
            else:
                self.storage.setData(self._tableName, self._rowName, self._colName, str(value))
        self.model = modelAgora
        self.valueChanged.emit(value)
        
    def bind_to(self, signalOtherVar: Signal, isConnect: bool):  
        if isConnect == True:      
            signalOtherVar.connect(self._update_from_other)
        else:
            signalOtherVar.disconnect(self._update_from_other)
        
    @Slot()
    def _update_from_other(self):
        self.valueChanged.emit()
        