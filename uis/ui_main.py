# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QLCDNumber, QLabel, QLineEdit, QMainWindow,
    QPushButton, QRadioButton, QSizePolicy, QSlider,
    QSpacerItem, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

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
        self.widgetLIT100 = QWidget(self.processTab1)
        self.widgetLIT100.setObjectName(u"widgetLIT100")
        self.widgetLIT100.setGeometry(QRect(150, 20, 111, 71))
        self.widgetLIT100.setMinimumSize(QSize(111, 71))
        self.widgetLIT100.setAutoFillBackground(False)
        self.widgetLIT100.setStyleSheet(u"#widgetLIT100 {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_3 = QLabel(self.widgetLIT100)
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
        self.label_24 = QLabel(self.widgetLIT100)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(95, 40, 21, 16))
        self.lcdLIT100 = QLCDNumber(self.widgetLIT100)
        self.lcdLIT100.setObjectName(u"lcdLIT100")
        self.lcdLIT100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lcdLIT100.sizePolicy().hasHeightForWidth())
        self.lcdLIT100.setSizePolicy(sizePolicy2)
        self.lcdLIT100.setStyleSheet(u"#lcdLIT100 {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdLIT100.setSmallDecimalPoint(True)
        self.lcdLIT100.setDigitCount(6)
        self.widgetPIT100V = QWidget(self.processTab1)
        self.widgetPIT100V.setObjectName(u"widgetPIT100V")
        self.widgetPIT100V.setGeometry(QRect(0, 10, 121, 71))
        font1 = QFont()
        font1.setUnderline(False)
        font1.setStrikeOut(False)
        self.widgetPIT100V.setFont(font1)
        self.widgetPIT100V.setTabletTracking(False)
        self.widgetPIT100V.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.widgetPIT100V.setAutoFillBackground(False)
        self.widgetPIT100V.setStyleSheet(u"#widgetPIT100V{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_6 = QLabel(self.widgetPIT100V)
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
        self.lcdPIT100V = QLCDNumber(self.widgetPIT100V)
        self.lcdPIT100V.setObjectName(u"lcdPIT100V")
        self.lcdPIT100V.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPIT100V.sizePolicy().hasHeightForWidth())
        self.lcdPIT100V.setSizePolicy(sizePolicy2)
        self.lcdPIT100V.setStyleSheet(u"#lcdPIT100V {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdPIT100V.setSmallDecimalPoint(True)
        self.lcdPIT100V.setDigitCount(6)
        self.label_26 = QLabel(self.widgetPIT100V)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(95, 40, 41, 16))
        self.widgetFIT100A = QWidget(self.processTab1)
        self.widgetFIT100A.setObjectName(u"widgetFIT100A")
        self.widgetFIT100A.setGeometry(QRect(0, 170, 131, 60))
        self.widgetFIT100A.setAutoFillBackground(False)
        self.widgetFIT100A.setStyleSheet(u"#widgetFIT100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_8 = QLabel(self.widgetFIT100A)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(30, 2, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFIT100A = QLCDNumber(self.widgetFIT100A)
        self.lcdFIT100A.setObjectName(u"lcdFIT100A")
        self.lcdFIT100A.setGeometry(QRect(10, 25, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFIT100A.sizePolicy().hasHeightForWidth())
        self.lcdFIT100A.setSizePolicy(sizePolicy2)
        self.lcdFIT100A.setStyleSheet(u"#lcdFIT100A {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFIT100A.setSmallDecimalPoint(True)
        self.lcdFIT100A.setDigitCount(6)
        self.label_25 = QLabel(self.widgetFIT100A)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(95, 33, 41, 16))
        self.widgetTIT100 = QWidget(self.processTab1)
        self.widgetTIT100.setObjectName(u"widgetTIT100")
        self.widgetTIT100.setGeometry(QRect(0, 90, 121, 71))
        self.widgetTIT100.setMinimumSize(QSize(121, 71))
        self.widgetTIT100.setAutoFillBackground(False)
        self.widgetTIT100.setStyleSheet(u"#widgetTIT100{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_9 = QLabel(self.widgetTIT100)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(30, 10, 48, 22))
        sizePolicy1.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy1)
        self.label_9.setFont(font)
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdTIT100 = QLCDNumber(self.widgetTIT100)
        self.lcdTIT100.setObjectName(u"lcdTIT100")
        self.lcdTIT100.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdTIT100.sizePolicy().hasHeightForWidth())
        self.lcdTIT100.setSizePolicy(sizePolicy2)
        self.lcdTIT100.setStyleSheet(u"#lcdTIT100 {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdTIT100.setSmallDecimalPoint(True)
        self.lcdTIT100.setDigitCount(6)
        self.label_27 = QLabel(self.widgetTIT100)
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
        self.pbAMFV100AR.setStyleSheet(u"")
        self.pbAMFV100AR.setCheckable(True)
        self.pbAMFV100AR.setChecked(True)

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
        self.sliderFV100AR = QSlider(self.widgetSliderFV100AR)
        self.sliderFV100AR.setObjectName(u"sliderFV100AR")
        self.sliderFV100AR.setGeometry(QRect(4, 7, 201, 20))
        self.sliderFV100AR.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_7.addWidget(self.widgetSliderFV100AR)

        self.widgetFIT100V = QWidget(self.processTab1)
        self.widgetFIT100V.setObjectName(u"widgetFIT100V")
        self.widgetFIT100V.setGeometry(QRect(520, 370, 223, 128))
        self.verticalLayout_8 = QVBoxLayout(self.widgetFIT100V)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.widgetCtrlFIT100V = QWidget(self.widgetFIT100V)
        self.widgetCtrlFIT100V.setObjectName(u"widgetCtrlFIT100V")
        self.widgetCtrlFIT100V.setMinimumSize(QSize(131, 71))
        self.widgetCtrlFIT100V.setAutoFillBackground(False)
        self.widgetCtrlFIT100V.setStyleSheet(u"#widgetCtrlFIT100V{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_34 = QLabel(self.widgetCtrlFIT100V)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy1)
        self.label_34.setFont(font)
        self.label_34.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdFIT100V = QLCDNumber(self.widgetCtrlFIT100V)
        self.lcdFIT100V.setObjectName(u"lcdFIT100V")
        self.lcdFIT100V.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFIT100V.sizePolicy().hasHeightForWidth())
        self.lcdFIT100V.setSizePolicy(sizePolicy2)
        self.lcdFIT100V.setStyleSheet(u"#lcdFIT100V {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFIT100V.setSmallDecimalPoint(True)
        self.lcdFIT100V.setDigitCount(6)
        self.label_35 = QLabel(self.widgetCtrlFIT100V)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setGeometry(QRect(96, 40, 31, 16))

        self.horizontalLayout_6.addWidget(self.widgetCtrlFIT100V)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_4)


        self.horizontalLayout_6.addLayout(self.verticalLayout_12)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.widgetSliderFIT100V = QWidget(self.widgetFIT100V)
        self.widgetSliderFIT100V.setObjectName(u"widgetSliderFIT100V")
        sizePolicy1.setHeightForWidth(self.widgetSliderFIT100V.sizePolicy().hasHeightForWidth())
        self.widgetSliderFIT100V.setSizePolicy(sizePolicy1)
        self.widgetSliderFIT100V.setMinimumSize(QSize(201, 31))
        self.widgetSliderFIT100V.setStyleSheet(u"#widgetSliderFIT100V {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.sliderFIT100V = QSlider(self.widgetSliderFIT100V)
        self.sliderFIT100V.setObjectName(u"sliderFIT100V")
        self.sliderFIT100V.setGeometry(QRect(4, 7, 201, 20))
        self.sliderFIT100V.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_8.addWidget(self.widgetSliderFIT100V)

        self.groupBoxSimul = QGroupBox(self.processTab1)
        self.groupBoxSimul.setObjectName(u"groupBoxSimul")
        self.groupBoxSimul.setGeometry(QRect(760, 370, 161, 151))
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxSimul)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_10 = QLabel(self.groupBoxSimul)
        self.label_10.setObjectName(u"label_10")
        sizePolicy1.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy1)
        self.label_10.setFont(font)
        self.label_10.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.label_10.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.horizontalLayout.addWidget(self.label_10)

        self.lineEditMBPort = QLineEdit(self.groupBoxSimul)
        self.lineEditMBPort.setObjectName(u"lineEditMBPort")
        self.lineEditMBPort.setFont(font)

        self.horizontalLayout.addWidget(self.lineEditMBPort)


        self.verticalLayout_5.addLayout(self.horizontalLayout)

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
        self.pbAMFV100CA.setStyleSheet(u"")
        self.pbAMFV100CA.setCheckable(True)
        self.pbAMFV100CA.setChecked(True)

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
        self.sliderFV100CA = QSlider(self.widgetSliderFV100CA)
        self.sliderFV100CA.setObjectName(u"sliderFV100CA")
        self.sliderFV100CA.setGeometry(QRect(4, 7, 201, 20))
        self.sliderFV100CA.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_13.addWidget(self.widgetSliderFV100CA)

        self.widgetPIT100A = QWidget(self.processTab1)
        self.widgetPIT100A.setObjectName(u"widgetPIT100A")
        self.widgetPIT100A.setGeometry(QRect(250, 340, 223, 128))
        self.verticalLayout_15 = QVBoxLayout(self.widgetPIT100A)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_11)

        self.widgetCtrlPIT100A = QWidget(self.widgetPIT100A)
        self.widgetCtrlPIT100A.setObjectName(u"widgetCtrlPIT100A")
        self.widgetCtrlPIT100A.setMinimumSize(QSize(131, 71))
        self.widgetCtrlPIT100A.setAutoFillBackground(False)
        self.widgetCtrlPIT100A.setStyleSheet(u"#widgetCtrlPIT100A{\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_38 = QLabel(self.widgetCtrlPIT100A)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_38.sizePolicy().hasHeightForWidth())
        self.label_38.setSizePolicy(sizePolicy1)
        self.label_38.setFont(font)
        self.label_38.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.lcdPIT100A = QLCDNumber(self.widgetCtrlPIT100A)
        self.lcdPIT100A.setObjectName(u"lcdPIT100A")
        self.lcdPIT100A.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdPIT100A.sizePolicy().hasHeightForWidth())
        self.lcdPIT100A.setSizePolicy(sizePolicy2)
        self.lcdPIT100A.setStyleSheet(u"#lcdPIT100A {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdPIT100A.setSmallDecimalPoint(True)
        self.lcdPIT100A.setDigitCount(6)
        self.label_39 = QLabel(self.widgetCtrlPIT100A)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setGeometry(QRect(96, 40, 31, 16))

        self.horizontalLayout_13.addWidget(self.widgetCtrlPIT100A)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_8)


        self.horizontalLayout_13.addLayout(self.verticalLayout_16)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)


        self.verticalLayout_15.addLayout(self.horizontalLayout_13)

        self.widgetSliderPIT100A = QWidget(self.widgetPIT100A)
        self.widgetSliderPIT100A.setObjectName(u"widgetSliderPIT100A")
        sizePolicy1.setHeightForWidth(self.widgetSliderPIT100A.sizePolicy().hasHeightForWidth())
        self.widgetSliderPIT100A.setSizePolicy(sizePolicy1)
        self.widgetSliderPIT100A.setMinimumSize(QSize(201, 31))
        self.widgetSliderPIT100A.setStyleSheet(u"#widgetSliderPIT100A {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.sliderPIT100A = QSlider(self.widgetSliderPIT100A)
        self.sliderPIT100A.setObjectName(u"sliderPIT100A")
        self.sliderPIT100A.setGeometry(QRect(4, 7, 201, 20))
        self.sliderPIT100A.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_15.addWidget(self.widgetSliderPIT100A)

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
        self.pbAMFV100A.setStyleSheet(u"")
        self.pbAMFV100A.setCheckable(True)
        self.pbAMFV100A.setChecked(True)

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
        self.sliderFV100A = QSlider(self.widgetSliderFV100A)
        self.sliderFV100A.setObjectName(u"sliderFV100A")
        self.sliderFV100A.setGeometry(QRect(4, 7, 201, 20))
        self.sliderFV100A.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_17.addWidget(self.widgetSliderFV100A)

        self.widgetFIT100CA = QWidget(self.processTab1)
        self.widgetFIT100CA.setObjectName(u"widgetFIT100CA")
        self.widgetFIT100CA.setGeometry(QRect(300, 20, 131, 71))
        self.widgetFIT100CA.setMinimumSize(QSize(111, 71))
        self.widgetFIT100CA.setAutoFillBackground(False)
        self.widgetFIT100CA.setStyleSheet(u"#widgetFIT100CA {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_4 = QLabel(self.widgetFIT100CA)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.label_28 = QLabel(self.widgetFIT100CA)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(95, 40, 31, 20))
        self.lcdFIT100CA = QLCDNumber(self.widgetFIT100CA)
        self.lcdFIT100CA.setObjectName(u"lcdFIT100CA")
        self.lcdFIT100CA.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFIT100CA.sizePolicy().hasHeightForWidth())
        self.lcdFIT100CA.setSizePolicy(sizePolicy2)
        self.lcdFIT100CA.setStyleSheet(u"#lcdFIT100CA {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFIT100CA.setSmallDecimalPoint(True)
        self.lcdFIT100CA.setDigitCount(6)
        self.widgetFIT100AR = QWidget(self.processTab1)
        self.widgetFIT100AR.setObjectName(u"widgetFIT100AR")
        self.widgetFIT100AR.setGeometry(QRect(450, 20, 131, 71))
        self.widgetFIT100AR.setMinimumSize(QSize(111, 71))
        self.widgetFIT100AR.setAutoFillBackground(False)
        self.widgetFIT100AR.setStyleSheet(u"#widgetFIT100AR {\n"
"    background-color: #c0c0c0; /* Uma cor de fundo neutra */\n"
"    border-width: 2px;\n"
"    border-style: solid;\n"
"    border-color: #ffffff #888888 #888888 #ffffff; /* Bordas: cima, direita, baixo, esquerda */\n"
"    border-radius: 4px; /* Bordas arredondadas (opcional) */\n"
"    padding: 4px; /* Espa\u00e7amento interno (opcional) */\n"
"}")
        self.label_5 = QLabel(self.widgetFIT100AR)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(17, 10, 71, 22))
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)
        self.label_29 = QLabel(self.widgetFIT100AR)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(95, 40, 31, 16))
        self.lcdFIT100AR = QLCDNumber(self.widgetFIT100AR)
        self.lcdFIT100AR.setObjectName(u"lcdFIT100AR")
        self.lcdFIT100AR.setGeometry(QRect(10, 32, 81, 31))
        sizePolicy2.setHeightForWidth(self.lcdFIT100AR.sizePolicy().hasHeightForWidth())
        self.lcdFIT100AR.setSizePolicy(sizePolicy2)
        self.lcdFIT100AR.setStyleSheet(u"#lcdFIT100AR {\n"
"        color: red;\n"
"        background-color: black;\n"
"        border: 2px solid gray;\n"
"        border-radius: 5px;\n"
"    }")
        self.lcdFIT100AR.setSmallDecimalPoint(True)
        self.lcdFIT100AR.setDigitCount(6)
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
        self.mainTab.setTabText(self.mainTab.indexOf(self.modbusTab), QCoreApplication.translate("MainWindow", u"ModBus", None))
        self.radioButtonHex.setText(QCoreApplication.translate("MainWindow", u"Machine Value", None))
        self.radioButtonHrt.setText(QCoreApplication.translate("MainWindow", u"Human Value", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.hartTab), QCoreApplication.translate("MainWindow", u"Hart", None))
