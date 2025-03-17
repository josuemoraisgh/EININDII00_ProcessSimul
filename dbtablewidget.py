from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QTableWidgetItem
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
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
        
    def changeType(self, state:bool):
        self.state = not state
        self.redrawAll()
        
    def redraw(self):   
        self.df = self.hrt_data.get_dataframe()
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        for rowName in self.df.index:               
            for colName in self.df.columns: 
                machineValue = (colName in ["BYTE_SIZE","TYPE"]) or self.state
                data = self.hrt_data.get_variable(rowName, colName, machineValue) 
                cell_value = f"{data:.2f}" if not machineValue and isinstance(data, float) else str(data)
                rowID = self.df.index.get_loc(rowName)
                colID = self.df.columns.get_loc(colName)
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
        self.df = self.hrt_data.get_dataframe()
        rows, cols = self.df.shape
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(self.df.columns)
        self.setVerticalHeaderLabels(self.df.index)        
        # Ajuste automático das colunas ao conteúdo
      
        for rowName in self.df.index: 
            for colName in self.df.columns: 
                machineValue = (colName in ["BYTE_SIZE","TYPE"]) or self.state
                data = self.hrt_data.get_variable(rowName, colName, machineValue) 
                cell_value = f"{data:.2f}" if not machineValue and isinstance(data, float) else str(data)
                typeValue = self.df.loc[rowName,'TYPE']
                dataModel = self.hrt_data.getDataModel(rowName,colName)
                rowID = self.df.index.get_loc(rowName)
                colID = self.df.columns.get_loc(colName)
                
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
