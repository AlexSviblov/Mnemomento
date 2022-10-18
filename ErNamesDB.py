import logging
import sqlite3
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

import ErrorsAndWarnings
import Screenconfig
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet4 = str()
stylesheet5 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()

conn = sqlite3.connect('ErrorNames.db', check_same_thread=False)  # соединение с БД

cur = conn.cursor()

font12 = QtGui.QFont('Times', 12)

system_scale = Screenconfig.monitor_info()[1]


# просмотр базы исправлений
class ViewBDDialog(QWidget):
    resized_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle('База исправлений')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.table = QTableWidget(self)
        self.add_btn = QPushButton(self)
        self.del_btn = QPushButton(self)
        self.edit_btn = QPushButton(self)
        self.edit_mode = QLabel(self)

        self.make_gui()

        self.indicator = 0

        self.my_size()

    def make_gui(self):
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

        self.add_btn.setText('Добавить')
        self.add_btn.setFont(font12)
        self.add_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.add_btn, 0, 0, 1, 1)

        self.del_btn.setText('Удалить')
        self.del_btn.setFont(font12)
        self.del_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.del_btn, 0, 1, 1, 1)

        self.add_btn.clicked.connect(self.call_add)
        self.del_btn.clicked.connect(self.call_del)

        self.edit_btn.setText('Редактировать')
        self.edit_btn.setFont(font12)
        self.edit_btn.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.edit_btn, 0, 2, 1, 1)

        self.edit_mode.setText('Режим редактирования')
        self.edit_mode.setFont(font12)
        self.layout.addWidget(self.edit_mode, 2, 0, 1, 1)
        self.edit_mode.hide()

        self.table.doubleClicked.connect(self.edit_func)
        self.table.itemChanged.connect(self.edit_element)
        self.edit_btn.clicked.connect(self.edit_indicator)

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet4
        global stylesheet5
        global stylesheet6
        global stylesheet7
        global stylesheet8
        global stylesheet9

        if Settings.get_theme_color() == 'light':
            stylesheet1 =   """
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            """
            stylesheet2 =   """
                                border: 0px;
                                color: #000000;
                                background-color: #F0F0F0
                            """
            stylesheet3 =   """
                                QHeaderView::section
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    background-color: #F0F0F0;
                                    color: #000000;
                                }
                            """
            stylesheet4 =   """
                                QMenuBar
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0
                                }
                                QMenuBar::item::selected
                                {
                                    color: #000000;
                                    background-color: #C0C0C0
                                }
                            """
            stylesheet5 =   """
                                QProgressBar
                                {
                                    border: 1px;
                                    border-color: #000000;
                                    border-style: solid;
                                    background-color: #FFFFFF;
                                    color: #000000
                                }
                                QProgressBar::chunk
                                {
                                    background-color: #00FF7F;
                                }
                            """
            stylesheet6 =   """
                                QTableView
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0;
                                    gridline-color: #A9A9A9;
                                }
                            """
            stylesheet7 =   """
                            QTabWidget::pane
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                background-color: #F0F0F0;
                                color: #000000;
                            }
                            QTabBar::tab
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                padding: 5px;
                                color: #000000;
                                min-width: 12em;
                            }
                            QTabBar::tab:selected
                            {
                                border: 2px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                margin-top: -1px;
                                background-color: #C0C0C0;
                                color: #000000;
                            }
                            """
            stylesheet8 =   """
                                QPushButton
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0
                                }
                                QPushButton::pressed
                                {
                                    border: 2px;
                                    background-color: #C0C0C0;
                                    margin-top: -1px
                                }
                            """
            stylesheet9 =   """
                                QComboBox
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0;
                                }
                                QComboBox QAbstractItemView
                                {
                                    selection-background-color: #C0C0C0;
                                }
                            """
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 =   """
                                border: 1px;
                                border-color: #696969;
                                border-style: solid;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            """
            stylesheet2 =   """
                                border: 0px;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            """
            stylesheet3 =   """
                                QHeaderView::section
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    background-color: #1C1C1C;
                                    color: #D3D3D3;
                                }
                            """
            stylesheet4 =   """
                                QMenuBar
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1C1C1C
                                }
                                QMenuBar::item::selected
                                {
                                    color: #D3D3D3;
                                    background-color: #3F3F3F
                                }
                            """
            stylesheet5 =   """
                                QProgressBar
                                {
                                    border: 1px;
                                    border-color: #000000;
                                    border-style: solid;
                                    background-color: #CCCCCC;
                                    color: #000000
                                } 
                                QProgressBar::chunk 
                                {
                                    background-color: #1F7515;
                                }
                            """
            stylesheet6 =   """
                                QTableView
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1c1c1c;
                                    gridline-color: #696969;
                                }
                            """
            stylesheet7 =   """
                                QTabWidget::pane
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1C1C1C;
                                    color: #D3D3D3
                                }
                                QTabBar::tab
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    padding: 5px;
                                    color: #D3D3D3;
                                    min-width: 12em;
                                } 
                                QTabBar::tab:selected
                                {
                                    border: 2px;
                                    border-color: #6A6A6A;
                                    border-style: solid;
                                    margin-top: -1px;
                                    background-color: #1F1F1F;
                                    color: #D3D3D3
                                }
                            """
            stylesheet8 =   """
                                QPushButton
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1C1C1C
                                }
                                QPushButton::pressed
                                {
                                    border: 2px;
                                    background-color: #2F2F2F;
                                    margin-top: -1px
                                }
                            """
            stylesheet9 =   """
                                QComboBox
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    background-color: #1C1C1C;
                                    color: #D3D3D3;
                                }
                                QComboBox QAbstractItemView
                                {
                                    selection-background-color: #4F4F4F;
                                }
                            """

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

    # при двойном нажатии на ячейку, данные в ней запоминаются
    def edit_func(self) -> None:
        self.old_element = self.table.currentItem().text()
        self.old_element_col = self.table.currentColumn()

    # если был включен режим редактирования, происходит редактирование
    def edit_element(self) -> None:
        if self.indicator == 1:
            # изменение в БД
            self.new_element = self.table.currentItem().text()
            match self.new_element:
                case 0:
                    col_name = 'type'
                case 1:
                    col_name = 'exifname'
                case 2:
                    col_name = 'normname'

            sql_red_str = f"UPDATE ernames SET {col_name} = '{self.new_element}' WHERE {col_name} = '{self.old_element}'"
            cur.execute(sql_red_str)
            conn.commit()

            logging.info(f"ErNamesDB - Отредактировано значение {col_name} с {self.old_element} на {self.new_element}")

            self.indicator = 0
            self.edit_btn.setDisabled(False)
            self.edit_mode.hide()
            self.get_bd_info()
            self.my_size()
        else:
            pass

    # включение режима редактирования
    def edit_indicator(self) -> None:
        self.indicator = 1
        self.edit_mode.setFixedHeight(self.height() - self.table.height() - self.add_btn.height())
        self.edit_mode.show()
        self.edit_btn.setDisabled(True)

    # получение информации из БД
    def get_bd_info(self) -> None:
        cur.execute("SELECT * FROM ernames")
        all_results = cur.fetchall()
        self.row_num = len(all_results)
        self.table.setRowCount(self.row_num)
        self.table.setHorizontalHeaderLabels(['Тип', 'Ошибочное отображение', 'Верное название'])
        for i in range(0, len(all_results)):
            if all_results[i][0] == 'maker':
                type_str = 'Производитель'
            elif all_results[i][0] == 'lens':
                type_str = 'Объектив'
            elif all_results[i][0] == 'camera':
                type_str = 'Камера'
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

    # вызов окна добавления записи
    def call_add(self) -> None:
        self.indicator = 0
        self.edit_mode.hide()
        dialog_add = AddBDDialog()
        if dialog_add.exec():
            pass
        self.get_bd_info()
        self.my_size()

    # вызов окна удаления записи
    def call_del(self) -> None:
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
        width = self.table.width()
        height = self.table.height() + self.add_btn.height()
        self.resize(width + 20, height + 20)
        self.resized_signal.emit()


