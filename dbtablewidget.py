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
        # Configurar o menu de contexto
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        horizontalHeader_font = QFont("Arial", 12, QFont.Bold)  # Fonte maior e em negrito
        self.horizontalHeader().setFont(horizontalHeader_font)
        verticalHeader_font = QFont("Arial", 10, QFont.Bold)  # Fonte maior e em negrito
        self.verticalHeader().setFont(verticalHeader_font)              
        self.redrawAll()

    def show_context_menu(self, position: QPoint):
        """Mostra o menu de contexto quando o botão direito é pressionado"""
        item = self.itemAt(position)
        if item:  # Verifica se há um item na posição
            menu = QMenu(self)
            row = self.row(item)  # Obtém a linha do item
            col = self.column(item)  # Obtém a coluna do item
            # Adiciona uma opção para abrir o QDialog
            action_Value = menu.addAction("Value")
            action_Func = menu.addAction("Func")
            action_tFunc = menu.addAction("tf")
            # Exibe o menu
            action = menu.exec(self.viewport().mapToGlobal(position))
            dialog = QDialog(self)
            # Carregar o QDialog do arquivo .ui
            if action == action_Value: 
                dialog_ui = Ui_Dialog_Value()  # Cria a instância do QDialog
                dialog_ui.lineEdit.setText(self.hrt_data.get_variable(row,col,self.state))
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.set_variable(dialog_ui.lineEdit.text(),row,col,self.state))
            elif action == action_Func: 
                dialog_ui = Ui_Dialog_Func()
                dialog_ui.lineEdit.setText(self.hrt_data.getStrData[row,col][1:])
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.setStrData(f'@{dialog_ui.lineEdit.text()}',row,col))
            elif action == action_tFunc: 
                dialog_ui = Ui_Dialog_Tfunc()
                num_str, den_str, input_str = map(str.strip, self.hrt_data.getStrData[row,col].split(","))
                dialog_ui.lineEditNum.setText(num_str[1:-1])
                dialog_ui.lineEditDen.setText(den_str[1:-1])
                dialog_ui.lineEditInput.setText(input_str)
                dialog_ui.buttonBox.accepted.connect(lambda: self.hrt_data.setStrData(f'$[{dialog_ui.lineEditNum.text()}],[{dialog_ui.lineEditDen.text()}],{dialog_ui.lineEditInput.text()}',row,col))
            dialog_ui.setupUi(dialog)  # Configura a interface do QDialogpath = '../uis/dialog_value.ui'            dialog.setModal(True)  # Torna o dialog modal (bloqueia interação com outras janelas)
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
                
                if (self.state or (colName in ["BYTE_SIZE","TYPE"]) or any(typeValue.find(x)!=-1 for x in ["PACKED", "UNSIGNED", "FLOAT", "INTEGER", "DATE", "TIME"])) and not (dataModel in ["Func", "tFunc"]):
                    widget = QLineEdit()
                    widget.setStyleSheet("QLineEdit { background-color: white; }")
                    widget.setText(cell_value)
                    widget.editingFinished.connect(partial(self.on_edit_finished, widget, rowName, colName, machineValue))
                    self.setCellWidget(rowID, colID, widget)

                elif any(typeValue.find(x)!=-1 for x in ["ENUM", "BIT_ENUM"]) and not (dataModel in ["Func", "tFunc"]):
                    widget = QComboBox()
                    if typeValue.find("BIT_") == -1:
                        dados = list(hrt_enum[int(typeValue[4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(typeValue[8:])].values())
                    widget.addItems(dados)
                    widget.setCurrentText(cell_value)
                    widget.currentIndexChanged.connect(partial(self.on_combo_changed, widget, rowName, colName, machineValue))
                    self.setCellWidget(rowID, colID, widget)
                
                else:
                    widget = QTableWidgetItem()
                    widget.setFlags(widget.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    widget.setBackground(QColor("#D3D3D3"))  # Define fundo cinza claro
                    widget.setText(cell_value)
                    self.setItem(rowID, colID, widget)
                    
                self.setColumnWidth(colID, 150)

        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface

    def on_edit_finished(self, widget, row, col, machineValue):
        """Atualiza os dados ao editar um QLineEdit."""
        value = widget.text()
        self.hrt_data.set_variable(value, row, col, machineValue)

    def on_combo_changed(self, widget, row, col, machineValue, _):
        """Atualiza os dados ao mudar um QComboBox."""
        value = widget.currentText()
        self.hrt_data.set_variable(value, row, col, machineValue)
