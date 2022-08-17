import sqlite3
import sys
import ErrorsAndWarnings

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *

conn = sqlite3.connect('ErrorNames.db')  # соединение с БД
cur = conn.cursor()


# просмотр базы исправлений
class ViewBDDialog(QWidget):
    resized_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Создание окна
        self.setWindowTitle('База исправлений')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setFont(QtGui.QFont('Times', 12))
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.get_bd_info()
        self.layout.addWidget(self.table, 1, 0, 1, 3, alignment=Qt.AlignCenter)

        self.add_btn = QPushButton(self)
        self.add_btn.setText('Добавить')
        self.add_btn.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.add_btn, 0, 0, 1, 1)

        self.del_btn = QPushButton(self)
        self.del_btn.setText('Удалить')
        self.del_btn.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.del_btn, 0, 1, 1, 1)

        self.add_btn.clicked.connect(self.call_add)
        self.del_btn.clicked.connect(self.call_del)

        self.chng_btn = QPushButton(self)
        self.chng_btn.setText('Редактировать')
        self.chng_btn.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.chng_btn, 0, 2, 1, 1)

        self.edit_mode = QLabel(self)
        self.edit_mode.setText('Режим редактирования')
        self.edit_mode.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.edit_mode, 2, 0, 1, 1)
        self.edit_mode.hide()

        self.indicator = 0

        self.table.doubleClicked.connect(self.change_func)
        self.table.itemChanged.connect(self.edit_element)
        self.chng_btn.clicked.connect(self.edit_indicator)

        self.my_size()

        # self.table.setDisabled(True)

    # при двойном нажатии на ячейку, данные в ней запоминаются
    def change_func(self) -> None:
        self.old_element = self.table.currentItem().text()
        self.old_element_col = self.table.currentColumn()

    # если был включен режим редактирования, происходит редактирование
    def edit_element(self) -> None:
        if self.indicator == 1:
            # изменение в БД
            self.new_element = self.table.currentItem().text()
            if self.old_element_col == 0:
                col_name = 'type'
            elif self.old_element_col == 1:
                col_name = 'exifname'
            elif self.old_element_col == 2:
                col_name = 'normname'

            sql_red_str = f"UPDATE ernames SET {col_name} = '{self.new_element}' WHERE {col_name} = '{self.old_element}'"
            cur.execute(sql_red_str)
            conn.commit()

            self.indicator = 0
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


    # получение информации из БД
    def get_bd_info(self) -> None:
        cur.execute("SELECT * FROM ernames")
        all_results = cur.fetchall()
        self.row_num = len(all_results)
        self.table.setRowCount(self.row_num)
        self.table.setHorizontalHeaderLabels(['Тип', 'Ошибочное отображение', 'Верное название'])
        # self.table.horizontalHeaderItem(0).setToolTip('Тип')
        # self.table.horizontalHeaderItem(1).setToolTip('Неверное написание')
        # self.table.horizontalHeaderItem(2).setToolTip('Исправленное описание')
        for i in range(0, len(all_results)):
            self.table.setItem(i, 0, QTableWidgetItem(str(all_results[i][0])))
            self.table.setItem(i, 1, QTableWidgetItem(str(all_results[i][1])))
            self.table.setItem(i, 2, QTableWidgetItem(str(all_results[i][2])))

        self.table.resizeColumnsToContents()
        self.table.setFixedWidth(self.table.columnWidth(0) + self.table.columnWidth(1) + self.table.columnWidth(2))
        height = 0
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i)
        height += self.table.horizontalHeader().height()
        self.table.setFixedHeight(height)
        self.resize(self.table.width(), self.height())
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.verticalScrollBar().setDisabled(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # вызов окна добавления записи
    def call_add(self) -> None:
        dialog_add = AddBDDialog()
        if dialog_add.exec():
            pass
        elif dialog_add.reject():
            return
        self.get_bd_info()
        self.my_size()

    # вызов окна удаления записи
    def call_del(self) -> None:
        cur_row = self.table.currentRow()  # считывание выбранной перед нажатием строки
        ername_to_del = self.table.item(cur_row, 1).text()  # неправильное имя удаляемого объекта
        normname_to_del = self.table.item(cur_row, 2).text()  # правильное имя удаляемого объекта
        # передача названий в окно удаления
        dialog_del = DelBDDialog(del_object_ername=ername_to_del, del_object_normname=normname_to_del)
        if dialog_del.exec():
            pass
        elif dialog_del.reject():
            return
        self.get_bd_info()
        self.my_size()

    def my_size(self) -> None:
        width = self.table.width()
        height = self.table.height() + self.add_btn.height()
        self.resize(width, height)
        self.resized_signal.emit()


# добавить новую подмены
class AddBDDialog(QDialog):
    def __init__(self):
        super(AddBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle('Исправление неправильного считывания')
        self.resize(600, 90)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.buttonBox1 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox1.button(QDialogButtonBox.Ok).setText('Ввод')
        self.buttonBox1.button(QDialogButtonBox.Cancel).setText('Отмена')
        self.buttonBox1.setFont(QtGui.QFont('Times', 12))
        self.buttonBox1.setFixedHeight(30)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.buttonBox1, 3, 1, 1, 1)

        self.buttonBox1.accepted.connect(self.check_empty)
        self.buttonBox1.rejected.connect(self.reject)

        self.type_lbl = QtWidgets.QLabel()
        self.type_lbl.setText('Тип неправильно отображаемого названия:')
        self.type_lbl.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.type_lbl, 0, 0, 1, 1)

        self.error_label = QtWidgets.QLabel()
        self.error_label.setText('Неправильное название:')
        self.error_label.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.error_label, 1, 0, 1, 1)

        self.norm_label = QtWidgets.QLabel()
        self.norm_label.setText('Правильное название:')
        self.norm_label.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.norm_label, 2, 0, 1, 1)

        self.type_combobox = QtWidgets.QComboBox()
        self.type_combobox.addItem('Производитель')
        self.type_combobox.addItem('Камера')
        self.type_combobox.addItem('Объектив')
        self.type_combobox.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.type_combobox, 0, 1, 1, 1)

        self.error_text = QtWidgets.QLineEdit()
        self.error_text.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.error_text, 1, 1, 1, 1)

        self.norm_text = QtWidgets.QLineEdit()
        self.norm_text.setFont(QtGui.QFont('Times', 12))
        self.layout.addWidget(self.norm_text, 2, 1, 1, 1)

    # проверка заполнения полей ввода
    def check_empty(self) -> None:
        if self.error_text.text() == '':
            warning = ErrorsAndWarnings.ErNamesDBWarn(code=1)
            warning.show()
            if warning.exec_():
                return
        else:
            pass

        if self.norm_text.text() == '':
            warning = ErrorsAndWarnings.ErNamesDBWarn(code=2)
            warning.show()
            if warning.exec_():
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
        self.buttonBox1.hide()
        self.error_label.hide()
        self.norm_label.hide()
        self.type_combobox.hide()
        self.error_text.hide()
        self.norm_text.hide()

        self.confirm_label = QtWidgets.QLabel()
        self.confirm_label.setText('Правильно ли введены данные?\n')
        self.layout.addWidget(self.confirm_label, 0, 0, 1, 1)

        self.entered_info = QtWidgets.QLabel()
        self.entered_info.setText(
            f'Тип: {self.type_entered}\nНеверное отображение: {self.error_entered}\nПравильное отображение: {self.norm_entered}\n')
        self.layout.addWidget(self.entered_info, 1, 0, 1, 1)

        self.buttonBox2 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox2.button(QDialogButtonBox.Ok).setText('Ввод')
        self.buttonBox2.button(QDialogButtonBox.Cancel).setText('Отмена')
        self.layout.addWidget(self.buttonBox2, 2, 0, 1, 1)

        self.buttonBox2.accepted.connect(self.confirm_func)
        self.buttonBox2.rejected.connect(self.not_confirm_func)

    # после отмены добавления
    def not_confirm_func(self) -> None:
        self.confirm_label.hide()
        self.entered_info.hide()
        self.buttonBox2.hide()

        self.buttonBox1.show()

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
        if self.type_combobox.currentIndex() == 0:
            type = 'maker'
        elif self.type_combobox.currentIndex() == 1:
            type = 'camera'
        elif self.type_combobox.currentIndex() == 2:
            type = 'lens'

        enter_1 = "INSERT INTO ernames(type,exifname,normname) VALUES(?,?,?)"
        enter_2 = (type, self.error_entered, self.norm_entered)

        try:
            cur.execute(enter_1, enter_2)
        except:
            warning = ErrorsAndWarnings.ErNamesDBWarn(code=3)
            warning.show()
            if warning.exec_():
                return

        conn.commit()

        ready = SuccessWindowClass(code=1000)
        ready.show()
        if ready.exec_():
            self.close()


