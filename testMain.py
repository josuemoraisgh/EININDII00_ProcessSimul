import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QComboBox, QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt_data import HrtData

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
        rows, cols = self.df.shape
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(cols)
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)

        for row in range(rows): 
            if any(x in self.widget_row_types[row][:4] for x in ["PACK", "ASCI", "UNSI", "FLOA", "INTE", "INDE"]): # "QLineEdit"
                row_type = 2
            elif any(x in self.widget_row_types[row][:4] for x in ["ENUM", "BIT_"]) : # "QComboBox"
                row_type = 1
            else:
                row_type = 0
              
            for col in range(cols):         
                cell_value = str(self.df.iloc[row, col])
                
                if col > 2 and row_type == 2:
                    widget = QLineEdit()
                    widget.setStyleSheet("QLineEdit { background-color: white;}")
                    widget.setText(cell_value)
                    # widget.editingFinished.connect(lambda r=row, c=col, w=widget: self.update_dataframe(r, c, w.text()))
                    self.tableWidget.setCellWidget(row, col, widget)

                elif col > 2 and row_type == 1:
                    widget = QComboBox()
                    widget.addItems(["Opção 1", "Opção 2", "Opção 3"])
                    widget.setCurrentText(cell_value)
                    # widget.currentTextChanged.connect(lambda value, r=row, c=col: self.update_dataframe(r, c, value))
                    self.tableWidget.setCellWidget(row, col, widget)
                
                else:
                    widget = QTableWidgetItem(cell_value)
                    widget.setFlags(widget.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    widget.setBackground(QColor("#D3D3D3"))  # Define fundo cinza claro
                    self.tableWidget.setItem(row, col, widget)
                    
    def on_cell_changed(self, row, column):
        """Atualiza o Excel sempre que uma célula for editada na interface."""
        value = self.tableWidget.item(row, column).text()
        self.hrt_data.set_pos_datframe(row, column, value)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData('all','dados.xlsx')
    window = ExcelTable(hrt_data)
    window.show()

    sys.exit(app.exec())
