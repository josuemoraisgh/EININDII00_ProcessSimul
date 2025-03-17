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

class Ui_Dialog_Tfunc(object):
    def setupUi(self, Dialog_Tfunc):
        if not Dialog_Tfunc.objectName():
            Dialog_Tfunc.setObjectName(u"Dialog_Tfunc")
        Dialog_Tfunc.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Tfunc.resize(268, 157)
        self.verticalLayout = QVBoxLayout(Dialog_Tfunc)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog_Tfunc)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit = QLineEdit(Dialog_Tfunc)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(Dialog_Tfunc)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_2 = QLineEdit(Dialog_Tfunc)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(Dialog_Tfunc)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEdit_3 = QLineEdit(Dialog_Tfunc)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.horizontalLayout_3.addWidget(self.lineEdit_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

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
    # retranslateUi

