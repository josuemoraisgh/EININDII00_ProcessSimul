import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QComboBox, QTableWidgetItem
from PySide6.QtCore import Qt
from ui_main import Ui_MainWindow  # Interface do Qt Designer

class ExcelTable(QMainWindow, Ui_MainWindow):
    def __init__(self, excel_file="dados.xlsx"):
        super().__init__()
        self.setupUi(self)  # Configura a interface do Qt Designer
        
        self.excel_file = excel_file
        self.load_data()
        self.initUI()

    def load_data(self):
        """Carrega os dados do Excel para o DataFrame."""
        try:
            self.df = pd.read_excel(self.excel_file, engine="openpyxl")
        except FileNotFoundError:
            # Se o arquivo não existir, cria uma tabela vazia
            self.df = pd.DataFrame(columns=["Nome", "Idade", "Cidade", "Numero"])
            self.save_data()
        self.widget_row_types = self.df['Tipo']

    def save_data(self):
        """Salva os dados da tabela de volta no Excel."""
        self.df.to_excel(self.excel_file, index=False, engine="openpyxl")

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
                    widget.setText(cell_value)
                    widget.editingFinished.connect(lambda r=row, c=col, w=widget: self.update_dataframe(r, c, w.text()))
                    self.tableWidget.setCellWidget(row, col, widget)

                elif col > 2 and row_type == 1:
                    widget = QComboBox()
                    widget.addItems(["Opção 1", "Opção 2", "Opção 3"])
                    widget.setCurrentText(cell_value)
                    widget.currentTextChanged.connect(lambda value, r=row, c=col: self.update_dataframe(r, c, value))
                    self.tableWidget.setCellWidget(row, col, widget)
                
                else:
                    item = QTableWidgetItem(cell_value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    self.tableWidget.setItem(row, col, item)

    def update_dataframe(self, row, col, value):
        """Atualiza o DataFrame quando a célula for alterada."""
        self.df.iloc[row, col] = value
        self.save_data()  # Salva automaticamente no Excel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = ExcelTable("dados.xlsx")
    window.show()

    sys.exit(app.exec())
