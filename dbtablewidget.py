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
        self.cellChanged.connect(self.on_cell_changed)  # Detecta edições na tabela  
        
        header_font = QFont("Arial", 12, QFont.Bold)  # Fonte maior e em negrito
        self.horizontalHeader().setFont(header_font)
        self.verticalHeader().setFont(header_font)        
        # Criar uma fonte com tamanho 14
        # fonte = QFont("Arial", 14)
        # # Aplicar a fonte na tabela inteira
        # self.setFont(fonte)        
        self.redraw()
        
    def changeType(self, state:bool):
        self.state = not state
        self.redraw()
        
    def redraw(self):   
        self.df = self.hrt_data.get_dataframe()
        rows, cols = self.df.shape
        self.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.setRowCount(rows)
        self.setColumnCount(cols-1)
        self.setHorizontalHeaderLabels([item for item in self.df.columns if item != "NAME"])
        self.setVerticalHeaderLabels(self.df.iloc[:,0])        
        # Ajuste automático das colunas ao conteúdo
                
        widget_row_types = self.df['TYPE']    
        for row in range(rows): 
            if any(x in widget_row_types[row][:4] for x in ["PACK", "ASCI", "UNSI", "FLOA", "INTE", "INDE"]):  # "QLineEdit"
                row_type = 2
            elif any(x in widget_row_types[row][:4] for x in ["ENUM", "BIT_"]):  # "QComboBox"
                row_type = 1
            else:
                row_type = 0
              
            for col in range(1, cols): 
                data = self.hrt_data.get_variable_with_pos(row, col, machineValue=(col <= 2) or self.state) 
                cell_value = f"{data:.2f}" if isinstance(data, float) else str(data)

                if col == 2 or (col >= 2 and (row_type == 2 or self.state)):
                    widget = QLineEdit()
                    widget.setStyleSheet("QLineEdit { background-color: white; }")
                    widget.setText(cell_value)
                    widget.editingFinished.connect(partial(self.on_edit_finished, widget, row, col))
                    self.setCellWidget(row, col-1, widget)

                elif col > 2 and row_type == 1:
                    widget = QComboBox()
                    if widget_row_types[row][:4] == "ENUM":
                        dados = list(hrt_enum[int(widget_row_types[row][4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(widget_row_types[row][8:])].values())
                    widget.addItems(dados)
                    widget.setCurrentText(cell_value)
                    widget.currentIndexChanged.connect(partial(self.on_combo_changed, widget, row, col))
                    self.setCellWidget(row, col-1, widget)
                
                else:
                    widget = QTableWidgetItem()
                    widget.setFlags(widget.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    widget.setBackground(QColor("#D3D3D3"))  # Define fundo cinza claro
                    widget.setText(cell_value)
                    self.setItem(row, col-1, widget)
                    
                self.setColumnWidth(col-1, 150)

        self.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.viewport().update()  # Atualiza a interface

    def on_edit_finished(self, widget, row, col):
        """Atualiza os dados ao editar um QLineEdit."""
        value = widget.text()
        self.hrt_data.set_variable_with_pos(value, row, col, machineValue=(col <= 2) or self.state)

    def on_combo_changed(self, widget, row, col, _):
        """Atualiza os dados ao mudar um QComboBox."""
        value = widget.currentText()
        self.hrt_data.set_variable_with_pos(value, row, col, machineValue=(col <= 2) or self.state)

    def on_cell_changed(self, row, column):
        """Atualiza o Excel sempre que uma célula for editada na interface."""
        value = self.tableWidget.item(row, column).text()
        self.hrt_data.set_variable_with_pos(value, row, column, machineValue=(column <= 2) or self.state)