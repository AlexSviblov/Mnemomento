# coding: utf-8
import logging
import sqlite3
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from GUI import Screenconfig, Settings, ErrorsAndWarnings
from Database import ErrorNamesDB


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet4 = str()
stylesheet5 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()


font12 = QtGui.QFont("Times", 12)

system_scale = Screenconfig.monitor_info()[1]


class ViewBDDialog(QWidget):
    """
    Просмотр базы исправлений
    """
    resized_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle("База исправлений")
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.table = QTableWidget(self)
        self.add_btn = QPushButton(self)
        self.del_btn = QPushButton(self)
        self.edit_btn = QPushButton(self)
        self.edit_mode = QLabel(self)

        self.new_element = ""
        self.old_element = ""
        self.old_element_col = 0

        self.make_gui()

        self.indicator = 0

        self.my_size()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.table.setFont(font12)
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(stylesheet6)
        self.table.horizontalHeader().setDisabled(True)
        self.table.horizontalHeader().setStyleSheet(stylesheet3)
        self.table.horizontalHeader().setFont(font12)
        self.get_bd_info()
        self.layout.addWidget(self.table, 1, 0, 1, 3, alignment=Qt.AlignCenter)

        self.add_btn.setText("Добавить")
        self.add_btn.setFont(font12)
        self.add_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.add_btn, 0, 0, 1, 1)

        self.del_btn.setText("Удалить")
        self.del_btn.setFont(font12)
        self.del_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.del_btn, 0, 1, 1, 1)

        self.add_btn.clicked.connect(self.call_add)
        self.del_btn.clicked.connect(self.call_del)

        self.edit_btn.setText("Редактировать")
        self.edit_btn.setFont(font12)
        self.edit_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.edit_btn, 0, 2, 1, 1)

        self.edit_mode.setText("Режим редактирования")
        self.edit_mode.setFont(font12)
        self.layout.addWidget(self.edit_mode, 2, 0, 1, 1)
        self.edit_mode.hide()

        self.table.doubleClicked.connect(self.edit_func)
        self.table.itemChanged.connect(self.edit_element)
        self.edit_btn.clicked.connect(self.edit_indicator)

    def stylesheet_color(self) -> None:
        """
        Задать стили для всего модуля в зависимости от выбранной темы
        """
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet4
        global stylesheet5
        global stylesheet6
        global stylesheet7
        global stylesheet8
        global stylesheet9

        theme = Settings.get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f"{theme}"]["stylesheet1"]
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        stylesheet3 = style[f"{theme}"]["stylesheet3"]
        stylesheet4 = style[f"{theme}"]["stylesheet4"]
        stylesheet5 = style[f"{theme}"]["stylesheet5"]
        stylesheet6 = style[f"{theme}"]["stylesheet6"]
        stylesheet7 = style[f"{theme}"]["stylesheet7"]
        stylesheet8 = style[f"{theme}"]["stylesheet8"]
        stylesheet9 = style[f"{theme}"]["stylesheet9"]

        self.setStyleSheet(stylesheet2)

        try:
            self.table.setStyleSheet(stylesheet6)
        except AttributeError:
            pass

        try:
            self.table.horizontalHeader().setStyleSheet(stylesheet3)
        except AttributeError:
            pass

        try:
            self.add_btn.setStyleSheet(stylesheet8)
        except AttributeError:
            pass

        try:
            self.del_btn.setStyleSheet(stylesheet8)
        except AttributeError:
            pass

        try:
            self.edit_btn.setStyleSheet(stylesheet8)
        except AttributeError:
            pass

    def edit_func(self) -> None:
        """
        При двойном нажатии на ячейку, данные в ней запоминаются
        """
        self.old_element = self.table.currentItem().text()
        self.old_element_col = self.table.currentColumn()

    def edit_element(self) -> None:
        """
        Если был включен режим редактирования, происходит редактирование
        """
        if self.indicator == 1:
            # изменение в БД
            self.new_element = self.table.currentItem().text()
            match self.old_element_col:
                case 0:
                    col_name = "type"
                case 1:
                    col_name = "exifname"
                case 2:
                    col_name = "normname"
                case _:
                    return

            ErrorNamesDB.edit_error_name(col_name, self.new_element, self.old_element)
            logging.info(f"ErNamesDB - Edited value {col_name} from {self.old_element} to {self.new_element}")

            self.indicator = 0
            self.edit_btn.setDisabled(False)
            self.edit_mode.hide()
            self.get_bd_info()
            self.my_size()
        else:
            pass

    def edit_indicator(self) -> None:
        """
        Включение режима редактирования
        """
        self.indicator = 1
        self.edit_mode.setFixedHeight(self.height() - self.table.height() - self.add_btn.height())
        self.edit_mode.show()
        self.edit_btn.setDisabled(True)

    def get_bd_info(self) -> None:
        """
        Получение информации из БД
        """
        all_results = ErrorNamesDB.get_all_ernames()
        row_num = len(all_results)
        self.table.setRowCount(row_num)
        self.table.setHorizontalHeaderLabels(["Тип", "Ошибочное отображение", "Верное название"])
        for i in range(0, len(all_results)):
            if all_results[i][0] == "maker":
                type_str = "Производитель"
            elif all_results[i][0] == "lens":
                type_str = "Объектив"
            elif all_results[i][0] == "camera":
                type_str = "Камера"
            else:
                type_str = "error"
            self.table.setItem(i, 0, QTableWidgetItem(type_str))
            self.table.setItem(i, 1, QTableWidgetItem(str(all_results[i][1])))
            self.table.setItem(i, 2, QTableWidgetItem(str(all_results[i][2])))

        self.table.resizeColumnsToContents()
        self.table.setFixedWidth(self.table.columnWidth(0) + self.table.columnWidth(1) + self.table.columnWidth(2) + 2)
        height = 0
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i)
        height += self.table.horizontalHeader().height()
        self.table.setFixedHeight(height)
        self.resize(self.table.width() + 20, self.height() + 20)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.verticalScrollBar().setDisabled(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def call_add(self) -> None:
        """
        Вызов окна добавления записи
        """
        self.indicator = 0
        self.edit_mode.hide()
        dialog_add = AddBDDialog()
        if dialog_add.exec():
            pass
        self.get_bd_info()
        self.my_size()

    def call_del(self) -> None:
        """
        Вызов окна удаления записи
        """
        self.indicator = 0
        self.edit_mode.hide()
        cur_row = self.table.currentRow()  # считывание выбранной перед нажатием строки
        ername_to_del = self.table.item(cur_row, 1).text()  # неправильное имя удаляемого объекта
        normname_to_del = self.table.item(cur_row, 2).text()  # правильное имя удаляемого объекта
        # передача названий в окно удаления
        dialog_del = DelBDDialog(del_object_ername=ername_to_del, del_object_normname=normname_to_del)
        if dialog_del.exec():
            pass
        self.get_bd_info()
        self.my_size()

    def my_size(self) -> None:
        """
        """
        width = self.table.width()
        height = self.table.height() + self.add_btn.height()
        self.resize(width + 20, height + 20)
        self.resized_signal.emit()


class AddBDDialog(QDialog):
    """
    Добавить новую подмену
    """
    def __init__(self):
        super(AddBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle("Исправление неправильных названий")
        self.resize(600, 90)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.setStyleSheet(stylesheet2)

        self.layout_win = QGridLayout(self)
        self.btn_ok = QPushButton(self)
        self.btn_cancel = QPushButton(self)
        self.type_lbl = QtWidgets.QLabel()
        self.error_label = QtWidgets.QLabel()
        self.norm_label = QtWidgets.QLabel()
        self.type_combobox = QtWidgets.QComboBox()
        self.error_text = QtWidgets.QLineEdit()
        self.norm_text = QtWidgets.QLineEdit()

        self.confirm_label = QtWidgets.QLabel()
        self.entered_info = QtWidgets.QLabel()
        self.btn_ok_c = QPushButton(self)
        self.btn_cancel_c = QPushButton(self)

        self.norm_entered = str()
        self.error_entered = str()
        self.type_index = int()

        self.make_gui()

    def make_gui(self) -> None:
        self.btn_ok.setText("Ввод")
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font12)
        self.btn_ok.setFixedHeight(int(30*system_scale)+1)
        self.layout_win.addWidget(self.btn_ok, 3, 0, 1, 1)

        self.btn_cancel.setText("Отмена")
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.btn_cancel.setFont(font12)
        self.btn_cancel.setFixedHeight(int(30*system_scale)+1)
        self.layout_win.addWidget(self.btn_cancel, 3, 1, 1, 1)

        self.btn_ok.clicked.connect(self.confirm_window)
        self.btn_cancel.clicked.connect(self.reject)

        self.type_lbl.setText("Тип неправильно отображаемого названия:")
        self.type_lbl.setFont(font12)
        self.layout_win.addWidget(self.type_lbl, 0, 0, 1, 1)

        self.error_label.setText("Неправильное название:")
        self.error_label.setFont(font12)
        self.layout_win.addWidget(self.error_label, 1, 0, 1, 1)

        self.norm_label.setText("Правильное название:")
        self.norm_label.setFont(font12)
        self.layout_win.addWidget(self.norm_label, 2, 0, 1, 1)

        self.type_combobox.addItem("Производитель")
        self.type_combobox.addItem("Камера")
        self.type_combobox.addItem("Объектив")
        self.type_combobox.setFont(font12)
        self.type_combobox.setFixedHeight(int(40*system_scale)+1)
        self.type_combobox.setStyleSheet(stylesheet9)
        self.layout_win.addWidget(self.type_combobox, 0, 1, 1, 1)

        self.error_text.setFont(font12)
        self.error_text.setStyleSheet(stylesheet1)
        self.error_text.setFixedHeight(30)
        self.layout_win.addWidget(self.error_text, 1, 1, 1, 1)

        self.norm_text.setFont(font12)
        self.norm_text.setFixedHeight(30)
        self.norm_text.setStyleSheet(stylesheet1)
        self.layout_win.addWidget(self.norm_text, 2, 1, 1, 1)

    def confirm_window(self) -> None:
        """
        Подтверждение добавления записи
        """

        # Проверка заполнения полей ввода
        if self.error_text.text() == "":
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=1)
            warning.show()
            return

        if self.norm_text.text() == "":
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=2)
            warning.show()
            return

        self.norm_entered = self.norm_text.text()
        self.error_entered = self.error_text.text()
        type_entered = self.type_combobox.currentText()
        self.type_index = self.type_combobox.currentIndex()

        self.type_lbl.hide()
        self.btn_ok.hide()
        self.btn_cancel.hide()
        self.error_label.hide()
        self.norm_label.hide()
        self.type_combobox.hide()
        self.error_text.hide()
        self.norm_text.hide()

        self.confirm_label.setText("Правильно ли введены данные?\n")
        self.confirm_label.setFont(font12)
        self.layout_win.addWidget(self.confirm_label, 0, 0, 1, 2)

        self.entered_info.setFont(font12)
        self.entered_info.setText(
            f"Тип: {type_entered}\nНеверное отображение: {self.error_entered}\nПравильное отображение: {self.norm_entered}\n")
        self.layout_win.addWidget(self.entered_info, 1, 0, 1, 2)

        self.btn_ok_c.setText("Ввод")
        self.btn_ok_c.setFont(font12)
        self.btn_ok_c.setStyleSheet(stylesheet8)

        self.btn_cancel_c.setText("Отмена")
        self.btn_cancel_c.setFont(font12)
        self.btn_cancel_c.setStyleSheet(stylesheet8)

        self.layout_win.addWidget(self.btn_ok_c, 2, 0, 1, 1)
        self.layout_win.addWidget(self.btn_cancel_c, 2, 1, 1, 1)

        self.btn_ok_c.clicked.connect(self.confirm_func)
        self.btn_cancel_c.clicked.connect(self.not_confirm_func)

    def not_confirm_func(self) -> None:
        """
        После отмены добавления
        """
        self.confirm_label.hide()
        self.entered_info.hide()
        self.btn_ok_c.hide()
        self.btn_cancel_c.hide()

        self.btn_ok.show()
        self.btn_cancel.show()

        self.type_lbl.show()
        self.error_label.show()
        self.norm_label.show()
        self.type_combobox.show()
        self.error_text.show()
        self.norm_text.show()

        self.type_combobox.setCurrentIndex(self.type_index)
        self.error_text.setText(self.error_entered)
        self.norm_text.setText(self.norm_entered)

    def confirm_func(self) -> None:
        """
        После подтверждения добавления
        """
        match self.type_combobox.currentIndex():
            case 0:
                equip_type = "maker"
            case 1:
                equip_type = "camera"
            case 2:
                equip_type = "lens"
            case _:
                raise ValueError

        try:
            ErrorNamesDB.add_ername(equip_type, self.error_entered, self.norm_entered)
        except sqlite3.OperationalError :
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=3)
            warning.show()
            return

        logging.info(f"ErNamesDB - Added correction {equip_type} - {self.error_entered} - {self.norm_entered}")

        ready = SuccessWindowClass(self)
        ready.show()


