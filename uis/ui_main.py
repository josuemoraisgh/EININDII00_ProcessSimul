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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QLCDNumber,
    QLabel, QMainWindow, QRadioButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

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
        self.tabdbase = DBTableWidget()
        self.tabdbase.setObjectName(u"tabdbase")
        self.verticalLayout_3 = QVBoxLayout(self.tabdbase)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.radioButtonHex = QRadioButton(self.tabdbase)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButtonHex)
        self.radioButtonHex.setObjectName(u"radioButtonHex")
        self.radioButtonHex.setChecked(True)

        self.horizontalLayout_3.addWidget(self.radioButtonHex)

        self.radioButtonHrt = QRadioButton(self.tabdbase)
        self.buttonGroup.addButton(self.radioButtonHrt)
        self.radioButtonHrt.setObjectName(u"radioButtonHrt")

        self.horizontalLayout_3.addWidget(self.radioButtonHrt)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tabdbase, "")
        self.oldCtrlGLWidget = CtrlGLWidget()
        self.oldCtrlGLWidget.setObjectName(u"oldCtrlGLWidget")
        self.horizontalLayout_7 = QHBoxLayout(self.oldCtrlGLWidget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.oldCtrlGLWidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)

        self.horizontalLayout_2.addWidget(self.label)

        self.lcdNumber_2 = QLCDNumber(self.oldCtrlGLWidget)
        self.lcdNumber_2.setObjectName(u"lcdNumber_2")

        self.horizontalLayout_2.addWidget(self.lcdNumber_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.oldCtrlGLWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.lcdNumber_3 = QLCDNumber(self.oldCtrlGLWidget)
        self.lcdNumber_3.setObjectName(u"lcdNumber_3")

        self.horizontalLayout_4.addWidget(self.lcdNumber_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_3 = QLabel(self.oldCtrlGLWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.horizontalLayout_5.addWidget(self.label_3)

        self.lcdNumber_4 = QLCDNumber(self.oldCtrlGLWidget)
        self.lcdNumber_4.setObjectName(u"lcdNumber_4")

        self.horizontalLayout_5.addWidget(self.lcdNumber_4)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_6.addLayout(self.verticalLayout_2)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_6)

        self.tabWidget.addTab(self.oldCtrlGLWidget, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.radioButtonHex.setText(QCoreApplication.translate("MainWindow", u"Hex", None))
        self.radioButtonHrt.setText(QCoreApplication.translate("MainWindow", u"Hart", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabdbase), QCoreApplication.translate("MainWindow", u"DBase", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"PV", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"SP", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"MV", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.oldCtrlGLWidget), QCoreApplication.translate("MainWindow", u"CtrlN\u00edvel", None))
    # retranslateUi