# добавить новую подмены
class AddBDDialog(QDialog):
    def __init__(self):
        super(AddBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle('Исправление неправильных названий')
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

        self.make_gui()

    def make_gui(self):
        self.btn_ok.setText('Ввод')
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font12)
        self.btn_ok.setFixedHeight(int(30*system_scale)+1)
        self.layout_win.addWidget(self.btn_ok, 3, 0, 1, 1)

        self.btn_cancel.setText('Отмена')
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.btn_cancel.setFont(font12)
        self.btn_cancel.setFixedHeight(int(30*system_scale)+1)
        self.layout_win.addWidget(self.btn_cancel, 3, 1, 1, 1)

        self.btn_ok.clicked.connect(self.check_empty)
        self.btn_cancel.clicked.connect(self.reject)

        self.type_lbl.setText('Тип неправильно отображаемого названия:')
        self.type_lbl.setFont(font12)
        self.layout_win.addWidget(self.type_lbl, 0, 0, 1, 1)

        self.error_label.setText('Неправильное название:')
        self.error_label.setFont(font12)
        self.layout_win.addWidget(self.error_label, 1, 0, 1, 1)

        self.norm_label.setText('Правильное название:')
        self.norm_label.setFont(font12)
        self.layout_win.addWidget(self.norm_label, 2, 0, 1, 1)

        self.type_combobox.addItem('Производитель')
        self.type_combobox.addItem('Камера')
        self.type_combobox.addItem('Объектив')
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

    # проверка заполнения полей ввода
    def check_empty(self) -> None:
        if self.error_text.text() == '':
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=1)
            warning.show()
            return
        else:
            pass

        if self.norm_text.text() == '':
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=2)
            warning.show()
            return
        else:
            pass
        self.confirm_window()

    # подтверждение добавления записи
    def confirm_window(self) -> None:
        self.norm_entered = self.norm_text.text()
        self.error_entered = self.error_text.text()
        self.type_entered = self.type_combobox.currentText()
        self.type_index = self.type_combobox.currentIndex()

        self.type_lbl.hide()
        self.btn_ok.hide()
        self.btn_cancel.hide()
        self.error_label.hide()
        self.norm_label.hide()
        self.type_combobox.hide()
        self.error_text.hide()
        self.norm_text.hide()

        self.confirm_label = QtWidgets.QLabel()
        self.confirm_label.setText('Правильно ли введены данные?\n')
        self.confirm_label.setFont(font12)
        self.layout_win.addWidget(self.confirm_label, 0, 0, 1, 2)

        self.entered_info = QtWidgets.QLabel()
        self.entered_info.setFont(font12)
        self.entered_info.setText(
            f'Тип: {self.type_entered}\nНеверное отображение: {self.error_entered}\nПравильное отображение: {self.norm_entered}\n')
        self.layout_win.addWidget(self.entered_info, 1, 0, 1, 2)

        self.btn_ok_c = QPushButton(self)
        self.btn_ok_c.setText('Ввод')
        self.btn_ok_c.setFont(font12)
        self.btn_ok_c.setStyleSheet(stylesheet8)
        self.btn_cancel_c = QPushButton(self)
        self.btn_cancel_c.setText('Отмена')
        self.btn_cancel_c.setFont(font12)
        self.btn_cancel_c.setStyleSheet(stylesheet8)

        self.layout_win.addWidget(self.btn_ok_c, 2, 0, 1, 1)
        self.layout_win.addWidget(self.btn_cancel_c, 2, 1, 1, 1)

        self.btn_ok_c.clicked.connect(self.confirm_func)
        self.btn_cancel_c.clicked.connect(self.not_confirm_func)

    # после отмены добавления
    def not_confirm_func(self) -> None:
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

    # после подтверждения добавления
    def confirm_func(self) -> None:
        match self.type_combobox.currentIndex():
            case 0:
                type = 'maker'
            case 1:
                type = 'camera'
            case 2:
                type = 'lens'

        enter_1 = "INSERT INTO ernames(type,exifname,normname) VALUES(?,?,?)"
        enter_2 = (type, self.error_entered, self.norm_entered)

        try:
            cur.execute(enter_1, enter_2)
        except Exception:
            warning = ErrorsAndWarnings.ErNamesDBWarn(self, code=3)
            warning.show()
            return

        conn.commit()

        logging.info(f"ErNamesDB - Добавлено исправление {type} - {self.error_entered} - {self.norm_entered}")

        ready = SuccessWindowClass(self)
        ready.show()


