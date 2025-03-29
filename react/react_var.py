from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from PySide6.QtCore import QObject, Signal, Slot
from react.referencia import RefVar
from db.db_state import DBState
from db.db_storage import DBStorage
from asteval import Interpreter
import math
import random
import re

class ReactVar(QObject):
    valueChanged = Signal()  # Sinal emitido quando o valor muda
    expressionToken = Signal(list,bool)

    def __init__(self, tableName: str, rowName: str, colName: str, storage: DBStorage, tf_ref: RefVar):
        super().__init__()
        self._tableName = tableName
        self._rowName = rowName
        self._colName = colName
        # state = 0 -> MachineValue, state = 1 -> HumanValue, state = 2 -> OriginValue
        self.storage = storage
        self.tf_ref = tf_ref
        self._tokens = ""

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
 
    def type(self):
        return self.getVariable(self._tableName, self._rowName, 'TYPE')
 
    def value(self, state : DBState = DBState.originValue):
        return self.getVariable(self._tableName, self._rowName, self._colName, state)

    def setValue(self, value, state : DBState = DBState.originValue):
        if self._rowName == self._colName or self._colName == 'NAME':
            self.storage.dataFrame(self._tableName).loc[self._rowName,0] = value
        else:
            modelAntes = self.getDataModel(self._tableName, self._rowName, self._colName) == "Func" # Se antes era Func
            modelAgora = self.model(value) == "Func" != -1 # Se agora é Func
            if modelAntes and not modelAgora: # Se antes era Func e agora não é mais 
                self.expressionToken.emit(self.tokens, False)
            modelAntes = self.getDataModel(self._tableName, self._rowName, self._colName) == "tFunc" # Se antes era tf
            modelAgora = self.model(value) == "tFunc" # Se agora é tf
            if not modelAntes and modelAgora: # Se antes não era tF e agora é
                self.tf_ref.value[self._tableName][self._rowName, self._colName] = 0
            if modelAntes and not modelAgora: # Se antes era tF e agora não é 
                self.tf_ref.value[self._tableName].pop((self._rowName, self._colName), None)
            if state == DBState.humanValue and not modelAntes:
                value = hrt_type_hex_from(value, self.storage.getData(self._tableName, self._rowName, "TYPE"), int(self.storage.getData(self._tableName, self._rowName, "BYTE_SIZE")))
                self.storage.setData(self._tableName, self._rowName, self._colName, value)
            else:
                self.storage.setData(self._tableName, self._rowName, self._colName, str(value))
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
            value = self.storage.getData(self._tableName, self._rowName,self._colName)
        if value.startswith('@'):
            return "Func"
        elif value.startswith('$'):
            return "tFunc"
        else:
            return "Value"
               
    def getDataModel(self, tableName: str, rowName: str, colName: str) -> str:
        value = self.storage.getData(tableName, rowName, colName)
        return self.model(value)
    
    def getVariable(self, tableName: str, rowName: str, colName: str, state: DBState = DBState.machineValue):
        if rowName == colName or colName == 'NAME':
            return rowName
        else: 
            value = self.storage.getData(tableName, rowName, colName)
            dataModel = self.model(value)
            if not colName in ['NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS']:
                if dataModel == "Func":
                    if state == DBState.originValue:
                        return value
                    result = self.evaluate_expression(value)
                    if state == DBState.machineValue:
                        return hrt_type_hex_from(result, self.storage.getData(tableName, rowName, "TYPE"), int(self.storage.getData(tableName, rowName, "BYTE_SIZE")))
                    else:
                        return result
                elif dataModel == "tFunc": 
                    if state == DBState.humanValue:
                        return self.tf_ref.value[tableName][rowName, colName]
                    elif state == DBState.machineValue:
                        resp = hrt_type_hex_from(self.tf_ref.value[tableName][rowName, colName], self.storage.getData(tableName, rowName, "TYPE"), int(self.storage.getData(tableName, rowName, "BYTE_SIZE")))
                        return resp
                elif state == DBState.humanValue:
                    return hrt_type_hex_to(self.storage.getData(tableName, rowName, colName), self.storage.getData(tableName, rowName, "TYPE"))
            return value
    
    def evaluate_expression(self, func: str):
        evaluator = Interpreter()
        if func[0] == '@':
            func = func[1:]  # Remove o caractere '@' inicial
        tokens: list = re.findall(r'[A-Z]\w+\.[A-Z0-9]\w+\.[A-Za-z_0-9]\w+', func)
        if self._tokens != tokens:
            self._tokens = tokens
            self.expressionToken.emit(tokens, True) # self.bind_to(self.df.loc(token, colName))        
        for token in tokens:
            # Fazer no futuro: Checar se todas as variaves são do mesmo tipo ?
            tableName, col, row = token.split(".")
            var_val = self.getVariable(tableName, row, col, DBState.humanValue)
            if var_val is not None:
                evaluator.symtable[token.replace(".","_")] = var_val
            evaluator.symtable["math"] = math
            evaluator.symtable["random"] = random
        try:
            result = evaluator(re.sub(r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2_\3', func.replace(' ','')))   
            return result
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            return 0.0