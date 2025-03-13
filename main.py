from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout
from uis.ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt.hrt_data import HrtData
from abaData import DBTableWidget
from abaNivel import ImageGLWidget
import sys
import os

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, hrt_data: HrtData):
        super().__init__()
        self.resize(800, 600)  # Defina o tamanho desejado
        self.setupUi(self)  # Configura a interface do Qt Designer        
        self.hrt_data = hrt_data
        self.substituir_widget("oldTableWidget", DBTableWidget(hrt_data)) 
        image_path = os.path.abspath("img/caldeira.jpg")
        self.substituir_widget("oldOpenGLWidget", ImageGLWidget(image_path))          
        self.centralizar_janela()

    def substituir_widget(self, widget_nome: str, novo_widget: QWidget):
        """
        Substitui um widget existente na interface por um novo widget.

        :param widget_nome: Nome do widget no Qt Designer a ser substituído.
        :param novo_widget: Instância do novo widget que substituirá o original.
        """
        # 🔹 Encontrar o widget que será substituído
        placeholder:QWidget = getattr(self, widget_nome, None)

        if placeholder:
            # Obter o layout do widget pai
            parent_layout: QLayout = placeholder.parentWidget().layout()

            if parent_layout:
                # 🔹 Substituir o widget
                index = parent_layout.indexOf(placeholder)
                parent_layout.removeWidget(placeholder)
                placeholder.deleteLater()  # Remove o widget original
                parent_layout.insertWidget(index, novo_widget)  # Insere o novo widget

    def centralizar_janela(self):
        # Obtém a tela primária
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        # Obtém a geometria da janela
        janela_geometry = self.frameGeometry()
        # Calcula o centro da tela e ajusta a posição da janela
        center_point = screen_geometry.center()
        janela_geometry.moveCenter(center_point)
        # Aplica a posição calculada
        self.move(janela_geometry.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData()
    window = MainWindow(hrt_data)
    window.show()
    sys.exit(app.exec())
