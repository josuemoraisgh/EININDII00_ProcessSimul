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
    QSlider, QSpacerItem, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

from ctrlglwidget import CtrlGLWidget
from dbtablewidget import DBTableWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(643, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAutoFillBackground(True)
        self.tableWidget = QWidget()
        self.tableWidget.setObjectName(u"tableWidget")
        self.verticalLayout_4 = QVBoxLayout(self.tableWidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.radioButtonHex = QRadioButton(self.tableWidget)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButtonHex)
        self.radioButtonHex.setObjectName(u"radioButtonHex")
        self.radioButtonHex.setChecked(True)

        self.horizontalLayout_9.addWidget(self.radioButtonHex)

        self.radioButtonHrt = QRadioButton(self.tableWidget)
        self.buttonGroup.addButton(self.radioButtonHrt)
        self.radioButtonHrt.setObjectName(u"radioButtonHrt")

        self.horizontalLayout_9.addWidget(self.radioButtonHrt)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.label_4 = QLabel(self.tableWidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_8.addWidget(self.label_4)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.label_5 = QLabel(self.tableWidget)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_9.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.oldDBTableWidget = DBTableWidget(self.tableWidget)
        self.oldDBTableWidget.setObjectName(u"oldDBTableWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.oldDBTableWidget.sizePolicy().hasHeightForWidth())
        self.oldDBTableWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_4.addWidget(self.oldDBTableWidget)

        self.tabWidget.addTab(self.tableWidget, "")
        self.oldCtrlGLWidget = CtrlGLWidget()
        self.oldCtrlGLWidget.setObjectName(u"oldCtrlGLWidget")
        self.widgetLI100 = QWidget(self.oldCtrlGLWidget)
        self.widgetLI100.setObjectName(u"widgetLI100")
        self.widgetLI100.setGeometry(QRect(400, 20, 111, 71))
        self.widgetLI100.setMinimumSize(QSize(111, 71))
        self.widgetLI100.setAutoFillBackground(False)
        self.widgetLI100.setStyleSheet(u"#widgetLI100 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_3 = QLabel(self.widgetLI100)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.label_24 = QLabel(self.widgetLI100)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(95, 40, 21, 16))
        self.lcdPVLIC100 = QLCDNumber(self.widgetLI100)
        self.lcdPVLIC100.setObjectName(u"lcdPVLIC100")
        self.lcdPVLIC100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lcdPVLIC100.sizePolicy().hasHeightForWidth())
        self.lcdPVLIC100.setSizePolicy(sizePolicy2)
        self.lcdPVLIC100.setSmallDecimalPoint(True)
        self.lcdPVLIC100.setDigitCount(6)
        self.widgetPI100 = QWidget(self.oldCtrlGLWidget)
        self.widgetPI100.setObjectName(u"widgetPI100")
        self.widgetPI100.setGeometry(QRect(10, 90, 121, 71))
        font1 = QFont()
        font1.setUnderline(False)
        font1.setStrikeOut(False)
        self.widgetPI100.setFont(font1)
        self.widgetPI100.setTabletTracking(False)
        self.widgetPI100.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.widgetPI100.setAutoFillBackground(False)
        self.widgetPI100.setStyleSheet(u"#widgetPI100{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_6 = QLabel(self.widgetPI100)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setPointSize(12)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        self.label_6.setFont(font2)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVPIC100 = QLCDNumber(self.widgetPI100)
        self.lcdPVPIC100.setObjectName(u"lcdPVPIC100")
        self.lcdPVPIC100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVPIC100.sizePolicy().hasHeightForWidth())
        self.lcdPVPIC100.setSizePolicy(sizePolicy2)
        self.lcdPVPIC100.setSmallDecimalPoint(True)
        self.lcdPVPIC100.setDigitCount(6)
        self.label_26 = QLabel(self.widgetPI100)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(95, 40, 41, 16))
        self.widgetFI100A = QWidget(self.oldCtrlGLWidget)
        self.widgetFI100A.setObjectName(u"widgetFI100A")
        self.widgetFI100A.setGeometry(QRect(130, 420, 141, 71))
        self.widgetFI100A.setAutoFillBackground(False)
        self.widgetFI100A.setStyleSheet(u"#widgetFI100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_8 = QLabel(self.widgetFI100A)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVFV101 = QLCDNumber(self.widgetFI100A)
        self.lcdPVFV101.setObjectName(u"lcdPVFV101")
        self.lcdPVFV101.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVFV101.sizePolicy().hasHeightForWidth())
        self.lcdPVFV101.setSizePolicy(sizePolicy2)
        self.lcdPVFV101.setSmallDecimalPoint(True)
        self.lcdPVFV101.setDigitCount(6)
        self.label_25 = QLabel(self.widgetFI100A)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(95, 40, 41, 16))
        self.widgetTI100 = QWidget(self.oldCtrlGLWidget)
        self.widgetTI100.setObjectName(u"widgetTI100")
        self.widgetTI100.setGeometry(QRect(10, 250, 121, 71))
        self.widgetTI100.setMinimumSize(QSize(121, 71))
        self.widgetTI100.setAutoFillBackground(False)
        self.widgetTI100.setStyleSheet(u"#widgetTI100{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_9 = QLabel(self.widgetTI100)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy1)
        self.label_9.setFont(font)
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVTIC100 = QLCDNumber(self.widgetTI100)
        self.lcdPVTIC100.setObjectName(u"lcdPVTIC100")
        self.lcdPVTIC100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVTIC100.sizePolicy().hasHeightForWidth())
        self.lcdPVTIC100.setSizePolicy(sizePolicy2)
        self.lcdPVTIC100.setSmallDecimalPoint(True)
        self.lcdPVTIC100.setDigitCount(6)
        self.label_27 = QLabel(self.widgetTI100)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(96, 40, 21, 16))
        self.widgetCtrlFV100B = QWidget(self.oldCtrlGLWidget)
        self.widgetCtrlFV100B.setObjectName(u"widgetCtrlFV100B")
        self.widgetCtrlFV100B.setGeometry(QRect(10, 330, 111, 71))
        self.widgetCtrlFV100B.setMinimumSize(QSize(111, 71))
        self.widgetCtrlFV100B.setAutoFillBackground(False)
        self.widgetCtrlFV100B.setStyleSheet(u"#widgetCtrlFV100B{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_12 = QLabel(self.widgetCtrlFV100B)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)
        self.label_12.setFont(font)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVFV100B = QLCDNumber(self.widgetCtrlFV100B)
        self.lcdPVFV100B.setObjectName(u"lcdPVFV100B")
        self.lcdPVFV100B.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVFV100B.sizePolicy().hasHeightForWidth())
        self.lcdPVFV100B.setSizePolicy(sizePolicy2)
        self.lcdPVFV100B.setSmallDecimalPoint(True)
        self.lcdPVFV100B.setDigitCount(6)
        self.label_23 = QLabel(self.widgetCtrlFV100B)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(95, 40, 21, 16))
        self.widgetFI100B = QWidget(self.oldCtrlGLWidget)
        self.widgetFI100B.setObjectName(u"widgetFI100B")
        self.widgetFI100B.setGeometry(QRect(164, 20, 198, 219))
        self.horizontalLayout = QHBoxLayout(self.widgetFI100B)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.widgetFI100B_1 = QWidget(self.widgetFI100B)
        self.widgetFI100B_1.setObjectName(u"widgetFI100B_1")
        sizePolicy1.setHeightForWidth(self.widgetFI100B_1.sizePolicy().hasHeightForWidth())
        self.widgetFI100B_1.setSizePolicy(sizePolicy1)
        self.widgetFI100B_1.setMinimumSize(QSize(141, 71))
        self.widgetFI100B_1.setAutoFillBackground(False)
        self.widgetFI100B_1.setStyleSheet(u"#widgetFI100B_1 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_7 = QLabel(self.widgetFI100B_1)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVFI100A = QLCDNumber(self.widgetFI100B_1)
        self.lcdPVFI100A.setObjectName(u"lcdPVFI100A")
        self.lcdPVFI100A.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVFI100A.sizePolicy().hasHeightForWidth())
        self.lcdPVFI100A.setSizePolicy(sizePolicy2)
        self.lcdPVFI100A.setSmallDecimalPoint(True)
        self.lcdPVFI100A.setDigitCount(6)
        self.label = QLabel(self.widgetFI100B_1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(95, 40, 41, 16))

        self.verticalLayout_2.addWidget(self.widgetFI100B_1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.widgetFI100A_1 = QWidget(self.widgetFI100B)
        self.widgetFI100A_1.setObjectName(u"widgetFI100A_1")
        sizePolicy1.setHeightForWidth(self.widgetFI100A_1.sizePolicy().hasHeightForWidth())
        self.widgetFI100A_1.setSizePolicy(sizePolicy1)
        self.widgetFI100A_1.setMinimumSize(QSize(31, 201))
        self.widgetFI100A_1.setStyleSheet(u"#widgetFI100A_1 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100A = QSlider(self.widgetFI100A_1)
        self.verticalSliderFV100A.setObjectName(u"verticalSliderFV100A")
        self.verticalSliderFV100A.setGeometry(QRect(6, 14, 20, 181))
        sizePolicy1.setHeightForWidth(self.verticalSliderFV100A.sizePolicy().hasHeightForWidth())
        self.verticalSliderFV100A.setSizePolicy(sizePolicy1)
        self.verticalSliderFV100A.setOrientation(Qt.Orientation.Vertical)

        self.horizontalLayout.addWidget(self.widgetFI100A_1)

        self.widgetVI100 = QWidget(self.oldCtrlGLWidget)
        self.widgetVI100.setObjectName(u"widgetVI100")
        self.widgetVI100.setGeometry(QRect(390, 240, 168, 219))
        self.horizontalLayout_2 = QHBoxLayout(self.widgetVI100)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)

        self.widgetCtrlVI100 = QWidget(self.widgetVI100)
        self.widgetCtrlVI100.setObjectName(u"widgetCtrlVI100")
        self.widgetCtrlVI100.setMinimumSize(QSize(111, 71))
        self.widgetCtrlVI100.setAutoFillBackground(False)
        self.widgetCtrlVI100.setStyleSheet(u"#widgetCtrlVI100{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_30 = QLabel(self.widgetCtrlVI100)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy1)
        self.label_30.setFont(font)
        self.label_30.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPVTIC100_3 = QLCDNumber(self.widgetCtrlVI100)
        self.lcdPVTIC100_3.setObjectName(u"lcdPVTIC100_3")
        self.lcdPVTIC100_3.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPVTIC100_3.sizePolicy().hasHeightForWidth())
        self.lcdPVTIC100_3.setSizePolicy(sizePolicy2)
        self.lcdPVTIC100_3.setSmallDecimalPoint(True)
        self.lcdPVTIC100_3.setDigitCount(6)
        self.label_31 = QLabel(self.widgetCtrlVI100)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setGeometry(QRect(96, 40, 16, 16))

        self.verticalLayout_5.addWidget(self.widgetCtrlVI100)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.widgetSliderVI100 = QWidget(self.widgetVI100)
        self.widgetSliderVI100.setObjectName(u"widgetSliderVI100")
        sizePolicy1.setHeightForWidth(self.widgetSliderVI100.sizePolicy().hasHeightForWidth())
        self.widgetSliderVI100.setSizePolicy(sizePolicy1)
        self.widgetSliderVI100.setMinimumSize(QSize(31, 201))
        self.widgetSliderVI100.setStyleSheet(u"#widgetSliderVI100 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100B = QSlider(self.widgetSliderVI100)
        self.verticalSliderFV100B.setObjectName(u"verticalSliderFV100B")
        self.verticalSliderFV100B.setGeometry(QRect(6, 11, 20, 181))
        self.verticalSliderFV100B.setOrientation(Qt.Orientation.Vertical)

        self.horizontalLayout_2.addWidget(self.widgetSliderVI100)

        self.tabWidget.addTab(self.oldCtrlGLWidget, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.radioButtonHrt.toggled.connect(self.oldDBTableWidget.changeType)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.radioButtonHex.setText(QCoreApplication.translate("MainWindow", u"Machine Value", None))
        self.radioButtonHrt.setText(QCoreApplication.translate("MainWindow", u"Human Value", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Para equa\u00e7\u00f5es inicie o campo 'TYPE' com '@'.", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Para fun\u00e7\u00f5es de transfer\u00eancia em 'S' inicie o campo 'TYPE' com '$'.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tableWidget), QCoreApplication.translate("MainWindow", u"DBase", None))
#if QT_CONFIG(tooltip)
        self.widgetLI100.setToolTip(QCoreApplication.translate("MainWindow", u"N\u00edvel do Tubul\u00e3o Superior", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetLI100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"LI100", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetPI100.setToolTip(QCoreApplication.translate("MainWindow", u"Press\u00e3o na Fornalha", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetPI100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"PI100", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"bar", None))
#if QT_CONFIG(tooltip)
        self.widgetFI100A.setToolTip(QCoreApplication.translate("MainWindow", u"Medidor da Vaz\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFI100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"FI100A", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Nm3/h", None))
#if QT_CONFIG(tooltip)
        self.widgetTI100.setToolTip(QCoreApplication.translate("MainWindow", u"Temperatura da Fornalha", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetTI100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"TI100", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"\u00baC", None))
#if QT_CONFIG(tooltip)
        self.widgetCtrlFV100B.setToolTip(QCoreApplication.translate("MainWindow", u"Valvula da Vaz\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFV100B.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"FV100B", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetFI100B.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFI100B_1.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de Vaz\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFI100B_1.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"FI100B", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Nm3/h", None))
#if QT_CONFIG(tooltip)
        self.widgetFI100A_1.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlVI100.setToolTip(QCoreApplication.translate("MainWindow", u"Velocidade da Esteira de Baga\u00e7o", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlVI100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"VI100", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderVI100.setToolTip(QCoreApplication.translate("MainWindow", u"V\u00e1lvula da Vaz\u00e3o de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100B.setToolTip(QCoreApplication.translate("MainWindow", u"Valvula da Vaz\u00e3o de Agua", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.oldCtrlGLWidget), QCoreApplication.translate("MainWindow", u"CtrlN\u00edvel", None))
    # retranslateUi

