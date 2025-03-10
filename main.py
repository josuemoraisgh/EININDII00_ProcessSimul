from PySide6 import QtCore
from PySide6.QtGui import QIcon
from numpy import equal
from PySide6.QtWidgets import(QApplication, QDialog, QFileDialog,
 QMainWindow, QMessageBox, QTreeWidgetItem, QWidget)
import sys
from ui_main import Ui_Dialog

class Login(QDialog, Ui_Dialog):
    def __init__(self) -> None:
        super(Login, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Login do Sistema")
        # appIcon = QIcon('_imgs/logo.PNG')
        # self.setWindowIcon(appIcon)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec()