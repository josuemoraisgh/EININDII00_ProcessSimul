from PySide6.QtCore import QObject, Signal, Slot
from db.storage_sqlite import Storage, HrtState  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from asteval import Interpreter
from typing import Union, Callable
import re

class HrtReactiveVariable(QObject):
    valueChanged = Signal()  # Sinal emitido quando o valor muda
    expressionToken = Signal(list)

    def __init__(self, rowName, colName, hrt_storage: Storage):
        super().__init__()
        self._rowName = rowName
        self._colName = colName
        # state = 0 -> MachineValue, state = 1 -> HumanValue, state = 2 -> OriginValue
        self._hrt_storage = hrt_storage
        self._tokens = ""

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
 
    def type(self):
        return self.getVariable(self._rowName, 'TYPE')
 
    def value(self, state : HrtState = HrtState.originValue):
        return self.getVariable(self._rowName, self._colName, state)

    def setValue(self, value, state : HrtState = HrtState.originValue):
        if self._rowName == self._colName or self._colName == 'NAME':
            self._hrt_storage.df.loc[self._rowName,0] = value
        else:
            modelAntes = self.getDataModel(self._rowName, self._colName).find("tFunc") != -1 # Se antes era tf
            modelAgora = self.model(value).find("tFunc") != -1 # Se agora é tf
            if not modelAntes and modelAgora: self._hrt_storage.tf_dict[self._rowName, self._colName] = 0
            if modelAntes and not modelAgora: self._hrt_storage.tf_dict.pop((self._rowName, self._colName), None)
            if state == HrtState.humanValue and self.getDataModel(self._rowName, self._colName).find("Func") == -1:
                return self._hrt_storage.setStrData(self._rowName, self._colName, hrt_type_hex_from(value, self._hrt_storage.getStrData(self._rowName, "TYPE"), int(self._hrt_storage.getStrData(self._rowName, "BYTE_SIZE"))))
            else:
                return self._hrt_storage.setStrData(self._rowName, self._colName, str(value))    
        self.valueChanged.emit()
        
    def bind_to(self, signalOtherVar: Signal):        
        signalOtherVar.connect(self._update_from_other)
    
    @Slot()
    def _update_from_other(self):
        self.valueChanged.emit()
    
    def model(self, value: str = "") -> str:
        if value == "":
            value = self._hrt_storage.getStrData(self._rowName,self._colName)
        if value.startswith('@'):
            return "Func"
        elif value.startswith('$'):
            return "tFunc"
        else:
            return "Value"
               
    def getDataModel(self, rowName: str, colName: str) -> str:
        value = self._hrt_storage.getStrData(rowName,colName)
        return self.model(value)
    
    def getVariable(self, rowName: str, colName: str, state: HrtState = HrtState.machineValue):
        if rowName == colName or colName == 'NAME':
            return rowName
        else: 
            value = self._hrt_storage.getStrData(rowName, colName)
            dataModel = self.getDataModel(rowName, colName)
            if not colName in ["NAME", "TYPE", "BYTE_SIZE"]:
                if dataModel == "Func":
                    return self._evaluate_expression(value, rowName, colName, state)
                elif dataModel == "tFunc": 
                    if state == HrtState.humanValue:
                        return self._hrt_storage.tf_dict[rowName, colName]
                    elif state == HrtState.machineValue:
                        resp = hrt_type_hex_from(self._hrt_storage.tf_dict[rowName, colName], self._hrt_storage.getStrData(rowName, "TYPE"), int(self._hrt_storage.getStrData(rowName, "BYTE_SIZE")))
                        return resp
                elif state == HrtState.humanValue:
                    return hrt_type_hex_to(self._hrt_storage.getStrData(rowName, colName), self._hrt_storage.getStrData(rowName, "TYPE"))
            return value
    
    def _evaluate_expression(self, func: str, rowName: str, colName: str, state: HrtState):
        evaluator = Interpreter()
        func = func[1:]  # Remove o caractere '@' inicial
        tokens: list = re.findall(r'[A-Za-z_0-9]\w+\.[A-Za-z_0-9]\w+', func)
        if self._tokens != tokens:
            self._tokens = tokens
            self.expressionToken.emit(tokens) # self.bind_to(self.df.loc(token, colName))        
        for token in tokens:
            # Fazer no futuro: Checar se todas as variaves são do mesmo tipo ?
            col, row = token.split(".")
            var_val = self.getVariable(row, col, HrtState.humanValue)
            if var_val is not None:
                evaluator.symtable[token] = var_val
        try:
            result = evaluator(func)
            if state == HrtState.machineValue:
                resp = hrt_type_hex_from(result, self._hrt_storage.getStrData(rowName, "TYPE"), int(self._hrt_storage.getStrData(rowName, "BYTE_SIZE")))
                return resp
            else:    
                return result
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            if state == HrtState.machineValue:
                return "00".zfill(2*int(self._hrt_storage.getStrData(rowName, "BYTE_SIZE")))
            else:
                return 0.0