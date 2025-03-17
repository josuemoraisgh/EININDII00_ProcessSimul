from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QTableWidgetItem, QMenu, QDialog
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QPoint
from uis.ui_dialog_value import Ui_Dialog_Value
from uis.ui_dialog_func import Ui_Dialog_Func 
from uis.ui_dialog_tfunc import Ui_Dialog_Tfunc 
from PySide6 import QtUiTools
from functools import partial
from hrt.hrt_data import HrtData
from hrt.hrt_enum import hrt_enum
from hrt.hrt_bitenum import hrt_bitEnum

class DBTableWidget(QTableWidget):
    # def __init__(self):
    def __init__(self, parent: None):
        # super().__init__() 
        super().__init__(parent=parent)
        
    def setBaseData(self, hrt_data: HrtData):
        self.hrt_data = hrt_data
        self.hrt_data.data_updated.connect(self.redraw)  # Conecta sinal de atualização
        
        horizontalHeader_font = QFont("Arial", 12, QFont.Bold)  # Fonte maior e em negrito
        self.horizontalHeader().setFont(horizontalHeader_font)
        verticalHeader_font = QFont("Arial", 10, QFont.Bold)  # Fonte maior e em negrito
        self.verticalHeader().setFont(verticalHeader_font)              
        self.redrawAll()

    def show_custom_context_menu(self, line_edit, event, rowName, colName):
        """Mostra o menu de contexto quando o botão direito é pressionado"""
        if isinstance(line_edit, QLineEdit):
            menu = QMenu(self)
            action_Value = menu.addAction("Value")
            action_Func = menu.addAction("Func")
            action_tFunc = menu.addAction("tf")
            menu.addSeparator()
            standard_menu = line_edit.createStandardContextMenu()
            # Adiciona as ações padrão ao menu
            for action in standard_menu.actions():
                menu.addAction(action) 
            action = menu.exec(line_edit.mapToGlobal(event))
            dialog = QDialog(self)
            # Carregar o QDialog do arquivo .ui
            if action == action_Value: 
                dialog_ui = Ui_Dialog_Value()  # Cria a instância do QDialog
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEdit.setText(str(self.hrt_data.get_variable(rowName,colName,self.state)))
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.set_variable(dialog_ui.lineEdit.text(),rowName,colName,self.state))
            elif action == action_Func: 
                dialog_ui = Ui_Dialog_Func()
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                dialog_ui.lineEdit.setText(self.hrt_data.getStrData[rowName,colName][1:])
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.setStrData(f'@{dialog_ui.lineEdit.text()}',rowName,colName))
            elif action == action_tFunc: 
                dialog_ui = Ui_Dialog_Tfunc()
                dialog_ui.setupUi(dialog)  # Configura a interface do QDialog
                num_str, den_str, input_str = map(str.strip, self.hrt_data.getStrData[rowName,colName].split(","))
                dialog_ui.lineEditNum.setText(num_str[1:-1])
                dialog_ui.lineEditDen.setText(den_str[1:-1])
                dialog_ui.lineEditInput.setText(input_str)
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.setStrData(f'$[{dialog_ui.lineEditNum.text()}],[{dialog_ui.lineEditDen.text()}],{dialog_ui.lineEditInput.text()}',rowName,colName))
                # Definir o texto no QDialog (como exemplo, passando o valor do item clicado)
                # Exibe o QDialog
            dialog.exec()
            
    def changeType(self, state:bool):
        self.state = not state
        self.redrawAll()
        
    def redraw(self):   
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        for rowName in self.hrt_data.rowKeys():               
            for colName in self.hrt_data.colKeys(): 
                machineValue = (colName in ["BYTE_SIZE","TYPE"]) or self.state
                data = self.hrt_data.get_variable(rowName, colName, machineValue) 
                cell_value = f"{data:.2f}" if not machineValue and isinstance(data, float) else str(data)
                rowID = self.hrt_data.rowKeys().get_loc(rowName)
                colID = self.hrt_data.colKeys().get_loc(colName)
                widget = self.cellWidget(rowID, colID)
                item = self.item(rowID, colID)
                if item:
                    item.setText(cell_value)
                if widget:
                    if hasattr(widget, "setText"):
                        widget.setText(cell_value)
                    else:
                        widget.setCurrentText(cell_value)
                    
        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface
        
    def redrawAll(self):   
        rows, cols = self.hrt_data.getShape()
        rowKeys = self.hrt_data.rowKeys()
        colKeys = self.hrt_data.colKeys()
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(colKeys)
        self.setVerticalHeaderLabels(rowKeys)        
        # Ajuste automático das colunas ao conteúdo
      
        for rowName in rowKeys: 
            for colName in colKeys: 
                machineValue = (colName in ["BYTE_SIZE","TYPE"]) or self.state
                data = self.hrt_data.get_variable(rowName, colName, machineValue) 
                cell_value = f"{data:.2f}" if not machineValue and isinstance(data, float) else str(data)
                typeValue = self.hrt_data.get_variable(rowName,'TYPE')
                dataModel = self.hrt_data.getDataModel(rowName,colName)
                rowID = rowKeys.get_loc(rowName)
                colID = colKeys.get_loc(colName)

                if  any(typeValue.find(x)!=-1 for x in ["ENUM", "BIT_ENUM"]) and not (dataModel in ["Func", "tFunc"]) and not(colName in ["BYTE_SIZE","TYPE"]):
                    comboBox = QComboBox()
                    if typeValue.find("BIT_") == -1:
                        dados = list(hrt_enum[int(typeValue[4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(typeValue[8:])].values())
                    comboBox.addItems(dados)
                    comboBox.setCurrentText(cell_value)
                    comboBox.currentIndexChanged.connect(partial(self.on_combo_changed, comboBox, rowName, colName, machineValue))
                    self.setCellWidget(rowID, colID, comboBox)
                
                else:
                    lineEdit = QLineEdit()
                    if(self.state or (colName in ["BYTE_SIZE","TYPE"]) or any(typeValue.find(x)!=-1 for x in ["PACKED", "UNSIGNED", "FLOAT", "INTEGER", "DATE", "TIME"])) and not (dataModel in ["Func", "tFunc"]):
                        lineEdit.setStyleSheet("#QLineEdit{background-color: white;}")
                        lineEdit.editingFinished.connect(partial(self.on_edit_finished, lineEdit, rowName, colName, machineValue))
                    else:
                        lineEdit.setReadOnly(True)
                        lineEdit.setStyleSheet("background-color: #D3D3D3;")
                    lineEdit.setContextMenuPolicy(Qt.CustomContextMenu)
                    lineEdit.customContextMenuRequested.connect(lambda event: self.show_custom_context_menu(lineEdit, event, rowName, colName))
                    lineEdit.setText(cell_value)
                    self.setCellWidget(rowID, colID, lineEdit)
                                      
                self.setColumnWidth(colID, 150)

        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface

    def on_edit_finished(self, widget, row, col, machineValue):
        """Atualiza os dados ao editar um QLineEdit."""
        value = widget.text()
        self.hrt_data.set_variable(value, row, col, machineValue)

    def on_combo_changed(self, widget: QComboBox, row: str, col: str, machineValue, _):
        """Atualiza os dados ao mudar um QComboBox."""
        value = widget.currentText()
        self.hrt_data.set_variable(value, row, col, machineValue)
