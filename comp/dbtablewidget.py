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
                display_value = (type2str(raw_value, data.type())
                                 if (self.state == DBState.humanValue and not isinstance(raw_value, str))
                                 else raw_value)
                typeValue = data.type()
                model = data.model

                is_enum = any(x in typeValue for x in ["ENUM", "BIT_ENUM"]
                              ) and model not in {DBModel.Func, DBModel.tFunc}
                editable_field = (self.state == DBState.humanValue or colName in ["BYTE_SIZE", "TYPE"]
                                  or any(x in typeValue for x in ["PACKED","UNSIGNED","FLOAT","INTEGER","DATE","TIME"]))

                if is_enum and colName not in ["BYTE_SIZE", "TYPE"]:
                    combo = QComboBox()
                    items = []
                    if self.tableName == "HART":
                        # Tenta extrair índice de enum
                        idx = None
                        try:
                            if typeValue.startswith('BIT_ENUM'):
                                idx = int(typeValue[len('BIT_ENUM'):])
                                items = list(hrt_bitEnum.get(idx, {}).values())
                            elif typeValue.startswith('ENUM'):
                                idx = int(typeValue[len('ENUM'):])
                                items = list(hrt_enum.get(idx, {}).values())
                        except (ValueError, IndexError, KeyError):
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
                    if editable_field and model not in {DBModel.Func, DBModel.tFunc}:
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
                            (type2str(
                                get_sync_value(var, self.state),
                                var.type()
                            ) if (self.state == DBState.humanValue and not isinstance(get_sync_value(var, self.state), str))
                            else get_sync_value(var, self.state))
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
        menu = QMenu(self)
        data: ReactVar = self.df.at[rowName, colName]

        action_val = QAction(qta.icon("mdi.numeric"), "Value", self)
        action_val.triggered.connect(lambda: self._open_value_dialog(data))
        menu.addAction(action_val)

        action_fun = QAction(qta.icon("mdi.alarm-panel"), "Func", self)
        action_fun.triggered.connect(lambda: self._open_func_dialog(data))
        menu.addAction(action_fun)

        action_tfu = QAction(qta.icon("mdi.math-integral"), "Tfunc", self)
        action_tfu.triggered.connect(lambda: self._open_tfunc_dialog(data))
        menu.addAction(action_tfu)

        menu.addSeparator()
        for act in line_edit.createStandardContextMenu().actions():
            menu.addAction(act)
        menu.exec(line_edit.mapToGlobal(pos))

    def _open_value_dialog(self, data: ReactVar):
        dlg = QDialog(self)
        ui = Ui_Dialog_Value()
        ui.setupUi(dlg)
        ui.lineEdit.setText(str(data._value))
        ui.buttonBox.accepted.connect(lambda: data.setValue(ui.lineEdit.text(), self.state))
        dlg.exec()

    def _open_func_dialog(self, data: ReactVar):
        dlg = QDialog(self)
        ui = Ui_Dialog_Func()
        ui.setupUi(dlg)
        ui.lineEdit.suggestions = self.dbDataFrame.autoCompleteList
        ui.lineEdit.adjust_height_by_lines(1)
        ui.lineEdit.setText(data.getFunc() or "")
        ui.buttonBox.accepted.connect(lambda: data.setFunc(ui.lineEdit.toPlainText()))
        dlg.exec()

    def _open_tfunc_dialog(self, data: ReactVar):
        dlg = QDialog(self)
        ui = Ui_Dialog_Tfunc()
        ui.setupUi(dlg)
        ui.lineEditInput.suggestions = self.dbDataFrame.autoCompleteList
        ui.lineEditInput.adjust_height_by_lines(1)
        tfunc = data.getTFunc() or ''
        try:
            num, den, delay, inp = map(str.strip, tfunc.split(','))
        except ValueError:
            num = den = delay = inp = ''
        ui.lineEditNum.setText(num.strip('[]'))
        ui.lineEditDen.setText(den.strip('[]'))
        ui.lineEditDelay.setText(delay)
        ui.lineEditInput.setText(inp)
        ui.buttonBox.accepted.connect(lambda: data.setTFunc(
            f'[{ui.lineEditNum.text()}],[{ui.lineEditDen.text()}],' \
            f'{ui.lineEditDelay.text()},{ui.lineEditInput.toPlainText()},'
        ))
        dlg.exec()