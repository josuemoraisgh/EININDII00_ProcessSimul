from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QImage
from OpenGL.GL import *

class ImageGLWidget(QOpenGLWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.texture_id = None

    def initializeGL(self):
        """Configurações iniciais do OpenGL"""
        glEnable(GL_TEXTURE_2D)
        glClearColor(1, 1, 1, 1)  # Fundo branco
        self.load_texture()

    def load_texture(self):
        """Carrega a imagem e a converte em textura OpenGL"""
        image = QImage(self.image_path)
        if image.isNull():
            print("❌ Erro ao carregar a imagem!")
            return
        
        image = image.convertToFormat(QImage.Format_RGBA8888)
        width, height = image.width(), image.height()
        data = image.bits().tobytes()  # ✅ Correção aqui!

        # Criar textura OpenGL
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)

    def resizeGL(self, w, h):
        """Ajusta a viewport ao redimensionar"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1, 0, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Renderiza a textura"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.texture_id:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(0, 0)
            glTexCoord2f(1, 1); glVertex2f(1, 0)
            glTexCoord2f(1, 0); glVertex2f(1, 1)
            glTexCoord2f(0, 0); glVertex2f(0, 1)
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)