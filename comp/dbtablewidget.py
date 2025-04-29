from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QMenu, QDialog
from PySide6.QtGui import QAction, QFont
from PySide6.QtCore import Qt
from db.db_types import DBState, DBModel
from hrt.hrt_enum import hrt_enum
from hrt.hrt_bitenum import hrt_bitEnum
from hrt.hrt_type import str2type, type2str
import qtawesome as qta
from uis.ui_dialog_value import Ui_Dialog_Value
from uis.ui_dialog_func import Ui_Dialog_Func
from uis.ui_dialog_tfunc import Ui_Dialog_Tfunc
from react.react_var import ReactVar

class DBTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = DBState.humanValue

    def setAutoCompleteList(self, data: dict):
        self.autoCompleteList = data

    def setBaseData(self, dbDataFrame, tableName: str):
        self.tableName = tableName
        self.dbDataFrame = dbDataFrame
        self.df = dbDataFrame.df[tableName]

        hh_font = QFont("Arial", 12, QFont.Bold)
        vh_font = QFont("Arial", 10, QFont.Bold)
        self.horizontalHeader().setFont(hh_font)
        self.verticalHeader().setFont(vh_font)

        self.redrawAll()

    def changeType(self, isHuman: bool):
        self.state = DBState.humanValue if isHuman else DBState.machineValue
        self.redrawAll()

    def redrawAll(self):
        def get_sync_value(var: ReactVar, state: DBState):
            if state == DBState.humanValue:
                return var._value
            return var.translate(var._value, var.type(), var.byteSize(), DBState.machineValue, DBState.humanValue)

        rows, cols = self.df.shape
        rowKeys = self.df.index
        colKeys = self.df.columns
        self.blockSignals(True)
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(colKeys.tolist())
        self.setVerticalHeaderLabels(rowKeys.tolist())

        for r_idx, rowName in enumerate(rowKeys):
            for c_idx, colName in enumerate(colKeys):
                data: ReactVar = self.df.at[rowName, colName]
                raw_value = get_sync_value(data, self.state)
                display_value = (
                    type2str(raw_value, data.type())
                    if self.state == DBState.humanValue and not isinstance(raw_value, str)
                    else raw_value
                )
                typeValue = data.type()
                model = data.model

                is_enum = (
                    ("ENUM" in typeValue or "BIT_ENUM" in typeValue)
                    and model not in {DBModel.Func, DBModel.tFunc}
                    and colName not in ["BYTE_SIZE", "TYPE"]
                )
                editable_field = (
                    self.state == DBState.humanValue
                    or colName in ["BYTE_SIZE", "TYPE"]
                    or any(x in typeValue for x in ["PACKED","UNSIGNED","FLOAT","INTEGER","DATE","TIME"])
                ) and model not in {DBModel.Func, DBModel.tFunc}

                if is_enum:
                    combo = QComboBox()
                    items = []
                    if self.tableName == "HART":
                        try:
                            if typeValue.startswith('BIT_ENUM'):
                                idx = int(typeValue[len('BIT_ENUM'):])
                                items = list(hrt_bitEnum.get(idx, {}).values())
                            elif typeValue.startswith('ENUM'):
                                idx = int(typeValue[len('ENUM'):])
                                items = list(hrt_enum.get(idx, {}).values())
                        except Exception:
                            items = []
                    combo.addItems(items)
                    combo.setCurrentText(str(display_value))
                    combo.currentIndexChanged.connect(
                        lambda _, var=data, cb=combo: var.setValue(cb.currentText(), self.state)
                    )
                    data.valueChangedSignal.connect(
                        lambda var=data, cb=combo: cb.setCurrentText(
                            str(get_sync_value(var, self.state))
                        )
                    )
                    self.setCellWidget(r_idx, c_idx, combo)
                else:
                    line = QLineEdit()
                    if editable_field:
                        line.setStyleSheet("background-color: white;")
                        line.editingFinished.connect(
                            lambda var=data, ln=line: var.setValue(
                                str2type(ln.text(), var.type()), self.state
                            )
                        )
                    else:
                        line.setReadOnly(True)
                        line.setStyleSheet("background-color: #D3D3D3;")

                    data.valueChangedSignal.connect(
                        lambda var=data, ln=line: ln.setText(
                            type2str(
                                get_sync_value(var, self.state), var.type()
                            ) if self.state == DBState.humanValue and not isinstance(get_sync_value(var, self.state), str)
                            else str(get_sync_value(var, self.state))
                        )
                    )
                    line.setContextMenuPolicy(Qt.CustomContextMenu)
                    line.customContextMenuRequested.connect(
                        lambda pos, ln=line, rn=rowName, cn=colName: self.show_custom_context_menu(ln, rn, cn, pos)
                    )
                    line.setText(str(display_value))
                    self.setCellWidget(r_idx, c_idx, line)

                self.setColumnWidth(c_idx, 150)
        self.blockSignals(False)
        self.viewport().update()

    def show_custom_context_menu(self, line_edit, rowName, colName, pos):
        """Mostra o menu de contexto quando o botão direito for pressionado"""
        if not isinstance(line_edit, QLineEdit):
            return
        menu = QMenu(self)
        data: ReactVar = self.df.at[rowName, colName]

        # Value
        action_Value = QAction(qta.icon("mdi.numeric"), "Value", self)
        def actionValueSlot():
            dialog = QDialog(self)
            ui = Ui_Dialog_Value()
            ui.setupUi(dialog)
            cellVal = data._value
            if self.state == DBState.humanValue:
                cellVal = type2str(cellVal, data.type())
            ui.lineEdit.setText(str(cellVal))
            ui.buttonBox.accepted.connect(lambda: data.setValue(ui.lineEdit.text(), self.state))
            dialog.exec()
        action_Value.triggered.connect(actionValueSlot)
        menu.addAction(action_Value)

        # Func
        action_Func = QAction(qta.icon("mdi.alarm-panel"), "Func", self)
        def actionFuncSlot():
            dialog = QDialog(self)
            ui = Ui_Dialog_Func()
            ui.setupUi(dialog)
            ui.lineEdit.suggestions = self.dbDataFrame.autoCompleteList
            ui.lineEdit.adjust_height_by_lines(1)
            ui.lineEdit.setText(data.getFunc() or "")
            ui.buttonBox.accepted.connect(lambda: data.setFunc(ui.lineEdit.toPlainText()))
            dialog.exec()
        action_Func.triggered.connect(actionFuncSlot)
        menu.addAction(action_Func)

        # Tfunc
        action_Tfunc = QAction(qta.icon("mdi.math-integral"), "Tfunc", self)
        def actionTfuncSlot():
            dialog = QDialog(self)
            ui = Ui_Dialog_Tfunc()
            ui.setupUi(dialog)
            ui.lineEditInput.suggestions = self.dbDataFrame.autoCompleteList
            ui.lineEditInput.adjust_height_by_lines(1)
            tfunc = data.getTFunc() or ''
            try:
                num_str, den_str, delay_str, input_str = map(str.strip, tfunc.split(","))
            except Exception:
                num_str = den_str = delay_str = input_str = ""
            ui.lineEditNum.setText(num_str.strip('[]'))
            ui.lineEditDen.setText(den_str.strip('[]'))
            ui.lineEditDelay.setText(delay_str)
            ui.lineEditInput.setText(input_str)
            ui.buttonBox.accepted.connect(
                lambda: data.setTFunc(
                    f'[{ui.lineEditNum.text()}],[{ui.lineEditDen.text()}],'
                    f'{ui.lineEditDelay.text()},{ui.lineEditInput.toPlainText()},'
                )
            )
            dialog.exec()
        action_Tfunc.triggered.connect(actionTfuncSlot)
        menu.addAction(action_Tfunc)

        menu.addSeparator()
        standard_menu = line_edit.createStandardContextMenu()
        for action in standard_menu.actions():
            menu.addAction(action)
        menu.exec(line_edit.mapToGlobal(pos))