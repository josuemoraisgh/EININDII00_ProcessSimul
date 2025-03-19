from PySide6.QtCore import QObject, Signal
from db.storage_sqlite import Storage, HrtState  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from asteval import Interpreter
from typing import Union
import numpy as np
import pandas as pd
import re

class HrtReactiveVariable(QObject):
    valueChanged = Signal(object)  # Sinal emitido quando o valor muda

    def __init__(self, rowName, colName, hrt_storage: Storage):
        self._rowName = rowName
        self._colName = colName
        # state = 0 -> MachineValue, state = 1 -> HumanValue, state = 2 -> OriginValue
        self._hrt_storage = hrt_storage 

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
    
    @property # metodo getter 
    def sharedState(self):
        return self._hrt_storage.state
    
    @sharedState.setter # metodo setter 
    def sharedState(self, state: HrtState):
        self._hrt_storage.state = state 

    @property # metodo getter 
    def value(self):
        self._getVariable(self._rowName, self._colName, self._sharedState.value)

    @value.setter # metodo setter 
    def value(self, value):
        if self._rowName == self._colName or self._colName == 'NAME':
            self._hrt_storage.df.loc[self._rowName,0] = value
        else:
            modelAntes = self._getDataModel(self._rowName, self._colName).find("tFunc") != -1 # Se antes era tf
            modelAgora = self._getModel(value).find("tFunc") != -1 # Se agora é tf
            if not modelAntes and modelAgora: self._hrt_storage.tf_dict[self._rowName, self._colName] = 0
            if modelAntes and not modelAgora: self._hrt_storage.tf_dict.pop((self._rowName, self._colName), None)
            if self._hrt_storage.state == HrtState.humanValue and self._getDataModel(self._rowName, self._colName).find("Func") == -1:
                return self._hrt_storage.setStrData(self._rowName, self._colName, hrt_type_hex_from(value, self._hrt_storage.getStrData(self._rowName, "TYPE"), int(self._hrt_storage.getStrData(self._rowName, "BYTE_SIZE"))))
            else:
                return self._hrt_storage.setStrData(self._rowName, self._colName, str(value))    
        self.valueChanged.emit(value)
    
    def connect(self, update_function):
        self.valueChanged.connect(update_function)
        
    def bind_to(self, other_variable: "HrtReactiveVariable"):        
        other_variable.connect(self._update_from_other)
    
    def _update_from_other(self):
        self.valueChanged.emit(self._value)
    
    def _getModel(self, value: str) -> str:   
        if value.startswith('@'):
            return "Func"
        elif value.startswith('$'):
            return "tFunc"
        else:
            return "Value"
               
    def _getDataModel(self, rowName: str, colName: str) -> str:
        value = self._hrt_storage.getStrData(rowName,colName)
        return self._getModel(value)
    
    def _getVariable(self, rowName: str, colName: str, state: HrtState):
        if rowName == colName or colName == 'NAME':
            return rowName
        else: 
            value = self._hrt_storage.getStrData(rowName, colName)
            dataModel = self._getDataModel(rowName, colName)
            if not colName in ["NAME", "TYPE", "BYTE_SIZE"]:
                if dataModel == "Func":
                    return self._evaluate_expression(value, rowName, colName, state.value)
                elif dataModel == "tFunc": 
                    if state.value == HrtState.humanValue:
                        return self.tf_dict[rowName, colName]
                    elif state.value == HrtState.machineValue:
                        return hrt_type_hex_from(self.tf_dict[rowName, colName], super().getStrData(rowName, "TYPE"), super().getStrData(rowName, "BYTE_SIZE"))
                    else:
                        return value
                else: 
                    if state.value == HrtState.humanValue:
                        return hrt_type_hex_to(super().getStrData(rowName, colName), super().getStrData(rowName, "TYPE"))
                    else:
                        return value
    
    def _evaluate_expression(self, func: str, rowName: str, colName: str, state: HrtState) -> Union[float, str]:
        evaluator = Interpreter()
        func = func[1:]  # Remove o caractere '@' inicial
        tokens = re.findall(r'[A-Za-z_]\w*', func)
        for token in tokens:
            # Fazer no futuro: Checar se todas as variaves são do mesmo tipo ?
            var_val = self._getVariable(token, colName, False)
            if var_val is not None:
                evaluator.symtable[token] = var_val
        try:
            result = evaluator(func)
            if state == HrtState.machineValue:
                return hrt_type_hex_from(result, super().getStrData(rowName, "TYPE"), int(super().getStrData(rowName, "BYTE_SIZE")))
            else:    
                return result
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if state == HrtState.machineValue:
                return "00".zfill(2*int(super().getStrData(rowName, "BYTE_SIZE")))
            else:
                return 0.0