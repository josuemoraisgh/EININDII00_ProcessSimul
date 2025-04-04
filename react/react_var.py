from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from PySide6.QtCore import QObject, Signal, Slot
from db.db_types import DBState, DBModel
from asteval import Interpreter
from numpy import exp, log
import random
import math
import re

class ReactVar(QObject):
    valueChangedSignal      = Signal(QObject)  # Sinal emitido quando o valor muda
    isTFuncSignal           = Signal(QObject,bool)
    _value            = None  # Valor em DBState.humanValue
    inputValue        = None  # Valor em DBState.humanValue   
    model             = None     
    _func             = None  # Func que precisa ser resolvida
    _tFunc            = None  # tFunc que precisa ser resolvida
    _tokens           = ""    # Armazena de quais variaveis ele depende
    
    def __init__(self, tableName: str, rowName: str, colName: str, reactDB: "ReactDB"):
        super().__init__()
        self._evaluator = Interpreter()
        self.tableName  = tableName
        self.rowName    = rowName
        self.colName    = colName
        self.reactDB    = reactDB

    def type(self, tableName = None, rowName = None):
        if tableName == None or rowName == None:
            tableName = self.tableName
            rowName   = self.rowName
        return self.reactDB.storage.getData(tableName, rowName, 'TYPE')
        
    def byteSize(self, tableName = None, rowName = None):
        if tableName == None or rowName == None:
            tableName = self.tableName
            rowName   = self.rowName        
        return int(self.reactDB.storage.getData(tableName, rowName, 'BYTE_SIZE'))

    @staticmethod 
    def translate(value, type: str, byteSize: int, stateDesejado: DBState, stateAtual: DBState = DBState.humanValue):        
        if stateDesejado == stateAtual or (stateDesejado == DBState.originValue and stateAtual == DBState.machineValue) or (stateDesejado == DBState.machineValue and stateAtual == DBState.originValue):
            return value
        if stateDesejado == DBState.humanValue:
            return hrt_type_hex_to(value, type)
        # if stateDesejado == DBState.machineValue:
        return hrt_type_hex_from(value, type,  byteSize)
       
    def getModel(self, value=None) -> str:
        if value is None: 
            value = self.reactDB.storage.getData(self.tableName, self.rowName, self.colName)
        if isinstance(value,str):            
            if value.startswith('@'):
                return DBModel.Func
            elif value.startswith('$'):
                return DBModel.tFunc
        return DBModel.Value    
    
    def getValue(self, stateDesejado : DBState = DBState.humanValue):
        if self._value == None:
            self._startDataBase()
        if self.colName in ['NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS']:
            return self._value                                   
        return self.translate(self._value,self.type(),self.byteSize(),stateDesejado,DBState.humanValue)            
            
    def setValue(self, value, stateAtual : DBState = DBState.humanValue):
        if self.colName in ['NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS']:
            valueAux = value           
        else:
            self._checkModel(DBModel.Value)             
            valueAux = self.translate(value, self.type(), self.byteSize(), DBState.humanValue, stateAtual)  
        self._func = None
        self._tFunc = None
        isChanged = self._value != valueAux
        self._value = valueAux   
        self.model = DBModel.Value            
        if isChanged: self.valueChangedSignal.emit(self)

    def getFunc(self):
        if self._func == None:
            self._startDataBase()         
        return self._func       
            
    def setFunc(self, func):
        if self._func != func:
            self._checkModel(DBModel.Func) # Ele tem que ser ante do self._tFunc = None         
            self._tFunc = None
            self.model = DBModel.Func    
            self._startFunc(func) # Ele tem que ser o ultimo             
     
    def getTFunc(self):
        if self._tFunc == None:
            self._startDataBase()         
        return self._tFunc           
            
    def setTFunc(self, tFunc):
        if self._tFunc != tFunc:
            self._checkModel(DBModel.tFunc) # Ele tem que ser ante do self._tFunc = None    
            self.model = DBModel.tFunc
            self._value = 5.877471754111438e-39
            self._tFunc  = tFunc
            _, __, inpValue, ___, ____ = tFunc.split(",")
            self._startFunc(inpValue[1:]) # Ele tem que ser a penultima ante do sinal                         
            self.isTFuncSignal.emit(self, True)         

    def _checkModel(self, newModel):
        OldModel = self.model
        if OldModel != None or (OldModel == DBModel.Func and newModel != DBModel.Func) or (OldModel == DBModel.tFunc and newModel != DBModel.tFunc): # Se antes era e agora não é mais 
            self._connectTokens(self._tokens, False)
            if OldModel == DBModel.tFunc and newModel != DBModel.tFunc:
                self.isTFuncSignal.emit(self, False)        
        
    def _startDataBase(self): 
        dataBase = self.reactDB.storage.getData(self.tableName,self.rowName,self.colName)
        newModel = self.getModel(dataBase)                                              
        if newModel == DBModel.Value:
            self.setValue(dataBase, DBState.machineValue)
        elif newModel == DBModel.Func: # Se agora Func
            self.setFunc(dataBase[1:])                    
        elif newModel == DBModel.tFunc: # Se agora é tF
            self.setTFunc(dataBase[1:])

    def _startFunc(self, func: str):  
        self._func = func
        tokens = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', func)          
        if self._tokens != tokens:   
            # Inicializa apenas uma vez os módulos comuns
            self._evaluator.symtable.clear()
            self._evaluator.symtable.update({
                "math": math,
                "exp": exp,
                "random": random,
                "log": log
            })                  
            self._connectTokens(tokens, True)             
            self._tokens = tokens                   
        
    def _connectTokens(self, tokens: list, isconnect = True):          
        if self._tokens != tokens:                    
            for token in tokens:
                tableName, col, row = token.split(".")
                otherData: ReactVar = self.reactDB.df[tableName].loc[row, col]
                if isconnect == True:
                    self._evaluator.symtable[f'{tableName}_{col}_{row}'] = otherData.getValue()
                    otherData.valueChangedSignal.connect(self._update_from_other_slot) 
                else:
                    otherData.valueChangedSignal.disconnect(self._update_from_other_slot) 
            self._tokens = tokens
            if isconnect == True:
                result = self._evaluate_expression(self._func)
                if self.model == DBModel.tFunc: 
                    self.inputValue = result
                else:
                    self._value = result
                    self.valueChangedSignal.emit(self)
        
    def _evaluate_expression(self, func: str):
        expression_sanitized = re.sub(r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2_\3', func)
        result = self._evaluator(expression_sanitized)
        return float(result)
    
    @Slot()
    def _update_from_other_slot(self, data: "ReactVar"):
        self._evaluator.symtable[f'{data.tableName}_{data.colName}_{data.rowName}'] = data.getValue()
        result = self._evaluate_expression(self._func)
        if self.model == DBModel.tFunc: 
            self.inputValue = result
        else:
            self._value = result
            self.valueChangedSignal.emit(self)