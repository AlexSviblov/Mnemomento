import os
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
import sqlite3

conn = sqlite3.connect('PhotoDB.db')  # соединение с БД
cur = conn.cursor()


class SocialNetworks(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создание окна
        self.setWindowTitle('Соцсети')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(800, 800)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.top_text_lbl = QLabel(self)
        self.top_text_lbl.setText('Соц.сети')
        self.layout.addWidget(self.top_text_lbl, 0, 0, 1, 1)

        self.add_btn = QPushButton(self)
        self.add_btn.setText('Добавить')
        self.layout.addWidget(self.add_btn, 1, 0, 1, 1)
        self.add_btn.clicked.connect(self.add_func)

        self.networks_group = QGroupBox(self)
        self.group_layout = QGridLayout(self)
        self.networks_group.setLayout(self.group_layout)
        self.layout.addWidget(self.networks_group, 2, 0, 1, 1)

        self.show_social_networks()

    # отобразить введённые соцсети
    def show_social_networks(self) -> None:
        for i in reversed(range(self.group_layout.count())):
            self.group_layout.itemAt(i).widget().deleteLater()
        networks = self.get_social_networks_list()
        for i in range(0, len(networks)):
            self.soc_net_lbl = QLabel(self)
            self.soc_net_lbl.setText('')
            if networks[i][0:9] != 'numnumnum':
                self.soc_net_lbl.setText(f'{networks[i]}')
            else:
                self.soc_net_lbl.setText(f'{networks[i][9:]}')

            self.group_layout.addWidget(self.soc_net_lbl, i, 0, 1, 1)

            self.btn_red = QToolButton(self)
            self.btn_red.setText('RED')
            self.btn_red.setObjectName(networks[i])
            self.btn_red.clicked.connect(self.func_red)
            self.group_layout.addWidget(self.btn_red, i, 1, 1, 1)

            self.btn_del = QToolButton(self)
            self.btn_del.setText('DEL')
            self.btn_del.setObjectName(networks[i])
            self.btn_del.clicked.connect(self.func_del)
            self.group_layout.addWidget(self.btn_del, i, 2, 1, 1)

    # считать из БД введённые соцсети
    def get_social_networks_list(self) -> list[str, ...]:
        networks = list()
        sql_str = 'PRAGMA table_info(socialnetworks)'
        cur.execute(sql_str)
        all_tableinfo = cur.fetchall()
        for i in range(3, len(all_tableinfo)):
            networks.append(all_tableinfo[i][1])

        return networks

    # добавление соцсети
    def add_func(self) -> None:
        dialog_add = AddSN()
        if dialog_add.exec():
            pass
        elif dialog_add.reject():
            return

        self.show_social_networks()

    # редактирование имени соцсети
    def func_red(self) -> None:
        net_name = self.sender().objectName()
        red_dialog = RedSN(net_oldname=net_name)
        if red_dialog.exec():
            pass
        elif red_dialog.reject():
            return
        self.show_social_networks()

    # удаление соцсети
    def func_del(self) -> None:
        net_name = self.sender().objectName()
        del_dialog = DelSN(net_name=net_name)
        if del_dialog.exec():
            pass
        elif del_dialog.reject():
            return
        self.show_social_networks()


# добавление новой соцсети
class AddSN(QDialog):
    def __init__(self):
        super(AddSN, self).__init__()
        # Создание окна
        self.setWindowTitle('Добавить соцсеть')
        self.resize(600, 90)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.text_lbl = QLabel(self)
        self.text_lbl.setText('Введите название соцсети:')
        self.layout.addWidget(self.text_lbl, 0, 0, 1, 1)

        self.enter_name = QLineEdit(self)
        self.layout.addWidget(self.enter_name, 0, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.layout.addWidget(self.btn_cnl, 1, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    def func_ok(self):
        self.check_empty()

    # проверка заполнения полей ввода
    def check_empty(self) -> None:
        if self.enter_name.text() != '':
            self.do_func()
        else:
            return

    # после подтверждения добавления
    def do_func(self) -> None:
        sql_str = f'ALTER TABLE socialnetworks ADD COLUMN {self.enter_name.text()} TEXT DEFAULT \'No value\''
        try:
            cur.execute(sql_str)
        except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
            textwithnum = 'numnumnum' + self.enter_name.text()
            sql_str = f'ALTER TABLE socialnetworks ADD COLUMN {textwithnum} TEXT DEFAULT \'No value\''
            cur.execute(sql_str)
        conn.commit()
        self.accept()


# переименование соцсети
class RedSN(QDialog):
    def __init__(self, net_oldname):
        super(RedSN, self).__init__()
        # Создание окна
        self.setWindowTitle('Редактирование названия')
        self.resize(600, 90)

        self.net_oldname = net_oldname
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.old_name_lbl = QLabel(self)
        self.old_name_lbl.setText('Старое название:')
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        self.old_name = QLineEdit(self)
        if net_oldname[0:9] != 'numnumnum':
            self.old_name.setText(net_oldname)
        else:
            self.old_name.setText(net_oldname[9:])
        self.old_name.setDisabled(True)
        self.old_name.setStyleSheet('color: black')
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.new_name_lbl = QLabel(self)
        self.new_name_lbl.setText('Старое название:')
        self.layout.addWidget(self.new_name_lbl, 1, 0, 1, 1)

        self.new_name = QLineEdit(self)
        self.layout.addWidget(self.new_name, 1, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.layout.addWidget(self.btn_cnl, 2, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    # запуск проверки check_empty
    def func_ok(self) -> None:
        self.check_empty()

    # проверка заполнения полей ввода
    def check_empty(self) -> None:
        if self.new_name.text() != '':
            self.do_func()
        else:
            return

    # после проверки на пустоту - редактировать
    def do_func(self) -> None:
        sql_str = f'ALTER TABLE socialnetworks RENAME COLUMN {self.net_oldname} TO {self.new_name.text()}'
        try:
            cur.execute(sql_str)
        except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
            textwithnum = 'numnumnum' + self.new_name.text()
            sql_str = f'ALTER TABLE socialnetworks RENAME COLUMN {self.net_oldname} TO {textwithnum}'
            cur.execute(sql_str)
        conn.commit()
        self.accept()


# удалить соцсеть
class DelSN(QDialog):
    def __init__(self, net_name):
        super(DelSN, self).__init__()
        # Создание окна
        self.setWindowTitle('Редактирование названия')
        self.resize(600, 90)

        self.net_name = net_name
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.old_name_lbl = QLabel(self)
        self.old_name_lbl.setText('Вы уверены, что хотите удалить:')
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        self.old_name = QLineEdit(self)
        if net_name[0:9] != 'numnumnum':
            self.old_name.setText(net_name)
        else:
            self.old_name.setText(net_name[9:])
        self.old_name.setDisabled(True)
        self.old_name.setStyleSheet('color: black')
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.do_func)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.layout.addWidget(self.btn_cnl, 2, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    # после подтверждения удаления
    def do_func(self) -> None:
        sql_str = f'ALTER TABLE socialnetworks DROP COLUMN {self.net_name}'
        cur.execute(sql_str)

        conn.commit()
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SocialNetworks()
    win.show()
    sys.exit(app.exec_())
