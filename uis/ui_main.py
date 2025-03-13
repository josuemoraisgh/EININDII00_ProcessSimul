# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QSizePolicy,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget)

from ctrlglwidget import CtrlGLWidget
from dbtablewidget import DBTableWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabShape(QTabWidget.TabShape.Triangular)
        self.BDados = QWidget()
        self.BDados.setObjectName(u"BDados")
        self.verticalLayout = QVBoxLayout(self.BDados)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.oldTableWidget = DBTableWidget(self.BDados)
        self.oldTableWidget.setObjectName(u"oldTableWidget")

        self.verticalLayout.addWidget(self.oldTableWidget)

        self.tabWidget.addTab(self.BDados, "")
        self.CtrlNivel = QWidget()
        self.CtrlNivel.setObjectName(u"CtrlNivel")
        self.horizontalLayout_2 = QHBoxLayout(self.CtrlNivel)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.oldOpenGLWidget = CtrlGLWidget(self.CtrlNivel)
        self.oldOpenGLWidget.setObjectName(u"oldOpenGLWidget")

        self.horizontalLayout_2.addWidget(self.oldOpenGLWidget)

        self.tabWidget.addTab(self.CtrlNivel, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(accessibility)
        self.tabWidget.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.BDados), QCoreApplication.translate("MainWindow", u"BDados", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CtrlNivel), QCoreApplication.translate("MainWindow", u"CtrlNivel", None))
    # retranslateUi

