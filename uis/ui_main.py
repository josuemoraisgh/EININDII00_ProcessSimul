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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QGroupBox, QHBoxLayout,
    QLCDNumber, QLabel, QMainWindow, QPushButton,
    QRadioButton, QSizePolicy, QSlider, QSpacerItem,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget)

from comp.ctrlglwidget import CtrlGLWidget
from comp.dbtablewidget import DBTableWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1001, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainTab = QTabWidget(self.centralwidget)
        self.mainTab.setObjectName(u"mainTab")
        self.mainTab.setAutoFillBackground(True)
        self.configTab = QWidget()
        self.configTab.setObjectName(u"configTab")
        self.mainTab.addTab(self.configTab, "")
        self.modbusTab = QWidget()
        self.modbusTab.setObjectName(u"modbusTab")
        self.verticalLayout_10 = QVBoxLayout(self.modbusTab)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.radioButtonHex_2 = QRadioButton(self.modbusTab)
        self.radioButtonHex_2.setObjectName(u"radioButtonHex_2")
        self.radioButtonHex_2.setChecked(False)

        self.horizontalLayout_10.addWidget(self.radioButtonHex_2)

        self.radioButtonHrt_2 = QRadioButton(self.modbusTab)
        self.radioButtonHrt_2.setObjectName(u"radioButtonHrt_2")
        self.radioButtonHrt_2.setChecked(True)

        self.horizontalLayout_10.addWidget(self.radioButtonHrt_2)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_3)


        self.verticalLayout_9.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_5)


        self.verticalLayout_9.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_10.addLayout(self.verticalLayout_9)


        self.verticalLayout_10.addLayout(self.horizontalLayout_10)

        self.mbDBTableWidget = DBTableWidget(self.modbusTab)
        self.mbDBTableWidget.setObjectName(u"mbDBTableWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mbDBTableWidget.sizePolicy().hasHeightForWidth())
        self.mbDBTableWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_10.addWidget(self.mbDBTableWidget)

        self.mainTab.addTab(self.modbusTab, "")
        self.hartTab = QWidget()
        self.hartTab.setObjectName(u"hartTab")
        self.verticalLayout_4 = QVBoxLayout(self.hartTab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.radioButtonHex = QRadioButton(self.hartTab)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButtonHex)
        self.radioButtonHex.setObjectName(u"radioButtonHex")
        self.radioButtonHex.setChecked(False)

        self.horizontalLayout_9.addWidget(self.radioButtonHex)

        self.radioButtonHrt = QRadioButton(self.hartTab)
        self.buttonGroup.addButton(self.radioButtonHrt)
        self.radioButtonHrt.setObjectName(u"radioButtonHrt")
        self.radioButtonHrt.setChecked(True)

        self.horizontalLayout_9.addWidget(self.radioButtonHrt)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_9.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.hrtDBTableWidget = DBTableWidget(self.hartTab)
        self.hrtDBTableWidget.setObjectName(u"hrtDBTableWidget")
        sizePolicy.setHeightForWidth(self.hrtDBTableWidget.sizePolicy().hasHeightForWidth())
        self.hrtDBTableWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_4.addWidget(self.hrtDBTableWidget)

        self.mainTab.addTab(self.hartTab, "")
        self.processTab1 = CtrlGLWidget()
        self.processTab1.setObjectName(u"processTab1")
        self.widgetLI100 = QWidget(self.processTab1)
        self.widgetLI100.setObjectName(u"widgetLI100")
        self.widgetLI100.setGeometry(QRect(500, 10, 111, 71))
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
        self.lcdLI100 = QLCDNumber(self.widgetLI100)
        self.lcdLI100.setObjectName(u"lcdLI100")
        self.lcdLI100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lcdLI100.sizePolicy().hasHeightForWidth())
        self.lcdLI100.setSizePolicy(sizePolicy2)
        self.lcdLI100.setStyleSheet(u"#lcdLI100 {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdLI100.setSmallDecimalPoint(True)
        self.lcdLI100.setDigitCount(6)
        self.widgetPI100V = QWidget(self.processTab1)
        self.widgetPI100V.setObjectName(u"widgetPI100V")
        self.widgetPI100V.setGeometry(QRect(0, 10, 121, 71))
        font1 = QFont()
        font1.setUnderline(False)
        font1.setStrikeOut(False)
        self.widgetPI100V.setFont(font1)
        self.widgetPI100V.setTabletTracking(False)
        self.widgetPI100V.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.widgetPI100V.setAutoFillBackground(False)
        self.widgetPI100V.setStyleSheet(u"#widgetPI100V{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_6 = QLabel(self.widgetPI100V)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setPointSize(12)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        self.label_6.setFont(font2)
        self.label_6.setLineWidth(2)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPI100V = QLCDNumber(self.widgetPI100V)
        self.lcdPI100V.setObjectName(u"lcdPI100V")
        self.lcdPI100V.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPI100V.sizePolicy().hasHeightForWidth())
        self.lcdPI100V.setSizePolicy(sizePolicy2)
        self.lcdPI100V.setStyleSheet(u"#lcdPI100V {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdPI100V.setSmallDecimalPoint(True)
        self.lcdPI100V.setDigitCount(6)
        self.label_26 = QLabel(self.widgetPI100V)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(95, 40, 41, 16))
        self.widgetFI100A = QWidget(self.processTab1)
        self.widgetFI100A.setObjectName(u"widgetFI100A")
        self.widgetFI100A.setGeometry(QRect(0, 170, 141, 60))
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
        self.label_8.setGeometry(QRect(30, 2, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFI100A = QLCDNumber(self.widgetFI100A)
        self.lcdFI100A.setObjectName(u"lcdFI100A")
        self.lcdFI100A.setGeometry(QRect(10, 25, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFI100A.sizePolicy().hasHeightForWidth())
        self.lcdFI100A.setSizePolicy(sizePolicy2)
        self.lcdFI100A.setStyleSheet(u"#lcdFI100A {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFI100A.setSmallDecimalPoint(True)
        self.lcdFI100A.setDigitCount(6)
        self.label_25 = QLabel(self.widgetFI100A)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(95, 33, 41, 16))
        self.widgetTI100 = QWidget(self.processTab1)
        self.widgetTI100.setObjectName(u"widgetTI100")
        self.widgetTI100.setGeometry(QRect(0, 90, 121, 71))
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
        self.lcdTI100 = QLCDNumber(self.widgetTI100)
        self.lcdTI100.setObjectName(u"lcdTI100")
        self.lcdTI100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdTI100.sizePolicy().hasHeightForWidth())
        self.lcdTI100.setSizePolicy(sizePolicy2)
        self.lcdTI100.setStyleSheet(u"#lcdTI100 {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdTI100.setSmallDecimalPoint(True)
        self.lcdTI100.setDigitCount(6)
        self.label_27 = QLabel(self.widgetTI100)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(96, 40, 21, 16))
        self.widgetFI100V = QWidget(self.processTab1)
        self.widgetFI100V.setObjectName(u"widgetFI100V")
        self.widgetFI100V.setGeometry(QRect(140, 10, 198, 219))
        self.horizontalLayout = QHBoxLayout(self.widgetFI100V)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widgetFI100V_2 = QWidget(self.widgetFI100V)
        self.widgetFI100V_2.setObjectName(u"widgetFI100V_2")
        sizePolicy1.setHeightForWidth(self.widgetFI100V_2.sizePolicy().hasHeightForWidth())
        self.widgetFI100V_2.setSizePolicy(sizePolicy1)
        self.widgetFI100V_2.setMinimumSize(QSize(31, 201))
        self.widgetFI100V_2.setStyleSheet(u"#widgetFI100V_2 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFI100V = QSlider(self.widgetFI100V_2)
        self.verticalSliderFI100V.setObjectName(u"verticalSliderFI100V")
        self.verticalSliderFI100V.setGeometry(QRect(6, 14, 20, 181))
        sizePolicy1.setHeightForWidth(self.verticalSliderFI100V.sizePolicy().hasHeightForWidth())
        self.verticalSliderFI100V.setSizePolicy(sizePolicy1)
        self.verticalSliderFI100V.setOrientation(Qt.Orientation.Vertical)

        self.horizontalLayout.addWidget(self.widgetFI100V_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.widgetFI100V_1 = QWidget(self.widgetFI100V)
        self.widgetFI100V_1.setObjectName(u"widgetFI100V_1")
        sizePolicy1.setHeightForWidth(self.widgetFI100V_1.sizePolicy().hasHeightForWidth())
        self.widgetFI100V_1.setSizePolicy(sizePolicy1)
        self.widgetFI100V_1.setMinimumSize(QSize(141, 71))
        self.widgetFI100V_1.setAutoFillBackground(False)
        self.widgetFI100V_1.setStyleSheet(u"#widgetFI100V_1 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_7 = QLabel(self.widgetFI100V_1)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFI100V = QLCDNumber(self.widgetFI100V_1)
        self.lcdFI100V.setObjectName(u"lcdFI100V")
        self.lcdFI100V.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFI100V.sizePolicy().hasHeightForWidth())
        self.lcdFI100V.setSizePolicy(sizePolicy2)
        self.lcdFI100V.setStyleSheet(u"#lcdFI100V {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFI100V.setSmallDecimalPoint(True)
        self.lcdFI100V.setDigitCount(6)
        self.label = QLabel(self.widgetFI100V_1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(95, 40, 41, 16))

        self.verticalLayout_2.addWidget(self.widgetFI100V_1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.widgetFV100A = QWidget(self.processTab1)
        self.widgetFV100A.setObjectName(u"widgetFV100A")
        self.widgetFV100A.setGeometry(QRect(340, 10, 168, 219))
        self.horizontalLayout_4 = QHBoxLayout(self.widgetFV100A)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_5)

        self.widgetCtrlFV100A = QWidget(self.widgetFV100A)
        self.widgetCtrlFV100A.setObjectName(u"widgetCtrlFV100A")
        self.widgetCtrlFV100A.setMinimumSize(QSize(111, 71))
        self.widgetCtrlFV100A.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.widgetCtrlFV100A.setAutoFillBackground(False)
        self.widgetCtrlFV100A.setStyleSheet(u"#widgetCtrlFV100A{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_12 = QLabel(self.widgetCtrlFV100A)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(19, 7, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)
        self.label_12.setFont(font)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFV100A = QLCDNumber(self.widgetCtrlFV100A)
        self.lcdFV100A.setObjectName(u"lcdFV100A")
        self.lcdFV100A.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFV100A.sizePolicy().hasHeightForWidth())
        self.lcdFV100A.setSizePolicy(sizePolicy2)
        self.lcdFV100A.setStyleSheet(u"#lcdFV100A {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFV100A.setSmallDecimalPoint(True)
        self.lcdFV100A.setDigitCount(6)
        self.label_23 = QLabel(self.widgetCtrlFV100A)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(95, 40, 21, 16))

        self.verticalLayout_6.addWidget(self.widgetCtrlFV100A)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_6)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)

        self.widgetSliderFV100A = QWidget(self.widgetFV100A)
        self.widgetSliderFV100A.setObjectName(u"widgetSliderFV100A")
        sizePolicy1.setHeightForWidth(self.widgetSliderFV100A.sizePolicy().hasHeightForWidth())
        self.widgetSliderFV100A.setSizePolicy(sizePolicy1)
        self.widgetSliderFV100A.setMinimumSize(QSize(31, 201))
        self.widgetSliderFV100A.setStyleSheet(u"#widgetSliderFV100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100A_1 = QSlider(self.widgetSliderFV100A)
        self.verticalSliderFV100A_1.setObjectName(u"verticalSliderFV100A_1")
        self.verticalSliderFV100A_1.setGeometry(QRect(6, 11, 20, 181))
        self.verticalSliderFV100A_1.setOrientation(Qt.Orientation.Vertical)

        self.horizontalLayout_4.addWidget(self.widgetSliderFV100A)

        self.widgetVI100AR = QWidget(self.processTab1)
        self.widgetVI100AR.setObjectName(u"widgetVI100AR")
        self.widgetVI100AR.setGeometry(QRect(390, 230, 223, 128))
        self.verticalLayout_7 = QVBoxLayout(self.widgetVI100AR)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.widgetCtrlVI100AR = QWidget(self.widgetVI100AR)
        self.widgetCtrlVI100AR.setObjectName(u"widgetCtrlVI100AR")
        self.widgetCtrlVI100AR.setMinimumSize(QSize(111, 71))
        self.widgetCtrlVI100AR.setAutoFillBackground(False)
        self.widgetCtrlVI100AR.setStyleSheet(u"#widgetCtrlVI100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_32 = QLabel(self.widgetCtrlVI100AR)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(20, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy1)
        self.label_32.setFont(font)
        self.label_32.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdVI100AR = QLCDNumber(self.widgetCtrlVI100AR)
        self.lcdVI100AR.setObjectName(u"lcdVI100AR")
        self.lcdVI100AR.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdVI100AR.sizePolicy().hasHeightForWidth())
        self.lcdVI100AR.setSizePolicy(sizePolicy2)
        self.lcdVI100AR.setStyleSheet(u"#lcdVI100AR {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdVI100AR.setSmallDecimalPoint(True)
        self.lcdVI100AR.setDigitCount(6)
        self.label_33 = QLabel(self.widgetCtrlVI100AR)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setGeometry(QRect(96, 40, 16, 16))

        self.horizontalLayout_5.addWidget(self.widgetCtrlVI100AR)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.widgetSliderVI100AR = QWidget(self.widgetVI100AR)
        self.widgetSliderVI100AR.setObjectName(u"widgetSliderVI100AR")
        sizePolicy1.setHeightForWidth(self.widgetSliderVI100AR.sizePolicy().hasHeightForWidth())
        self.widgetSliderVI100AR.setSizePolicy(sizePolicy1)
        self.widgetSliderVI100AR.setMinimumSize(QSize(201, 31))
        self.widgetSliderVI100AR.setStyleSheet(u"#widgetSliderVI100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderVI100AR = QSlider(self.widgetSliderVI100AR)
        self.verticalSliderVI100AR.setObjectName(u"verticalSliderVI100AR")
        self.verticalSliderVI100AR.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderVI100AR.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_7.addWidget(self.widgetSliderVI100AR)

        self.widgetVI100CA = QWidget(self.processTab1)
        self.widgetVI100CA.setObjectName(u"widgetVI100CA")
        self.widgetVI100CA.setGeometry(QRect(390, 360, 223, 128))
        self.verticalLayout_8 = QVBoxLayout(self.widgetVI100CA)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.widgetCtrlVI100CA = QWidget(self.widgetVI100CA)
        self.widgetCtrlVI100CA.setObjectName(u"widgetCtrlVI100CA")
        self.widgetCtrlVI100CA.setMinimumSize(QSize(111, 71))
        self.widgetCtrlVI100CA.setAutoFillBackground(False)
        self.widgetCtrlVI100CA.setStyleSheet(u"#widgetCtrlVI100CA{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_34 = QLabel(self.widgetCtrlVI100CA)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy1)
        self.label_34.setFont(font)
        self.label_34.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdVI100CA = QLCDNumber(self.widgetCtrlVI100CA)
        self.lcdVI100CA.setObjectName(u"lcdVI100CA")
        self.lcdVI100CA.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdVI100CA.sizePolicy().hasHeightForWidth())
        self.lcdVI100CA.setSizePolicy(sizePolicy2)
        self.lcdVI100CA.setStyleSheet(u"#lcdVI100CA {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdVI100CA.setSmallDecimalPoint(True)
        self.lcdVI100CA.setDigitCount(6)
        self.label_35 = QLabel(self.widgetCtrlVI100CA)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setGeometry(QRect(96, 40, 16, 16))

        self.horizontalLayout_6.addWidget(self.widgetCtrlVI100CA)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.widgetSliderVI100CA = QWidget(self.widgetVI100CA)
        self.widgetSliderVI100CA.setObjectName(u"widgetSliderVI100CA")
        sizePolicy1.setHeightForWidth(self.widgetSliderVI100CA.sizePolicy().hasHeightForWidth())
        self.widgetSliderVI100CA.setSizePolicy(sizePolicy1)
        self.widgetSliderVI100CA.setMinimumSize(QSize(201, 31))
        self.widgetSliderVI100CA.setStyleSheet(u"#widgetSliderVI100CA {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderVI100CA = QSlider(self.widgetSliderVI100CA)
        self.verticalSliderVI100CA.setObjectName(u"verticalSliderVI100CA")
        self.verticalSliderVI100CA.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderVI100CA.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_8.addWidget(self.widgetSliderVI100CA)

        self.groupBoxSimul = QGroupBox(self.processTab1)
        self.groupBoxSimul.setObjectName(u"groupBoxSimul")
        self.groupBoxSimul.setGeometry(QRect(810, 380, 161, 151))
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxSimul)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButtonStart = QPushButton(self.groupBoxSimul)
        self.buttonGroup_2 = QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.pushButtonStart)
        self.pushButtonStart.setObjectName(u"pushButtonStart")
        self.pushButtonStart.setStyleSheet(u"#pushButtonStart {\n"
"    background-color: none;  /* Cor padr\u00e3o quando solto */\n"
"}\n"
"\n"
"#pushButtonStart:checked {\n"
"    background-color: green;  /* Verde quando pressionado */\n"
"}")
        self.pushButtonStart.setCheckable(True)

        self.verticalLayout_5.addWidget(self.pushButtonStart)

        self.pushButtonStop = QPushButton(self.groupBoxSimul)
        self.buttonGroup_2.addButton(self.pushButtonStop)
        self.pushButtonStop.setObjectName(u"pushButtonStop")
        self.pushButtonStop.setStyleSheet(u"#pushButtonStop {\n"
"    background-color: none;  /* Cor padr\u00e3o (normal) do sistema quando solto */\n"
"}\n"
"\n"
"#pushButtonStop:checked {\n"
"    background-color: red;  /* Verde quando pressionado */\n"
"}")
        self.pushButtonStop.setCheckable(True)
        self.pushButtonStop.setChecked(True)

        self.verticalLayout_5.addWidget(self.pushButtonStop)

        self.pushButtonReset = QPushButton(self.groupBoxSimul)
        self.pushButtonReset.setObjectName(u"pushButtonReset")
        self.pushButtonReset.setStyleSheet(u"#pushButtonReset{\n"
"    background-color: yellow;  /* Cor padr\u00e3o quando solto */\n"
"}\n"
"")
        self.pushButtonReset.setCheckable(False)

        self.verticalLayout_5.addWidget(self.pushButtonReset)

        self.mainTab.addTab(self.processTab1, "")

        self.verticalLayout.addWidget(self.mainTab)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.radioButtonHrt.toggled.connect(self.hrtDBTableWidget.changeType)

        self.mainTab.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.configTab), QCoreApplication.translate("MainWindow", u"Config", None))
        self.radioButtonHex_2.setText(QCoreApplication.translate("MainWindow", u"Machine Value", None))
        self.radioButtonHrt_2.setText(QCoreApplication.translate("MainWindow", u"Human Value", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.modbusTab), QCoreApplication.translate("MainWindow", u"ModBus", None))
        self.radioButtonHex.setText(QCoreApplication.translate("MainWindow", u"Machine Value", None))
        self.radioButtonHrt.setText(QCoreApplication.translate("MainWindow", u"Human Value", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.hartTab), QCoreApplication.translate("MainWindow", u"Hart", None))
#if QT_CONFIG(tooltip)
        self.widgetLI100.setToolTip(QCoreApplication.translate("MainWindow", u"N\u00edvel do Tubul\u00e3o Superior", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetLI100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"LI100", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetPI100V.setToolTip(QCoreApplication.translate("MainWindow", u"Press\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetPI100V.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"PI100V", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"bar", None))
#if QT_CONFIG(tooltip)
        self.widgetFI100A.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador da Vaz\u00e3o de \u00c1gua", None))
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
        self.widgetFI100V.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFI100V_2.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFI100V.setToolTip(QCoreApplication.translate("MainWindow", u"Seletor de demanda de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFI100V_1.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de Vaz\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFI100V_1.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"FI100V", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Nm3/h", None))
#if QT_CONFIG(tooltip)
        self.widgetFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Posicionador da V\u00e1lvula de Vaz\u00e3o de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Posicionador da V\u00e1lvula de Vaz\u00e3o de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFV100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"FV100A", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Posicionador da V\u00e1lvula de Vaz\u00e3o de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100A_1.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Posicionador da V\u00e1lvula de Vaz\u00e3o de \u00c1gua</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetVI100AR.setToolTip(QCoreApplication.translate("MainWindow", u"Velocidade do Ventilador de AR", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlVI100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlVI100AR.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"VI100AR", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderVI100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderVI100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetVI100CA.setToolTip(QCoreApplication.translate("MainWindow", u"Velocidade das Esteiras de Cavaco", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlVI100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlVI100CA.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"VI100CA", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderVI100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderVI100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBoxSimul.setTitle(QCoreApplication.translate("MainWindow", u"Simula\u00e7\u00e3o", None))
        self.pushButtonStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButtonStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.pushButtonReset.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.processTab1), QCoreApplication.translate("MainWindow", u"Process", None))
    # retranslateUi

