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
        MainWindow.resize(966, 613)
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
        self.buttonGroupState = QButtonGroup(MainWindow)
        self.buttonGroupState.setObjectName(u"buttonGroupState")
        self.buttonGroupState.addButton(self.radioButtonHex)
        self.radioButtonHex.setObjectName(u"radioButtonHex")
        self.radioButtonHex.setChecked(False)

        self.horizontalLayout_9.addWidget(self.radioButtonHex)

        self.radioButtonHrt = QRadioButton(self.hartTab)
        self.buttonGroupState.addButton(self.radioButtonHrt)
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
        self.widgetLI100.setGeometry(QRect(150, 20, 111, 71))
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
        self.widgetFV100AR = QWidget(self.processTab1)
        self.widgetFV100AR.setObjectName(u"widgetFV100AR")
        self.widgetFV100AR.setGeometry(QRect(10, 360, 223, 128))
        sizePolicy2.setHeightForWidth(self.widgetFV100AR.sizePolicy().hasHeightForWidth())
        self.widgetFV100AR.setSizePolicy(sizePolicy2)
        self.widgetFV100AR.setMinimumSize(QSize(223, 128))
        self.verticalLayout_7 = QVBoxLayout(self.widgetFV100AR)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.widgetCtrlFV100AR = QWidget(self.widgetFV100AR)
        self.widgetCtrlFV100AR.setObjectName(u"widgetCtrlFV100AR")
        self.widgetCtrlFV100AR.setMinimumSize(QSize(111, 71))
        self.widgetCtrlFV100AR.setAutoFillBackground(False)
        self.widgetCtrlFV100AR.setStyleSheet(u"#widgetCtrlFV100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_32 = QLabel(self.widgetCtrlFV100AR)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(20, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy1)
        self.label_32.setFont(font)
        self.label_32.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFV100AR = QLCDNumber(self.widgetCtrlFV100AR)
        self.lcdFV100AR.setObjectName(u"lcdFV100AR")
        self.lcdFV100AR.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFV100AR.sizePolicy().hasHeightForWidth())
        self.lcdFV100AR.setSizePolicy(sizePolicy2)
        self.lcdFV100AR.setStyleSheet(u"#lcdFV100AR {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFV100AR.setSmallDecimalPoint(True)
        self.lcdFV100AR.setDigitCount(6)
        self.label_33 = QLabel(self.widgetCtrlFV100AR)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setGeometry(QRect(96, 40, 16, 16))

        self.horizontalLayout_5.addWidget(self.widgetCtrlFV100AR)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_3)

        self.pbAMFV100AR = QPushButton(self.widgetFV100AR)
        self.pbAMFV100AR.setObjectName(u"pbAMFV100AR")
        sizePolicy2.setHeightForWidth(self.pbAMFV100AR.sizePolicy().hasHeightForWidth())
        self.pbAMFV100AR.setSizePolicy(sizePolicy2)
        self.pbAMFV100AR.setMinimumSize(QSize(30, 30))
        self.pbAMFV100AR.setStyleSheet(u"#pbAMFV100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.pbAMFV100AR.setCheckable(True)

        self.verticalLayout_11.addWidget(self.pbAMFV100AR)


        self.horizontalLayout_5.addLayout(self.verticalLayout_11)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.widgetSliderFV100AR = QWidget(self.widgetFV100AR)
        self.widgetSliderFV100AR.setObjectName(u"widgetSliderFV100AR")
        sizePolicy1.setHeightForWidth(self.widgetSliderFV100AR.sizePolicy().hasHeightForWidth())
        self.widgetSliderFV100AR.setSizePolicy(sizePolicy1)
        self.widgetSliderFV100AR.setMinimumSize(QSize(201, 31))
        self.widgetSliderFV100AR.setStyleSheet(u"#widgetSliderFV100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100AR = QSlider(self.widgetSliderFV100AR)
        self.verticalSliderFV100AR.setObjectName(u"verticalSliderFV100AR")
        self.verticalSliderFV100AR.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderFV100AR.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_7.addWidget(self.widgetSliderFV100AR)

        self.widgetFI100V = QWidget(self.processTab1)
        self.widgetFI100V.setObjectName(u"widgetFI100V")
        self.widgetFI100V.setGeometry(QRect(520, 370, 223, 128))
        self.verticalLayout_8 = QVBoxLayout(self.widgetFI100V)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.widgetCtrlFI100V = QWidget(self.widgetFI100V)
        self.widgetCtrlFI100V.setObjectName(u"widgetCtrlFI100V")
        self.widgetCtrlFI100V.setMinimumSize(QSize(131, 71))
        self.widgetCtrlFI100V.setAutoFillBackground(False)
        self.widgetCtrlFI100V.setStyleSheet(u"#widgetCtrlFI100V{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_34 = QLabel(self.widgetCtrlFI100V)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy1)
        self.label_34.setFont(font)
        self.label_34.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFI100V = QLCDNumber(self.widgetCtrlFI100V)
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
        self.label_35 = QLabel(self.widgetCtrlFI100V)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setGeometry(QRect(96, 40, 31, 16))

        self.horizontalLayout_6.addWidget(self.widgetCtrlFI100V)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_4)

        self.pbAMFI100V = QPushButton(self.widgetFI100V)
        self.pbAMFI100V.setObjectName(u"pbAMFI100V")
        sizePolicy2.setHeightForWidth(self.pbAMFI100V.sizePolicy().hasHeightForWidth())
        self.pbAMFI100V.setSizePolicy(sizePolicy2)
        self.pbAMFI100V.setMinimumSize(QSize(30, 30))
        self.pbAMFI100V.setStyleSheet(u"#pbAMFI100V {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.pbAMFI100V.setCheckable(True)

        self.verticalLayout_12.addWidget(self.pbAMFI100V)


        self.horizontalLayout_6.addLayout(self.verticalLayout_12)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.widgetSliderFI100V = QWidget(self.widgetFI100V)
        self.widgetSliderFI100V.setObjectName(u"widgetSliderFI100V")
        sizePolicy1.setHeightForWidth(self.widgetSliderFI100V.sizePolicy().hasHeightForWidth())
        self.widgetSliderFI100V.setSizePolicy(sizePolicy1)
        self.widgetSliderFI100V.setMinimumSize(QSize(201, 31))
        self.widgetSliderFI100V.setStyleSheet(u"#widgetSliderFI100V {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFI100V = QSlider(self.widgetSliderFI100V)
        self.verticalSliderFI100V.setObjectName(u"verticalSliderFI100V")
        self.verticalSliderFI100V.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderFI100V.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_8.addWidget(self.widgetSliderFI100V)

        self.groupBoxSimul = QGroupBox(self.processTab1)
        self.groupBoxSimul.setObjectName(u"groupBoxSimul")
        self.groupBoxSimul.setGeometry(QRect(760, 370, 161, 151))
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxSimul)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButtonStart = QPushButton(self.groupBoxSimul)
        self.buttonGroupSimul = QButtonGroup(MainWindow)
        self.buttonGroupSimul.setObjectName(u"buttonGroupSimul")
        self.buttonGroupSimul.addButton(self.pushButtonStart)
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
        self.buttonGroupSimul.addButton(self.pushButtonStop)
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

        self.widgetFV100CA = QWidget(self.processTab1)
        self.widgetFV100CA.setObjectName(u"widgetFV100CA")
        self.widgetFV100CA.setGeometry(QRect(670, 230, 223, 128))
        self.verticalLayout_13 = QVBoxLayout(self.widgetFV100CA)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_9)

        self.widgetCtrlFV100CA = QWidget(self.widgetFV100CA)
        self.widgetCtrlFV100CA.setObjectName(u"widgetCtrlFV100CA")
        self.widgetCtrlFV100CA.setMinimumSize(QSize(111, 71))
        self.widgetCtrlFV100CA.setAutoFillBackground(False)
        self.widgetCtrlFV100CA.setStyleSheet(u"#widgetCtrlFV100CA{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_36 = QLabel(self.widgetCtrlFV100CA)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy1)
        self.label_36.setFont(font)
        self.label_36.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFV100CA = QLCDNumber(self.widgetCtrlFV100CA)
        self.lcdFV100CA.setObjectName(u"lcdFV100CA")
        self.lcdFV100CA.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFV100CA.sizePolicy().hasHeightForWidth())
        self.lcdFV100CA.setSizePolicy(sizePolicy2)
        self.lcdFV100CA.setStyleSheet(u"#lcdFV100CA {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFV100CA.setSmallDecimalPoint(True)
        self.lcdFV100CA.setDigitCount(6)
        self.label_37 = QLabel(self.widgetCtrlFV100CA)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setGeometry(QRect(96, 40, 16, 16))

        self.horizontalLayout_12.addWidget(self.widgetCtrlFV100CA)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_7)

        self.pbAMFV100CA = QPushButton(self.widgetFV100CA)
        self.pbAMFV100CA.setObjectName(u"pbAMFV100CA")
        sizePolicy2.setHeightForWidth(self.pbAMFV100CA.sizePolicy().hasHeightForWidth())
        self.pbAMFV100CA.setSizePolicy(sizePolicy2)
        self.pbAMFV100CA.setMinimumSize(QSize(30, 30))
        self.pbAMFV100CA.setStyleSheet(u"#pbAMFV100CA {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.pbAMFV100CA.setCheckable(True)

        self.verticalLayout_14.addWidget(self.pbAMFV100CA)


        self.horizontalLayout_12.addLayout(self.verticalLayout_14)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_10)


        self.verticalLayout_13.addLayout(self.horizontalLayout_12)

        self.widgetSliderFV100CA = QWidget(self.widgetFV100CA)
        self.widgetSliderFV100CA.setObjectName(u"widgetSliderFV100CA")
        sizePolicy1.setHeightForWidth(self.widgetSliderFV100CA.sizePolicy().hasHeightForWidth())
        self.widgetSliderFV100CA.setSizePolicy(sizePolicy1)
        self.widgetSliderFV100CA.setMinimumSize(QSize(201, 31))
        self.widgetSliderFV100CA.setStyleSheet(u"#widgetSliderFV100CA {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100CA = QSlider(self.widgetSliderFV100CA)
        self.verticalSliderFV100CA.setObjectName(u"verticalSliderFV100CA")
        self.verticalSliderFV100CA.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderFV100CA.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_13.addWidget(self.widgetSliderFV100CA)

        self.widgetPI100A = QWidget(self.processTab1)
        self.widgetPI100A.setObjectName(u"widgetPI100A")
        self.widgetPI100A.setGeometry(QRect(250, 340, 223, 128))
        self.verticalLayout_15 = QVBoxLayout(self.widgetPI100A)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_11)

        self.widgetCtrlPI100A = QWidget(self.widgetPI100A)
        self.widgetCtrlPI100A.setObjectName(u"widgetCtrlPI100A")
        self.widgetCtrlPI100A.setMinimumSize(QSize(131, 71))
        self.widgetCtrlPI100A.setAutoFillBackground(False)
        self.widgetCtrlPI100A.setStyleSheet(u"#widgetCtrlPI100A{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_38 = QLabel(self.widgetCtrlPI100A)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_38.sizePolicy().hasHeightForWidth())
        self.label_38.setSizePolicy(sizePolicy1)
        self.label_38.setFont(font)
        self.label_38.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPI100A = QLCDNumber(self.widgetCtrlPI100A)
        self.lcdPI100A.setObjectName(u"lcdPI100A")
        self.lcdPI100A.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPI100A.sizePolicy().hasHeightForWidth())
        self.lcdPI100A.setSizePolicy(sizePolicy2)
        self.lcdPI100A.setStyleSheet(u"#lcdPI100A {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdPI100A.setSmallDecimalPoint(True)
        self.lcdPI100A.setDigitCount(6)
        self.label_39 = QLabel(self.widgetCtrlPI100A)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setGeometry(QRect(96, 40, 31, 16))

        self.horizontalLayout_13.addWidget(self.widgetCtrlPI100A)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_8)

        self.pbAMPI100A = QPushButton(self.widgetPI100A)
        self.pbAMPI100A.setObjectName(u"pbAMPI100A")
        sizePolicy2.setHeightForWidth(self.pbAMPI100A.sizePolicy().hasHeightForWidth())
        self.pbAMPI100A.setSizePolicy(sizePolicy2)
        self.pbAMPI100A.setMinimumSize(QSize(30, 30))
        self.pbAMPI100A.setStyleSheet(u"#pbAMPI100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.pbAMPI100A.setCheckable(True)

        self.verticalLayout_16.addWidget(self.pbAMPI100A)


        self.horizontalLayout_13.addLayout(self.verticalLayout_16)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)


        self.verticalLayout_15.addLayout(self.horizontalLayout_13)

        self.widgetSliderPI100A = QWidget(self.widgetPI100A)
        self.widgetSliderPI100A.setObjectName(u"widgetSliderPI100A")
        sizePolicy1.setHeightForWidth(self.widgetSliderPI100A.sizePolicy().hasHeightForWidth())
        self.widgetSliderPI100A.setSizePolicy(sizePolicy1)
        self.widgetSliderPI100A.setMinimumSize(QSize(201, 31))
        self.widgetSliderPI100A.setStyleSheet(u"#widgetSliderPI100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFI100V_2 = QSlider(self.widgetSliderPI100A)
        self.verticalSliderFI100V_2.setObjectName(u"verticalSliderFI100V_2")
        self.verticalSliderFI100V_2.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderFI100V_2.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_15.addWidget(self.widgetSliderPI100A)

        self.widgetFV100A = QWidget(self.processTab1)
        self.widgetFV100A.setObjectName(u"widgetFV100A")
        self.widgetFV100A.setGeometry(QRect(240, 170, 223, 128))
        sizePolicy2.setHeightForWidth(self.widgetFV100A.sizePolicy().hasHeightForWidth())
        self.widgetFV100A.setSizePolicy(sizePolicy2)
        self.widgetFV100A.setMinimumSize(QSize(223, 128))
        self.verticalLayout_17 = QVBoxLayout(self.widgetFV100A)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_13)

        self.widgetCtrlFV100A = QWidget(self.widgetFV100A)
        self.widgetCtrlFV100A.setObjectName(u"widgetCtrlFV100A")
        self.widgetCtrlFV100A.setMinimumSize(QSize(111, 71))
        self.widgetCtrlFV100A.setAutoFillBackground(False)
        self.widgetCtrlFV100A.setStyleSheet(u"#widgetCtrlFV100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_40 = QLabel(self.widgetCtrlFV100A)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setGeometry(QRect(20, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_40.sizePolicy().hasHeightForWidth())
        self.label_40.setSizePolicy(sizePolicy1)
        self.label_40.setFont(font)
        self.label_40.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
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
        self.label_41 = QLabel(self.widgetCtrlFV100A)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setGeometry(QRect(96, 40, 16, 16))

        self.horizontalLayout_14.addWidget(self.widgetCtrlFV100A)

        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_5)

        self.pbAMFV100A = QPushButton(self.widgetFV100A)
        self.pbAMFV100A.setObjectName(u"pbAMFV100A")
        sizePolicy2.setHeightForWidth(self.pbAMFV100A.sizePolicy().hasHeightForWidth())
        self.pbAMFV100A.setSizePolicy(sizePolicy2)
        self.pbAMFV100A.setMinimumSize(QSize(30, 30))
        self.pbAMFV100A.setStyleSheet(u"#pbAMFV100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.pbAMFV100A.setCheckable(True)

        self.verticalLayout_18.addWidget(self.pbAMFV100A)


        self.horizontalLayout_14.addLayout(self.verticalLayout_18)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_14)


        self.verticalLayout_17.addLayout(self.horizontalLayout_14)

        self.widgetSliderFV100A = QWidget(self.widgetFV100A)
        self.widgetSliderFV100A.setObjectName(u"widgetSliderFV100A")
        sizePolicy1.setHeightForWidth(self.widgetSliderFV100A.sizePolicy().hasHeightForWidth())
        self.widgetSliderFV100A.setSizePolicy(sizePolicy1)
        self.widgetSliderFV100A.setMinimumSize(QSize(201, 31))
        self.widgetSliderFV100A.setStyleSheet(u"#widgetSliderFV100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.verticalSliderFV100A = QSlider(self.widgetSliderFV100A)
        self.verticalSliderFV100A.setObjectName(u"verticalSliderFV100A")
        self.verticalSliderFV100A.setGeometry(QRect(4, 7, 201, 20))
        self.verticalSliderFV100A.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_17.addWidget(self.widgetSliderFV100A)

        self.widgetFI100CA = QWidget(self.processTab1)
        self.widgetFI100CA.setObjectName(u"widgetFI100CA")
        self.widgetFI100CA.setGeometry(QRect(300, 20, 111, 71))
        self.widgetFI100CA.setMinimumSize(QSize(111, 71))
        self.widgetFI100CA.setAutoFillBackground(False)
        self.widgetFI100CA.setStyleSheet(u"#widgetFI100CA {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_4 = QLabel(self.widgetFI100CA)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.label_28 = QLabel(self.widgetFI100CA)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(95, 40, 21, 16))
        self.lcdFI100CA = QLCDNumber(self.widgetFI100CA)
        self.lcdFI100CA.setObjectName(u"lcdFI100CA")
        self.lcdFI100CA.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFI100CA.sizePolicy().hasHeightForWidth())
        self.lcdFI100CA.setSizePolicy(sizePolicy2)
        self.lcdFI100CA.setStyleSheet(u"#lcdFI100CA {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFI100CA.setSmallDecimalPoint(True)
        self.lcdFI100CA.setDigitCount(6)
        self.widgetFI100AR = QWidget(self.processTab1)
        self.widgetFI100AR.setObjectName(u"widgetFI100AR")
        self.widgetFI100AR.setGeometry(QRect(450, 20, 111, 71))
        self.widgetFI100AR.setMinimumSize(QSize(111, 71))
        self.widgetFI100AR.setAutoFillBackground(False)
        self.widgetFI100AR.setStyleSheet(u"#widgetFI100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_5 = QLabel(self.widgetFI100AR)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.label_29 = QLabel(self.widgetFI100AR)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(95, 40, 21, 16))
        self.lcdFI100AR = QLCDNumber(self.widgetFI100AR)
        self.lcdFI100AR.setObjectName(u"lcdFI100AR")
        self.lcdFI100AR.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFI100AR.sizePolicy().hasHeightForWidth())
        self.lcdFI100AR.setSizePolicy(sizePolicy2)
        self.lcdFI100AR.setStyleSheet(u"#lcdFI100AR {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFI100AR.setSmallDecimalPoint(True)
        self.lcdFI100AR.setDigitCount(6)
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
        self.widgetFV100AR.setToolTip(QCoreApplication.translate("MainWindow", u"Abertura do damper de AR", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFV100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFV100AR.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"FV100AR", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.pbAMFV100AR.setText(QCoreApplication.translate("MainWindow", u"M", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFV100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFI100V.setToolTip(QCoreApplication.translate("MainWindow", u"Vaz\u00e3o de vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFI100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFI100V.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"FI100V", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"kg/s", None))
        self.pbAMFI100V.setText(QCoreApplication.translate("MainWindow", u"M", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFI100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFI100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBoxSimul.setTitle(QCoreApplication.translate("MainWindow", u"Simula\u00e7\u00e3o", None))
        self.pushButtonStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButtonStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.pushButtonReset.setText(QCoreApplication.translate("MainWindow", u"reset", None))
#if QT_CONFIG(tooltip)
        self.widgetFV100CA.setToolTip(QCoreApplication.translate("MainWindow", u"Abertura da v\u00e1lvula de combustivel", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFV100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFV100CA.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"FV100CA", None))
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.pbAMFV100CA.setText(QCoreApplication.translate("MainWindow", u"M", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFV100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetPI100A.setToolTip(QCoreApplication.translate("MainWindow", u"Velocidade da bomba de \u00e1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlPI100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlPI100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"PI100A", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"kPa", None))
        self.pbAMPI100A.setText(QCoreApplication.translate("MainWindow", u"M", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderPI100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFI100V_2.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Abertura do damper de AR", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFV100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFV100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"FV100A", None))
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.pbAMFV100A.setText(QCoreApplication.translate("MainWindow", u"M", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFV100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.verticalSliderFV100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFI100CA.setToolTip(QCoreApplication.translate("MainWindow", u"N\u00edvel do Tubul\u00e3o Superior", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFI100CA.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"FI100CA", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetFI100AR.setToolTip(QCoreApplication.translate("MainWindow", u"N\u00edvel do Tubul\u00e3o Superior", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFI100AR.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"FI100AR", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.processTab1), QCoreApplication.translate("MainWindow", u"Process", None))
    # retranslateUi