# удалить подмену
class DelBDDialog(QDialog):
    def __init__(self, del_object_ername, del_object_normname):
        super(DelBDDialog, self).__init__()
        # Создание окна
        self.setWindowTitle('Исправление неправильного считывания')
        self.resize(400, 100)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.del_obj_ername = del_object_ername
        self.del_obj_normname = del_object_normname

        self.obj_lbl = QLabel()
        self.obj_lbl.setText(f'Вы точно хотите удалить {self.del_obj_ername} -> {self.del_obj_normname}?')
        self.layout.addWidget(self.obj_lbl, 0, 0, 1, 1)
        self.obj_lbl.setFont(QtGui.QFont('Times', 12))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttonBox.button(QDialogButtonBox.Ok).setText('Подтверждение')
        buttonBox.button(QDialogButtonBox.Cancel).setText('Отмена')
        buttonBox.setFont(QtGui.QFont('Times', 12))

        self.layout.addWidget(buttonBox, 1, 0, 1, 1)

        buttonBox.accepted.connect(self.do_del)
        buttonBox.rejected.connect(self.reject)

    # произвести удаление записи
    def do_del(self) -> None:
        sql_del_str = f"DELETE FROM ernames WHERE exifname LIKE '{self.del_obj_ername}'"
        cur.execute(sql_del_str)
        conn.commit()
        self.accept()


class SuccessWindowClass(QMessageBox):
    def __init__(self, code=0):
        super(SuccessWindowClass, self).__init__()

        self.answer = None
        self.resize(100, 100)

        self.setWindowTitle('ГОТОВО')
        self.setText("Изменения сохранены")

        self.setDefaultButton(QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ViewBDDialog()
    form.show()
    app.exec_()
