from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QMenu, QDialog
from PySide6.QtGui import QAction, QFont
from db.storage_sqlite import HrtState
import qtawesome as qta
from PySide6.QtCore import Qt
from uis.ui_dialog_value import Ui_Dialog_Value
from uis.ui_dialog_func import Ui_Dialog_Func 
from uis.ui_dialog_tfunc import Ui_Dialog_Tfunc 
from functools import partial
from hrt.hrt_reactdf import HrtReactDataFrame
from hrt.hrt_reactvar import HrtReactiveVariable
from hrt.hrt_enum import hrt_enum
from hrt.hrt_bitenum import hrt_bitEnum

class DBTableWidget(QTableWidget):
    # def __init__(self):
    def __init__(self, parent: None):
        # super().__init__() 
        super().__init__(parent=parent)
        self.state = HrtState.humanValue
        
    def setBaseData(self, hrtDataFrame: HrtReactDataFrame):
        self.hrtDataFrame = hrtDataFrame
        horizontalHeader_font = QFont("Arial", 12, QFont.Bold)  # Fonte maior e em negrito
        self.horizontalHeader().setFont(horizontalHeader_font)
        verticalHeader_font = QFont("Arial", 10, QFont.Bold)  # Fonte maior e em negrito
        self.verticalHeader().setFont(verticalHeader_font)              
        self.redrawAll()
            
    def changeType(self, type:bool):
        if(type):
            self.state = HrtState.humanValue
        else:
            self.state = HrtState.machineValue
        self.redrawAll()

    def redrawAll(self):   
        rows, cols = self.hrtDataFrame.df.shape
        rowKeys = self.hrtDataFrame.df.index
        colKeys = self.hrtDataFrame.df.columns
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(colKeys)
        self.setVerticalHeaderLabels(rowKeys)        
        # Ajuste automático das colunas ao conteúdo
      
        for rowName in rowKeys: 
            for colName in colKeys: 
                data: HrtReactiveVariable = self.hrtDataFrame.df.loc[rowName, colName]
                value = data.value(self.state)
                cellValue = format(value, ".2e") if self.state == HrtState.humanValue and isinstance(value, float) else str(value)
                typeValue = data.type()
                dataModel = data.model()
                rowID = rowKeys.get_loc(rowName)
                colID = colKeys.get_loc(colName)

                if  self.state != HrtState.machineValue and any(typeValue.find(x)!=-1 for x in ["ENUM", "BIT_ENUM"]) and not (dataModel in ["Func", "tFunc"]) and not(colName in ["BYTE_SIZE","TYPE"]):
                    comboBox = QComboBox()
                    if typeValue.find("BIT_") == -1:
                        dados = list(hrt_enum[int(typeValue[4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(typeValue[8:])].values())
                    comboBox.addItems(dados)
                    comboBox.setCurrentText(cellValue)
                    def setDataBaseCombBox(data: HrtReactiveVariable, widget:QComboBox, state: HrtState, _):
                        data.setValue(widget.currentText(),state)
                    comboBox.currentIndexChanged.connect(partial(setDataBaseCombBox, data,comboBox,self.state))
                    def setTextCombBox(data: HrtReactiveVariable, widget:QLineEdit, state: HrtState):
                        value = data.value(state)
                        cellValue = format(value, ".2e") if state == HrtState.humanValue and isinstance(value, float) else str(value)
                        widget.setCurrentText(cellValue)
                    data.valueChanged.connect(partial(setTextCombBox,data,lineEdit,self.state))
                    self.setCellWidget(rowID, colID, comboBox)
                
                else:
                    lineEdit = QLineEdit()
                    if(self.state or (colName in ["BYTE_SIZE","TYPE"]) or any(typeValue.find(x)!=-1 for x in ["PACKED", "UNSIGNED", "FLOAT", "INTEGER", "DATE", "TIME"])) and not (dataModel in ["Func", "tFunc"]):
                        lineEdit.setStyleSheet("#QLineEdit{background-color: white;}")
                        def setDataBaseLineEdit(data: HrtReactiveVariable, widget:QLineEdit, state: HrtState):
                            data.setValue(widget.text(),state)
                        lineEdit.editingFinished.connect(partial(setDataBaseLineEdit,data,lineEdit,self.state))
                    else:
                        lineEdit.setReadOnly(True)
                        lineEdit.setStyleSheet("background-color: #D3D3D3;")
                    def setTextLineEdit(data: HrtReactiveVariable, widget:QLineEdit, state: HrtState):
                        value = data.value(state)
                        cellValue = f"{value:.2f}" if state == HrtState.humanValue and isinstance(value, float) else str(value)
                        widget.setText(cellValue)
                    data.valueChanged.connect(partial(setTextLineEdit,data,lineEdit,self.state))
                    lineEdit.setContextMenuPolicy(Qt.CustomContextMenu)
                    lineEdit.customContextMenuRequested.connect(partial(self.show_custom_context_menu, lineEdit, rowName, colName))
                    lineEdit.setText(cellValue)
                    self.setCellWidget(rowID, colID, lineEdit)
                                      
                self.setColumnWidth(colID, 150)

        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface
    
    def show_custom_context_menu(self, line_edit, rowName, colName, event):
        """Mostra o menu de contexto quando o botão direito é pressionado"""
        if isinstance(line_edit, QLineEdit):
            menu = QMenu(self)
            
            action_Value = QAction(qta.icon("mdi.numeric"), "Value", self)
            data : HrtReactiveVariable = self.hrtDataFrame.df.loc[rowName,colName]
            def actionValueSlot():
                dialog = QDialog(self)
                dialog_ui = Ui_Dialog_Value()  # Cria a instância do QDialog
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEdit.setText(str(data.value(self.state)))
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
                dialog_ui.lineEdit.setText(data.value(HrtState.originValue)[1:])
                dialog_ui.buttonBox.accepted.connect(lambda: data.setValue(f'@{dialog_ui.lineEdit.text()}',self.state))
                # dialog_ui.buttonBox.accepted.connect(self.redrawAll)                
                dialog.exec()
            action_Func.triggered.connect(actionFuncSlot)
            menu.addAction(action_Func)
            
            action_Tfunc = QAction(qta.icon("mdi.math-integral"), "Tfunc", self)
            def actionTfuncSlot():
                dialog = QDialog(self)
                dialog_ui = Ui_Dialog_Tfunc()
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                try:
                    num_str, den_str, input_str = map(str.strip, data.value(HrtState.originValue).split(","))
                    dialog_ui.lineEditNum.setText(num_str[2:-1])
                    dialog_ui.lineEditDen.setText(den_str[1:-1])
                    dialog_ui.lineEditInput.setText(input_str)
                except Exception as e:
                    dialog_ui.lineEditNum.setText("")
                    dialog_ui.lineEditDen.setText("")
                    dialog_ui.lineEditInput.setText("")
                dialog_ui.buttonBox.accepted.connect(lambda: 
                    data.setValue(f'$[{dialog_ui.lineEditNum.text()}],[{dialog_ui.lineEditDen.text()}],{dialog_ui.lineEditInput.text()}',self.state)
                )
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
            
    # def redraw(self):   
    #     self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
    #     for rowName in self.hrtDataFrame.df.index:               
    #         for colName in self.hrtDataFrame.df.columns: 
    #             data: HrtReactiveVariable = self.hrtDataFrame.df[rowName, colName]
    #             cell_value = f"{data.value:.2f}" if not self.hrtDataFrame._hrt_storage.state == HrtState.machineValue and isinstance(data, float) else str(data)
    #             rowID = self.hrtDataFrame.df.index.get_loc(rowName)
    #             colID = self.hrtDataFrame.df.columns.get_loc(colName)
    #             widget = self.cellWidget(rowID, colID)
    #             item = self.item(rowID, colID)
    #             if item:
    #                 item.setText(cell_value)
    #             if widget:
    #                 if hasattr(widget, "setText"):
    #                     widget.setText(cell_value)
    #                 else:
    #                     widget.setCurrentText(cell_value)
                    
    #     self.blockSignals(False)  # Libera sinais após a configuração da tabela
    #     self.viewport().update()  # Atualiza a interface