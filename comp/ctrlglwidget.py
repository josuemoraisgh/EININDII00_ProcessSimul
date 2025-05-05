import base64
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

class CtrlGLWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_base64 = None
        
        # Layout para exibir a imagem
        self.layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)
        
    def setBackgroundImageFromBase64(self, image_base64: str):
        """Define a imagem de fundo a partir de Base64 e agenda atualização."""
        self.image_base64 = image_base64
        self.load_image_from_base64()

    def load_image_from_base64(self):
        """Carrega a imagem Base64 e exibe no QLabel."""
        if not self.image_base64:
            print("❌ Nenhuma imagem Base64 definida!")
            return

        image_data = base64.b64decode(self.image_base64)
        image = QImage.fromData(image_data)

        if image.isNull():
            print("❌ Erro ao carregar a imagem a partir do Base64!")
            return

        # Convertendo a imagem para o formato adequado
        image = image.convertToFormat(QImage.Format_RGBA8888)

        # Exibindo a imagem no QLabel
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)  # Centraliza a imagem no QLabel

        print("✅ Imagem carregada com sucesso!")

    def resizeEvent(self, event):
        """Ajusta a exibição da imagem ao redimensionar."""
        self.image_label.resize(self.size())
        super().resizeEvent(event)

# import base64
# from PySide6.QtOpenGLWidgets import QOpenGLWidget
# from PySide6.QtGui import QImage
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *

# class CtrlGLWidget(QOpenGLWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.texture_id = None
#         self.image_base64 = None

#     def setBackgroundImageFromBase64(self, image_base64: str):
#         """Define a imagem de fundo a partir de Base64 e agenda atualização."""
#         self.image_base64 = image_base64
#         self.update()

#     def initializeGL(self):
#         """Configurações iniciais do OpenGL."""
#         glEnable(GL_TEXTURE_2D)
#         glClearColor(1, 1, 1, 1)

#         # ✅ Só aqui podemos chamar glGetString!
#         renderer = glGetString(GL_RENDERER)
#         print("OpenGL Renderer:", renderer)

#     def load_texture_from_base64(self):
#         """Carrega a imagem Base64 e a converte em textura OpenGL."""
#         if not self.image_base64:
#             print("❌ Nenhuma imagem Base64 definida!")
#             return

#         image_data = base64.b64decode(self.image_base64)
#         image = QImage.fromData(image_data)

#         if image.isNull():
#             print("❌ Erro ao carregar a imagem a partir do Base64!")
#             return

#         image = image.convertToFormat(QImage.Format_RGBA8888)
#         width, height = image.width(), image.height()
#         data = image.bits().tobytes()

#         if self.texture_id:
#             glDeleteTextures([self.texture_id])

#         self.texture_id = glGenTextures(1)
#         glBindTexture(GL_TEXTURE_2D, self.texture_id)
#         glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#         glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#         glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
#         glBindTexture(GL_TEXTURE_2D, 0)

#     def resizeGL(self, w, h):
#         """Ajusta a viewport ao redimensionar."""
#         glViewport(0, 0, w, h)
#         glMatrixMode(GL_PROJECTION)
#         glLoadIdentity()
#         glOrtho(0, 1, 0, 1, -1, 1)
#         glMatrixMode(GL_MODELVIEW)

#     def paintGL(self):
#         """Renderiza a textura."""
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         if self.image_base64 and not self.texture_id:
#             self.load_texture_from_base64()

#         if self.texture_id:
#             glBindTexture(GL_TEXTURE_2D, self.texture_id)

#             glBegin(GL_QUADS)
#             glTexCoord2f(0, 1); glVertex2f(0, 0)
#             glTexCoord2f(1, 1); glVertex2f(1, 0)
#             glTexCoord2f(1, 0); glVertex2f(1, 1)
#             glTexCoord2f(0, 0); glVertex2f(0, 1)
#             glEnd()

#             glBindTexture(GL_TEXTURE_2D, 0)