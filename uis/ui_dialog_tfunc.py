# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_tfunc.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

from comp.smarttextedit import SmartTextEdit

class Ui_Dialog_Tfunc(object):
    def setupUi(self, Dialog_Tfunc):
        if not Dialog_Tfunc.objectName():
            Dialog_Tfunc.setObjectName(u"Dialog_Tfunc")
        Dialog_Tfunc.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Tfunc.resize(649, 122)
        self.verticalLayout = QVBoxLayout(Dialog_Tfunc)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog_Tfunc)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEditNum = QLineEdit(Dialog_Tfunc)
        self.lineEditNum.setObjectName(u"lineEditNum")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditNum.sizePolicy().hasHeightForWidth())
        self.lineEditNum.setSizePolicy(sizePolicy)
        self.lineEditNum.setMinimumSize(QSize(218, 30))

        self.horizontalLayout.addWidget(self.lineEditNum)


        self.horizontalLayout_5.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(Dialog_Tfunc)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEditDen = QLineEdit(Dialog_Tfunc)
        self.lineEditDen.setObjectName(u"lineEditDen")
        sizePolicy.setHeightForWidth(self.lineEditDen.sizePolicy().hasHeightForWidth())
        self.lineEditDen.setSizePolicy(sizePolicy)
        self.lineEditDen.setMinimumSize(QSize(218, 30))

        self.horizontalLayout_2.addWidget(self.lineEditDen)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(Dialog_Tfunc)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEditInput = SmartTextEdit(Dialog_Tfunc)
        self.lineEditInput.setObjectName(u"lineEditInput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEditInput.sizePolicy().hasHeightForWidth())
        self.lineEditInput.setSizePolicy(sizePolicy1)
        self.lineEditInput.setMinimumSize(QSize(218, 30))

        self.horizontalLayout_3.addWidget(self.lineEditInput)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(Dialog_Tfunc)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.lineEditDelay = QLineEdit(Dialog_Tfunc)
        self.lineEditDelay.setObjectName(u"lineEditDelay")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEditDelay.sizePolicy().hasHeightForWidth())
        self.lineEditDelay.setSizePolicy(sizePolicy2)
        self.lineEditDelay.setMinimumSize(QSize(50, 30))

        self.horizontalLayout_4.addWidget(self.lineEditDelay)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_4)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.buttonBox = QDialogButtonBox(Dialog_Tfunc)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_Tfunc)
        self.buttonBox.accepted.connect(Dialog_Tfunc.accept)
        self.buttonBox.rejected.connect(Dialog_Tfunc.reject)

        QMetaObject.connectSlotsByName(Dialog_Tfunc)
    # setupUi

    def retranslateUi(self, Dialog_Tfunc):
        Dialog_Tfunc.setWindowTitle(QCoreApplication.translate("Dialog_Tfunc", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog_Tfunc", u"Num:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog_Tfunc", u"Den:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog_Tfunc", u"imput:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog_Tfunc", u"Atraso:", None))
    # retranslateUi