#if QT_CONFIG(tooltip)
        self.widgetLIT100.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de N\u00edvel do Tubul\u00e3o Superior", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetLIT100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"LIT100", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"%", None))
#if QT_CONFIG(tooltip)
        self.widgetPIT100V.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de Press\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetPIT100V.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"PIT100V", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"bar", None))
#if QT_CONFIG(tooltip)
        self.widgetFIT100A.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador da Vaz\u00e3o de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFIT100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"FIT100A", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"kg/s", None))
#if QT_CONFIG(tooltip)
        self.widgetTIT100.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador da Temperatura da Fornalha", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetTIT100.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"TIT100", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"\u00baC", None))
#if QT_CONFIG(tooltip)
        self.widgetFV100AR.setToolTip(QCoreApplication.translate("MainWindow", u"Abertura do damper de Ar", None))
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
        self.sliderFV100AR.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFIT100V.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de Vaz\u00e3o de Vapor", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlFIT100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlFIT100V.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"FIT100V", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"kg/s", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderFIT100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sliderFIT100V.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBoxSimul.setTitle(QCoreApplication.translate("MainWindow", u"Simula\u00e7\u00e3o", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"MB_PORT:", None))
        self.lineEditMBPort.setText(QCoreApplication.translate("MainWindow", u"502", None))
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
        self.sliderFV100CA.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetPIT100A.setToolTip(QCoreApplication.translate("MainWindow", u"Press\u00e3o da Bomba de \u00c1gua", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetCtrlPIT100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetCtrlPIT100A.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"PIT100A", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"kPa", None))
#if QT_CONFIG(tooltip)
        self.widgetSliderPIT100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sliderPIT100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFV100A.setToolTip(QCoreApplication.translate("MainWindow", u"Abertura da V\u00e1lvula de \u00c1gua", None))
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
        self.sliderFV100A.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.widgetFIT100CA.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador de Vaz\u00e3o de Combust\u00edvel", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFIT100CA.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"FIT100CA", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"kg/s", None))
#if QT_CONFIG(tooltip)
        self.widgetFIT100AR.setToolTip(QCoreApplication.translate("MainWindow", u"Indicador da Vaz\u00e3o de Ar", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.widgetFIT100AR.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"FIT100AR", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"kg/s", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.processTab1), QCoreApplication.translate("MainWindow", u"Process", None))
    # retranslateUi

