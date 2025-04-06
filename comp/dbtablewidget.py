from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QMenu, QDialog
from PySide6.QtGui import QAction, QFont
from db.db_types import DBState, DBModel
import qtawesome as qta
from PySide6.QtCore import Qt
from uis.ui_dialog_value import Ui_Dialog_Value
from uis.ui_dialog_func import Ui_Dialog_Func 
from uis.ui_dialog_tfunc import Ui_Dialog_Tfunc 
from functools import partial
from react.react_db import ReactDB
from react.react_var import ReactVar
from hrt.hrt_enum import hrt_enum
from hrt.hrt_bitenum import hrt_bitEnum
from hrt.hrt_type import str2type, type2str
class DBTableWidget(QTableWidget):
    # def __init__(self):
    def __init__(self, parent: None):
        # super().__init__() 
        super().__init__(parent=parent)
        self.state = DBState.humanValue

    def sertAutoCompleteList(self, data:list):
        self.autoCompleteList = data
        
    def setBaseData(self, dbDataFrame: ReactDB, tableName: str):
        self.tableName = tableName
        self.dbDataFrame = dbDataFrame
        self.df = dbDataFrame.df[tableName]
        horizontalHeader_font = QFont("Arial", 12, QFont.Bold)  # Fonte maior e em negrito
        self.horizontalHeader().setFont(horizontalHeader_font)
        verticalHeader_font = QFont("Arial", 10, QFont.Bold)  # Fonte maior e em negrito
        self.verticalHeader().setFont(verticalHeader_font)              
        self.redrawAll()
            
    def changeType(self, type:bool):
        if(type):
            self.state = DBState.humanValue
        else:
            self.state = DBState.machineValue
        self.redrawAll()

    def redrawAll(self):   
        rows, cols = self.df.shape
        rowKeys = self.df.index
        colKeys = self.df.columns
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(colKeys)
        self.setVerticalHeaderLabels(rowKeys)        
        # Ajuste automático das colunas ao conteúdo
      
        for rowName in rowKeys: 
            for colName in colKeys: 
                data: ReactVar = self.df.loc[rowName, colName]
                value = data.getValue(self.state)
                cellValue = type2str(value,data.type()) if self.state == DBState.humanValue and not isinstance(value,str) else value
                typeValue = data.type()
                dataModel = data.model
                rowID = rowKeys.get_loc(rowName)
                colID = colKeys.get_loc(colName)

                if  self.state != DBState.machineValue and any(typeValue.find(x)!=-1 for x in ["ENUM", "BIT_ENUM"]) and not (dataModel in [DBModel.Func, DBModel.tFunc]) and not(colName in ["BYTE_SIZE","TYPE"]):
                    comboBox = QComboBox()
                    if typeValue.find("BIT_") == -1:
                        dados = list(hrt_enum[int(typeValue[4:])].values()) if self.tableName == "HART" else {}
                    else:
                        dados = list(hrt_bitEnum[int(typeValue[8:])].values()) if self.tableName == "HART" else {}
                    comboBox.addItems(dados)
                    comboBox.setCurrentText(cellValue)
                    def setDataBaseCombBox(data: ReactVar, widget:QComboBox, state: DBState, _):
                        data.setValue(widget.currentText(),state)
                    comboBox.currentIndexChanged.connect(partial(setDataBaseCombBox, data,comboBox,self.state))
                    def setTextCombBox(widget:QLineEdit, state: DBState, data: ReactVar):
                        value = data.getValue(state)
                        cellValue = str(value)
                        widget.setCurrentText(cellValue)
                    data.valueChangedSignal.connect(partial(setTextCombBox,lineEdit,self.state))
                    self.setCellWidget(rowID, colID, comboBox)
                
                else:
                    lineEdit = QLineEdit()
                    if(self.state or (colName in ["BYTE_SIZE","TYPE"]) or any(typeValue.find(x)!=-1 for x in ["PACKED", "UNSIGNED", "FLOAT", "INTEGER", "DATE", "TIME"])) and not (dataModel in [DBModel.Func, DBModel.tFunc]):
                        lineEdit.setStyleSheet("#QLineEdit{background-color: white;}")
                        def setDataBaseLineEdit(data: ReactVar, widget:QLineEdit, state: DBState):
                            data.setValue(str2type(widget.text(),data.type()),state)
                        lineEdit.editingFinished.connect(partial(setDataBaseLineEdit,data,lineEdit,self.state))
                    else:
                        lineEdit.setReadOnly(True)
                        lineEdit.setStyleSheet("background-color: #D3D3D3;")
                    def setTextLineEdit(widget:QLineEdit, state: DBState, data: ReactVar):
                        value = data.getValue(state)
                        cellValue = type2str(value,data.type()) if state == DBState.humanValue and not isinstance(value,str) else value
                        widget.setText(cellValue)
                    data.valueChangedSignal.connect(partial(setTextLineEdit,lineEdit,self.state))
                    lineEdit.setContextMenuPolicy(Qt.CustomContextMenu)
                    lineEdit.customContextMenuRequested.connect(partial(self.show_custom_context_menu, lineEdit, rowName, colName))
                    lineEdit.setText(cellValue)
                    self.setCellWidget(rowID, colID, lineEdit)
                                      
                self.setColumnWidth(colID, 150)
                # self.resizeColumnToContents(colID)

        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface
        # self.resizeColumnsToContents()        
    
    def show_custom_context_menu(self, line_edit, rowName, colName, event):
        """Mostra o menu de contexto quando o botão direito é pressionado"""
        if isinstance(line_edit, QLineEdit):
            menu = QMenu(self)
            
            action_Value = QAction(qta.icon("mdi.numeric"), "Value", self)
            data : ReactVar = self.df.loc[rowName,colName]
            def actionValueSlot():
                dialog = QDialog(self)
                dialog_ui = Ui_Dialog_Value()  # Cria a instância do QDialog
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEdit.setText(str(data.getValue(self.state)))
                dialog_ui.buttonBox.accepted.connect(lambda: data.setValue(dialog_ui.lineEdit.text(),self.state))
                # dialog_ui.buttonBox.accepted.connect(self.redrawAll)
                dialog.exec()
            action_Value.triggered.connect(actionValueSlot)
            menu.addAction(action_Value)

            action_Func = QAction(qta.icon("mdi.alarm-panel"), "Func", self)
            def actionFuncSlot():
                dialog = QDialog(self)
                dialog_ui = Ui_Dialog_Func()
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEdit.suggestions = self.dbDataFrame.autoCompleteList
                dialog_ui.lineEdit.adjust_height_by_lines(1)
                dialog_ui.lineEdit.setText(data.getFunc())
                dialog_ui.buttonBox.accepted.connect(lambda: data.setFunc(f'{dialog_ui.lineEdit.toPlainText()}'))
                # dialog_ui.buttonBox.accepted.connect(self.redrawAll)                
                dialog.exec()
            action_Func.triggered.connect(actionFuncSlot)
            menu.addAction(action_Func)
            
            action_Tfunc = QAction(qta.icon("mdi.math-integral"), "Tfunc", self)
            def actionTfuncSlot():
                dialog = QDialog(self)
                dialog_ui = Ui_Dialog_Tfunc()
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEditInput.suggestions = self.dbDataFrame.autoCompleteList
                dialog_ui.lineEditInput.adjust_height_by_lines(1)   
                tfunc = data.getTFunc()                           
                if tfunc != None:
                    num_str, den_str, delay_str, input_str = map(str.strip, tfunc.split(","))
                    dialog_ui.lineEditNum.setText(num_str[1:-1])
                    dialog_ui.lineEditDen.setText(den_str[1:-1])
                    dialog_ui.lineEditDelay.setText(delay_str)
                    dialog_ui.lineEditInput.setText(input_str)
                else:
                    dialog_ui.lineEditNum.setText("")
                    dialog_ui.lineEditDen.setText("")
                    dialog_ui.lineEditDelay.setText("")
                    dialog_ui.lineEditInput.setText("")
                dialog_ui.buttonBox.accepted.connect(lambda: data.setTFunc(f'[{dialog_ui.lineEditNum.text()}],[{dialog_ui.lineEditDen.text()}],{dialog_ui.lineEditDelay.text()},{dialog_ui.lineEditInput.toPlainText()},') )
                # dialog_ui.buttonBox.accepted.connect(self.redrawAll)                
                dialog.exec()
            action_Tfunc.triggered.connect(actionTfuncSlot)
            menu.addAction(action_Tfunc)

            menu.addSeparator()
            standard_menu = line_edit.createStandardContextMenu()
            # Adiciona as ações padrão ao menu
            for action in standard_menu.actions():
                menu.addAction(action) 
            menu.exec(line_edit.mapToGlobal(event))  # Correção aqui