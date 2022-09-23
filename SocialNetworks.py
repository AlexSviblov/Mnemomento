import os
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sqlite3

import PhotoDataDB
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()
icon_edit = str()
icon_delete = str()


conn = sqlite3.connect('PhotoDB.db')  # соединение с БД
cur = conn.cursor()

font14 = QtGui.QFont('Times', 14)


class SocialNetworks(QWidget):
    resize_signal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        self.setStyleSheet(stylesheet2)

        # Создание окна
        self.setWindowTitle('Соцсети')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(200, 200)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.add_btn = QPushButton(self)
        self.add_btn.setText('Добавить')
        self.layout.addWidget(self.add_btn, 0, 0, 1, 1)
        self.add_btn.clicked.connect(self.add_func)
        self.add_btn.setFont(font14)
        self.add_btn.setFixedWidth(100)
        self.add_btn.setStyleSheet(stylesheet8)

        self.empty1 = QLabel(self)
        self.layout.addWidget(self.empty1, 0, 1, 1, 1)
        self.empty1.setStyleSheet(stylesheet2)

        self.networks_group = QGroupBox(self)
        self.networks_group.setStyleSheet(stylesheet2)
        self.group_layout = QGridLayout(self)
        self.group_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.group_layout.setSpacing(10)
        self.networks_group.setLayout(self.group_layout)
        self.layout.addWidget(self.networks_group, 1, 0, 1, 2)

        self.show_social_networks()

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global icon_edit
        global icon_delete

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
            icon_edit = os.getcwd() + '/icons/edit_light.png'
            icon_delete = os.getcwd() + '/icons/delete_light.png'
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
            icon_edit = os.getcwd() + '/icons/edit_dark.png'
            icon_delete = os.getcwd() + '/icons/delete_dark.png'

        try:
            self.setStyleSheet(stylesheet2)
            self.add_btn.setStyleSheet(stylesheet8)
            self.empty1.setStyleSheet(stylesheet2)
            self.networks_group.setStyleSheet(stylesheet2)
            self.show_social_networks()
        except AttributeError:
            pass

    # отобразить введённые соцсети
    def show_social_networks(self) -> None:
        for i in reversed(range(self.group_layout.count())):
            self.group_layout.itemAt(i).widget().deleteLater()

        networks = PhotoDataDB.get_socialnetworks()
        max_sn_name = 0
        for i in range(0, len(networks)):
            self.soc_net_lbl = QLabel(self)
            self.soc_net_lbl.setFont(font14)
            if networks[i][0:9] != 'numnumnum':
                self.soc_net_lbl.setText(f'{networks[i]}')
            else:
                self.soc_net_lbl.setText(f'{networks[i][9:]}')

            if len(self.soc_net_lbl.text()) > max_sn_name:
                max_sn_name = len(self.soc_net_lbl.text())

            self.group_layout.addWidget(self.soc_net_lbl, i, 0, 1, 1)

            self.btn_red = QToolButton(self)
            self.btn_red.setStyleSheet(stylesheet1)
            self.btn_red.setFixedSize(50, 50)
            self.btn_red.setIcon(QtGui.QIcon(icon_edit))
            self.btn_red.setToolTip('Редактировать название')
            self.btn_red.setObjectName(networks[i])
            self.btn_red.clicked.connect(self.func_red)
            self.group_layout.addWidget(self.btn_red, i, 1, 1, 1)

            self.btn_del = QToolButton(self)
            self.btn_del.setStyleSheet(stylesheet1)
            self.btn_del.setFixedSize(50, 50)
            self.btn_del.setIcon(QtGui.QIcon(icon_delete))
            self.btn_del.setToolTip('Удалить соцсеть')
            self.btn_del.setObjectName(networks[i])
            self.btn_del.clicked.connect(self.func_del)
            self.group_layout.addWidget(self.btn_del, i, 2, 1, 1)

        try:
            self.soc_net_lbl.setFixedWidth(max_sn_name*15)
            self.networks_group.setFixedWidth(self.soc_net_lbl.width()+self.btn_del.width()+self.btn_red.width()+self.group_layout.spacing()*4 + 10)
            self.networks_group.setFixedHeight(self.add_btn.height() + len(networks) * 60)
        except AttributeError:
            pass
        self.resize(self.networks_group.width(), self.add_btn.height() + self.networks_group.height() + 10)
        self.resize_signal.emit(self.networks_group.width(), self.add_btn.height() + self.networks_group.height() + 10)

    # считать из БД введённые соцсети
    def get_social_networks_list(self) -> list[str]:
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

        self.show_social_networks()

    # редактирование имени соцсети
    def func_red(self) -> None:
        net_name = self.sender().objectName()
        red_dialog = RedSN(net_oldname=net_name)
        if red_dialog.exec():
            pass

        self.show_social_networks()

    # удаление соцсети
    def func_del(self) -> None:
        net_name = self.sender().objectName()
        del_dialog = DelSN(net_name=net_name)
        if del_dialog.exec():
            pass

        self.show_social_networks()


# добавление новой соцсети
class AddSN(QDialog):
    def __init__(self):
        super(AddSN, self).__init__()
        # Создание окна
        self.setWindowTitle('Добавить соцсеть')
        self.resize(600, 90)
        self.setStyleSheet(stylesheet2)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.text_lbl = QLabel(self)
        self.text_lbl.setText('Введите название соцсети:')
        self.text_lbl.setFont(font14)
        self.text_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.text_lbl, 0, 0, 1, 1)

        self.enter_name = QLineEdit(self)
        self.enter_name.setFont(font14)
        self.enter_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.enter_name, 0, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
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

        self.setWindowTitle('Редактирование названия')
        self.resize(600, 90)
        self.setStyleSheet(stylesheet2)

        self.net_oldname = net_oldname
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.old_name_lbl = QLabel(self)
        self.old_name_lbl.setText('Старое название:')
        self.old_name_lbl.setFont(font14)
        self.old_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        self.old_name = QLineEdit(self)
        if net_oldname[0:9] != 'numnumnum':
            self.old_name.setText(net_oldname)
        else:
            self.old_name.setText(net_oldname[9:])
        self.old_name.setDisabled(True)
        self.old_name.setFont(font14)
        self.old_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.new_name_lbl = QLabel(self)
        self.new_name_lbl.setText('Новое название:')
        self.new_name_lbl.setFont(font14)
        self.new_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.new_name_lbl, 1, 0, 1, 1)

        self.new_name = QLineEdit(self)
        self.new_name.setFont(font14)
        self.new_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.new_name, 1, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
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
        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Редактирование названия')
        self.resize(600, 80)

        self.net_name = net_name
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.old_name_lbl = QLabel(self)
        self.old_name_lbl.setText('Вы уверены, что хотите удалить:')
        self.old_name_lbl.setFont(font14)
        self.old_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        self.old_name = QLineEdit(self)
        if net_name[0:9] != 'numnumnum':
            self.old_name.setText(net_name)
        else:
            self.old_name.setText(net_name[9:])
        self.old_name.setDisabled(True)
        self.old_name.setFont(font14)
        self.old_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ввод')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.do_func)

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
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
