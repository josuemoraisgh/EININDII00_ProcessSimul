# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_func.ui'
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
    QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

from comp.smarttextedit import SmartTextEdit

class Ui_Dialog_Func(object):
    def setupUi(self, Dialog_Func):
        if not Dialog_Func.objectName():
            Dialog_Func.setObjectName(u"Dialog_Func")
        Dialog_Func.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog_Func.resize(555, 82)
        self.verticalLayout = QVBoxLayout(Dialog_Func)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog_Func)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit = SmartTextEdit(Dialog_Func)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(Dialog_Func)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_Func)
        self.buttonBox.rejected.connect(Dialog_Func.reject)
        self.buttonBox.accepted.connect(Dialog_Func.accept)

        QMetaObject.connectSlotsByName(Dialog_Func)
    # setupUi

    def retranslateUi(self, Dialog_Func):
        Dialog_Func.setWindowTitle(QCoreApplication.translate("Dialog_Func", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog_Func", u"Func:", None))
    # retranslateUi

