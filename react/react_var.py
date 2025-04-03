from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from PySide6.QtCore import QObject, Signal, Slot
from db.db_types import DBState, DBModel
from asteval import Interpreter
import numpy as np
import random
import math
import re

class ReactVar(QObject):
    valueChangedSignal      = Signal(QObject)  # Sinal emitido quando o valor muda
    funcTokenSignal         = Signal(list,bool)
    isTFuncSignal           = Signal(QObject,bool)
    _value            = None  # Valor em DBState.humanValue
    inputValue        = None  # Valor em DBState.humanValue   
    model             = None     
    _func             = None  # Func que precisa ser resolvida
    _tFunc            = None  # tFunc que precisa ser resolvida
    _tokens           = ""    # Armazena de quais variaveis ele depende
    _evaluator        = Interpreter()
    
    def __init__(self, tableName: str, rowName: str, colName: str, reactDB: "ReactDB"):
        super().__init__()
        self.tableName = tableName
        self.rowName   = rowName
        self.colName   = colName
        self.reactDB   = reactDB

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
            self._checkModel(DBModel.Func)             
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
        return self._func[1:]        
            
    def setFunc(self, func):
        if self._func != func:
            self._checkModel(DBModel.Func)         
            self._tFunc = None
            self.model = DBModel.Func   
            self.start_tokens(func)
            self._value = self.evaluate_expression(func)                
            self._func = func      
        
    def getTFunc(self):
        if self._tFunc == None:
            self._startDataBase()         
        return self._tFunc           
            
    def setTFunc(self, tFunc):
        if self._tFunc != tFunc:
            self._checkModel(DBModel.tFunc)     
            self.model = DBModel.tFunc
            self._value = 0.0
            self._tFunc  = tFunc
            _, __, self._func, ___, ____ = tFunc.split(",")
            self.start_tokens(self._func)
            self.inputValue = self.evaluate_expression(self._func)                            
            self.isTFuncSignal.emit(self, True)         

    def _checkModel(self, newModel):
        OldModel = self.model
        if OldModel != None or (OldModel == DBModel.Func and newModel != DBModel.Func) or (OldModel == DBModel.tFunc and newModel != DBModel.tFunc): # Se antes era e agora não é mais 
            self.funcTokenSignal.emit(self._tokens, False)
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

    def start_tokens(self, func: str):  
        tokens = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', func)          
        if self._tokens != tokens:   
            # Inicializa apenas uma vez os módulos comuns
            self._evaluator.symtable.clear()
            self._evaluator.symtable.update({
                "math": math,
                "np": np,
                "random": random
            })                  
            for tokenAtual in tokens:
                try:
                    tableName, col, row = tokenAtual.split(".")
                    var_val = self.reactDB.df[tableName].loc[row, col].getValue()
                    if var_val is not None:
                        self._evaluator.symtable[tokenAtual.replace(".", "_")] = var_val
                except Exception as e:
                    print(f"Erro ao acessar variável {tokenAtual}: {e}")
                    continue
            self._tokens = tokens              
            self.funcTokenSignal.emit(self._tokens, True)        
        
    def evaluate_expression(self, func: str):
        expression_sanitized = re.sub(r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2_\3', func)
        result = self._evaluator(expression_sanitized)
        return float(result) if isinstance(result, (int, float)) else 0.0

    @Slot()                   
    def bindToSlot(self, data: "ReactVar", isConnect: bool):  
        if isConnect == True:      
            data.valueChangedSignal.connect(self._update_from_other_slot)
        else:
            try:
                data.valueChangedSignal.disconnect(self._update_from_other_slot)
            except (TypeError, RuntimeError):
                print("Tentativa de Desconectar Sinal que não estava Conectado")
                pass  # já estava desconectado; nada a fazer
        
    @Slot()
    def _update_from_other_slot(self, data: "ReactVar"):
        self._evaluator.symtable[f'{data.tableName}_{data.rowName}_{data.colName}'] = data.getValue()
        
        result = self.evaluate_expression(self._func)
        if self.model == DBModel.tFunc: 
            self.inputValue = result
        else:
            self._value = result
            self.valueChangedSignal.emit(self)