# удалить подмену
class DelBDDialog(QDialog):
    def __init__(self, del_object_ername, del_object_normname):
        super(DelBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle('Исправление неправильного считывания')
        self.resize(400, 100)
        self.setStyleSheet(stylesheet2)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout_win = QGridLayout()
        self.setLayout(self.layout_win)

        self.del_obj_ername = del_object_ername
        self.del_obj_normname = del_object_normname

        self.obj_lbl = QLabel()
        self.obj_lbl.setText(f'Вы точно хотите удалить {self.del_obj_ername} -> {self.del_obj_normname}?')
        self.layout_win.addWidget(self.obj_lbl, 0, 0, 1, 2)
        self.obj_lbl.setFont(font12)
        self.obj_lbl.setStyleSheet(stylesheet2)

        btn_ok = QPushButton(self)
        btn_ok.setText('Подтверждение')
        btn_ok.setFont(font12)
        btn_ok.setStyleSheet(stylesheet8)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('Отмена')
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet8)

        self.layout_win.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout_win.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(self.do_del)
        btn_cancel.clicked.connect(self.reject)

    # произвести удаление записи
    def do_del(self) -> None:
        sql_del_str = f"DELETE FROM ernames WHERE exifname LIKE '{self.del_obj_ername}'"
        cur.execute(sql_del_str)
        conn.commit()

        logging.info(f"ErNamesDB - Удалена запись исправления для {self.del_obj_ername}")
        self.accept()


# "Изменения сохранены"
class SuccessWindowClass(QDialog):
    def __init__(self, parent):
        super(SuccessWindowClass, self).__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.answer = None
        self.resize(100, 100)

        self.setWindowTitle('ГОТОВО')
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