class DelBDDialog(QDialog):
    """
    Удалить подмену
    """
    def __init__(self, del_object_ername: str, del_object_normname: str):
        super(DelBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle("Исправление неправильного считывания")
        self.resize(400, 100)
        self.setStyleSheet(stylesheet2)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout_win = QGridLayout()
        self.setLayout(self.layout_win)

        self.del_obj_ername = del_object_ername
        self.del_obj_normname = del_object_normname

        self.obj_lbl = QLabel()
        self.obj_lbl.setText(f"Вы точно хотите удалить {self.del_obj_ername} -> {self.del_obj_normname}?")
        self.layout_win.addWidget(self.obj_lbl, 0, 0, 1, 2)
        self.obj_lbl.setFont(font12)
        self.obj_lbl.setStyleSheet(stylesheet2)

        btn_ok = QPushButton(self)
        btn_ok.setText("Подтверждение")
        btn_ok.setFont(font12)
        btn_ok.setStyleSheet(stylesheet8)
        btn_cancel = QPushButton(self)
        btn_cancel.setText("Отмена")
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet8)

        self.layout_win.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout_win.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(self.do_del)
        btn_cancel.clicked.connect(self.reject)

    def do_del(self) -> None:
        """
        Произвести удаление записи
        """
        ErrorNamesDB.delete_ername(self.del_obj_ername)
        logging.info(f"ErNamesDB - Removed correction for {self.del_obj_ername}")
        self.accept()


class SuccessWindowClass(QDialog):
    """
    "Изменения сохранены"
    """
    def __init__(self, parent):
        super(SuccessWindowClass, self).__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.answer = None
        self.resize(100, 100)

        self.setWindowTitle("ГОТОВО")
        self.setStyleSheet(stylesheet2)

        self.layout_all = QGridLayout(self)

        self.text = QLabel(self)
        self.text.setStyleSheet(stylesheet2)
        self.text.setFont(font12)
        self.text.setText("Изменения сохранены")
        self.layout_all.addWidget(self.text, 0, 0, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setFont(font12)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setText("Ок")
        self.layout_all.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(parent.close)
        self.btn_ok.clicked.connect(self.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ViewBDDialog()
    form.show()
    app.exec_()
