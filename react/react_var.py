from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from PySide6.QtCore import QObject, Signal, Slot
from react.referencia import RefVar
from db.db_types import DBState, DBModel
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
        self.model = self.getDataModel(tableName, rowName, colName)
        self._tokens = ""

    @property # metodo getter 
    def rowName(self):
        return self._rowName

    @property # metodo getter 
    def colName(self):
        return self._colName
 
    def type(self):
        return self.getVariable(self._tableName, self._rowName, 'TYPE', DBState.machineValue, DBModel.Value)
 
    def value(self, state : DBState = DBState.originValue):
        return self.getVariable(self._tableName, self._rowName, self._colName, state, self.model)

    def setValue(self, value, state : DBState = DBState.originValue):
        if self._rowName == self._colName or self._colName == 'NAME':
            self.storage.dataFrame(self._tableName).loc[self._rowName,0] = value
        else:
            modelAntes = self.model
            modelAgora = self.getModel(value)
            if modelAntes == DBModel.Func and modelAgora != DBModel.Func: # Se antes era Func e agora não é mais 
                self.expressionToken.emit(self.tokens, False)
            if modelAntes != DBModel.tFunc and modelAgora == DBModel.tFunc: # Se antes não era tF e agora é
                self.tf_ref.value[self._tableName][self._rowName, self._colName] = 0
            if modelAntes == DBModel.tFunc and modelAgora != DBModel.tFunc: # Se antes era tF e agora não é 
                self.tf_ref.value[self._tableName].pop((self._rowName, self._colName), None)
            if state == DBState.humanValue and modelAgora != DBModel.tFunc:
                value = hrt_type_hex_from(value, self.storage.getData(self._tableName, self._rowName, "TYPE"), int(self.storage.getData(self._tableName, self._rowName, "BYTE_SIZE")))
                self.storage.setData(self._tableName, self._rowName, self._colName, value)
            else:
                self.storage.setData(self._tableName, self._rowName, self._colName, str(value))
        self.model = modelAgora
        self.valueChanged.emit()
        
    def bind_to(self, signalOtherVar: Signal, isConnect: bool):  
        if isConnect == True:      
            signalOtherVar.connect(self._update_from_other)
        else:
            signalOtherVar.disconnect(self._update_from_other)
        
    @Slot()
    def _update_from_other(self):
        self.valueChanged.emit()
        
    def getModel(self, value: str = "") -> str:
        if value == "":
            value = self.storage.getData(self._tableName, self._rowName,self._colName)
        if value.startswith('@'):
            return DBModel.Func
        elif value.startswith('$'):
            return DBModel.tFunc
        else:
            return DBModel.Value
               
    def getDataModel(self, tableName: str, rowName: str, colName: str) -> str:
        value = self.storage.getData(tableName, rowName, colName)
        return self.getModel(value)
    
    def getVariable(self, tableName: str, rowName: str, colName: str, state: DBState = DBState.machineValue, model : str = ''):        
        if rowName == colName or colName == 'NAME':
            return rowName

        if colName in ['NAME', 'TYPE', 'BYTE_SIZE', 'MB_POINT', 'ADDRESS']:
            return self.storage.getData(tableName, rowName, colName)
        
        if model == '': 
            model = self.getDataModel(tableName, rowName, colName)

        if model == DBModel.Func:
            value = self.storage.getData(tableName, rowName, colName)
            if state == DBState.originValue:
                return value

            result = self.evaluate_expression(value)
            if state == DBState.machineValue:
                return hrt_type_hex_from(result, self.storage.getData(tableName, rowName, "TYPE"), int(self.storage.getData(tableName, rowName, "BYTE_SIZE")))
            
            return result

        if model == DBModel.tFunc:
            if state == DBState.humanValue:
                return self.tf_ref.value[tableName][rowName, colName]

            if state == DBState.machineValue:
                return hrt_type_hex_from(self.tf_ref.value[tableName][rowName, colName], self.storage.getData(tableName, rowName, "TYPE"), int(self.storage.getData(tableName, rowName, "BYTE_SIZE")))

        if state == DBState.humanValue:
            return hrt_type_hex_to(self.storage.getData(tableName, rowName, colName), self.storage.getData(tableName, rowName, "TYPE"))

        return self.storage.getData(tableName, rowName, colName)
    
    def evaluate_expression(self, func: str):
        evaluator = Interpreter()
        if func[0] == '@' or func[0] == " ":
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
            result = evaluator(re.sub(r'([A-Z]\w+)\.([A-Z0-9]\w+)\.([A-Za-z_0-9]\w+)', r'\1_\2_\3', func))   
            return result
        except Exception as e:
            print("Erro ao avaliar expressão:", e)
            return 0.0