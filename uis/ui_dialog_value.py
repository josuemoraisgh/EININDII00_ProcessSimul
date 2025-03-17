# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_value.ui'
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

class Ui_Dialog_Value(object):
    def setupUi(self, Dialog_Value):
        if not Dialog_Value.objectName():
            Dialog_Value.setObjectName(u"Dialog_Value")
        Dialog_Value.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Value.resize(268, 82)
        self.verticalLayout = QVBoxLayout(Dialog_Value)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog_Value)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit = QLineEdit(Dialog_Value)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(Dialog_Value)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_Value)
        self.buttonBox.accepted.connect(Dialog_Value.accept)
        self.buttonBox.rejected.connect(Dialog_Value.reject)

        QMetaObject.connectSlotsByName(Dialog_Value)
    # setupUi

    def retranslateUi(self, Dialog_Value):
        Dialog_Value.setWindowTitle(QCoreApplication.translate("Dialog_Value", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog_Value", u"Value:", None))
    # retranslateUi

