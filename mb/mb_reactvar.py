from PySide6.QtCore import Signal, Slot
from inter.ireactvar import DBReactiveVariable
from mb.mb_storage import MBStorage
from inter.istate import DBState
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from asteval import Interpreter
import math
import random
import re

class MBReactiveVariable(DBReactiveVariable):
    valueChanged = Signal()  # Sinal emitido quando o valor muda
    expressionToken = Signal(list,bool)

    def __init__(self, rowName, colName, mb_storage: MBStorage):
        super().__init__()
        self._rowName = rowName
        self._colName = colName
        # state = 0 -> MachineValue, state = 1 -> HumanValue, state = 2 -> OriginValue
        self.mb_storage = mb_storage
        self._tokens = ""

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
 
    def type(self):
        return self.getVariable(self._rowName, 'TYPE')
 
    def value(self, state : DBState = DBState.originValue):
        return self.getVariable(self._rowName, self._colName, state)

    def setValue(self, value, state : DBState = DBState.originValue):
        if self._rowName == self._colName or self._colName == 'NAME':
            self.mb_storage.df.loc[self._rowName,0] = value
        else:
            modelAntes = self.getDataModel(self._rowName, self._colName) == "Func" # Se antes era Func
            modelAgora = self.model(value) == "Func" != -1 # Se agora é Func
            if modelAntes and not modelAgora: # Se antes era Func e agora não é mais 
                self.expressionToken.emit(self.tokens, False)
            modelAntes = self.getDataModel(self._rowName, self._colName) == "tFunc" # Se antes era tf
            modelAgora = self.model(value) == "tFunc" # Se agora é tf
            if not modelAntes and modelAgora: # Se antes não era tF e agora é
                self.mb_storage.tf_dict[self._rowName, self._colName] = 0
            if modelAntes and not modelAgora: # Se antes era tF e agora não é 
                self.mb_storage.tf_dict.pop((self._rowName, self._colName), None)
            if state == DBState.humanValue and self.getDataModel(self._rowName, self._colName).find("Func") == -1:
                value = hrt_type_hex_from(value, self.mb_storage.getStrData(self._rowName, "TYPE"), int(self.mb_storage.getStrData(self._rowName, "BYTE_SIZE")))
                self.mb_storage.setStrData(self._rowName, self._colName, value)
            else:
                self.mb_storage.setStrData(self._rowName, self._colName, str(value))
        self.valueChanged.emit()
        
    def bind_to(self, signalOtherVar: Signal, isConnect: bool):  
        if isConnect == True:      
            signalOtherVar.connect(self._update_from_other)
        else:
            signalOtherVar.disconnect(self._update_from_other)
        
    @Slot()
    def _update_from_other(self):
        self.valueChanged.emit()
    
    def model(self, value: str = "") -> str:
        if value == "":
            value = self.mb_storage.getStrData(self._rowName,self._colName)
        if value.startswith('@'):
            return "Func"
        elif value.startswith('$'):
            return "tFunc"
        else:
            return "Value"
               
    def getDataModel(self, rowName: str, colName: str) -> str:
        value = self.mb_storage.getStrData(rowName,colName)
        return self.model(value)
    
    def getVariable(self, rowName: str, colName: str, state: DBState = DBState.machineValue):
        if rowName == colName or colName == 'NAME':
            return rowName
        else: 
            value = self.mb_storage.getStrData(rowName, colName)
            dataModel = self.getDataModel(rowName, colName)
            if not colName in ["NAME", "TYPE", "BYTE_SIZE"]:
                if dataModel == "Func":
                    if state == DBState.originValue:
                        return value
                    result = self.evaluate_expression(value)
                    if state == DBState.machineValue:
                        return hrt_type_hex_from(result, self.mb_storage.getStrData(rowName, "TYPE"), int(self.mb_storage.getStrData(rowName, "BYTE_SIZE")))
                    else:
                        return result
                elif dataModel == "tFunc": 
                    if state == DBState.humanValue:
                        return self.mb_storage.tf_dict[rowName, colName]
                    elif state == DBState.machineValue:
                        resp = hrt_type_hex_from(self.mb_storage.tf_dict[rowName, colName], self.mb_storage.getStrData(rowName, "TYPE"), int(self.mb_storage.getStrData(rowName, "BYTE_SIZE")))
                        return resp
                elif state == DBState.humanValue:
                    return hrt_type_hex_to(self.mb_storage.getStrData(rowName, colName), self.mb_storage.getStrData(rowName, "TYPE"))
            return value
    
    def evaluate_expression(self, func: str):
        evaluator = Interpreter()
        func = func[1:]  # Remove o caractere '@' inicial
        tokens: list = re.findall(r'[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', func)
        if self._tokens != tokens:
            self._tokens = tokens
            self.expressionToken.emit(tokens, True) # self.bind_to(self.df.loc(token, colName))        
        for token in tokens:
            # Fazer no futuro: Checar se todas as variaves são do mesmo tipo ?
            col, row = token.split(".")
            var_val = self.getVariable(row, col, DBState.humanValue)
            if var_val is not None:
                evaluator.symtable[token.replace(".","_")] = var_val
            evaluator.symtable["math"] = math
            evaluator.symtable["random"] = random
        try:
            result = evaluator(re.sub(r'([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2', func))   
            return result
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            return 0.0