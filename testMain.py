from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QComboBox, QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt_data import HrtData
from hrt_enum import hrt_enum
from hrt_bitenum import hrt_bitEnum
import sys

class ExcelTable(QMainWindow, Ui_MainWindow):
    def __init__(self, hrt_data: HrtData):
        super().__init__()
        self.setupUi(self)  # Configura a interface do Qt Designer
        self.hrt_data = hrt_data
        self.hrt_data.data_updated.connect(self.initUI)  # Conecta sinal de atualização
        self.initUI()
        self.tableWidget.cellChanged.connect(self.on_cell_changed)  # Detecta edições na tabela

    def initUI(self):
        """Configura a tabela com base nos dados carregados do Excel."""
        self.df = self.hrt_data.get_dataframe()
        rows, cols = self.df.shape
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(cols)
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)
        widget_row_types = self.df['TYPE']
        
        for row in range(rows): 
            if any(x in widget_row_types[row][:4] for x in ["PACK", "ASCI", "UNSI", "FLOA", "INTE", "INDE"]): # "QLineEdit"
                row_type = 2
            elif any(x in widget_row_types[row][:4] for x in ["ENUM", "BIT_"]) : # "QComboBox"
                row_type = 1
            else:
                row_type = 0
              
            for col in range(cols): 
                data = self.hrt_data.get_variable_with_pos(row, col, machineValue = col <= 2) 
                if type(data) == float:                            
                    cell_value = f"{data:.2f}"
                else:
                    cell_value = str(data)

                if col > 2 and row_type == 2:
                    widget = QLineEdit()
                    widget.setStyleSheet("QLineEdit { background-color: white;}")
                    widget.setText(cell_value)
                    widget.editingFinished.connect(lambda w=widget, r=row, c=col: self.hrt_data.set_variable_with_pos(w.text(), r, c, machineValue= c <= 2))
                    self.tableWidget.setCellWidget(row, col, widget)

                elif col > 2 and row_type == 1:
                    widget = QComboBox()
                    if(widget_row_types[row][:4] == "ENUM"):
                        dados = list(hrt_enum[int(widget_row_types[row][4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(widget_row_types[row][8:])].values())
                    widget.addItems(dados)
                    widget.setCurrentText(cell_value)
                    widget.currentIndexChanged.connect(lambda _, w=widget, r=row, c=col: self.hrt_data.set_variable_with_pos(w.currentText(), r, c, machineValue= c <= 2))
                    self.tableWidget.setCellWidget(row, col, widget)
                
                else:
                    widget = QTableWidgetItem(cell_value)
                    widget.setFlags(widget.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    widget.setBackground(QColor("#D3D3D3"))  # Define fundo cinza claro
                    self.tableWidget.setItem(row, col, widget)
                    
    def on_cell_changed(self, row, column):
        """Atualiza o Excel sempre que uma célula for editada na interface."""
        value = self.tableWidget.item(row, column).text()
        self.hrt_data.set_variable_with_pos(value, row, column, machineValue= column <= 2)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData('dados.xls')
    window = ExcelTable(hrt_data)
    window.show()

    sys.exit(app.exec())
