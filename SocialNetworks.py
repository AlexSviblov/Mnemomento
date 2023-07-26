import logging
import os
import sys
import sqlite3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import PhotoDataDB
import Screenconfig
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()
icon_edit = str()
icon_delete = str()


conn = sqlite3.connect('PhotoDB.db')  # соединение с БД
cur = conn.cursor()

font14 = QtGui.QFont('Times', 14)


system_scale = Screenconfig.monitor_info()[1]


class SocialNetworks(QWidget):
    """
    Соц.сети
    """
    social_network_changed = QtCore.pyqtSignal()
    resize_signal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()

        self.layout = QGridLayout(self)
        self.add_btn = QPushButton(self)
        self.empty1 = QLabel(self)
        self.networks_group = QGroupBox(self)
        self.group_layout = QGridLayout(self)

        self.make_dafeult_gui()

        self.show_social_networks()

    def make_dafeult_gui(self) -> None:
        self.setStyleSheet(stylesheet2)

        # Создание окна
        self.setWindowTitle('Соцсети')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(200, 200)

        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.add_btn.setText('Добавить')
        self.layout.addWidget(self.add_btn, 0, 0, 1, 1)
        self.add_btn.clicked.connect(self.add_func)
        self.add_btn.setFont(font14)
        self.add_btn.setFixedWidth(100)
        self.add_btn.setStyleSheet(stylesheet8)

        self.layout.addWidget(self.empty1, 0, 1, 1, 1)
        self.empty1.setStyleSheet(stylesheet2)

        self.networks_group.setStyleSheet(stylesheet2)

        self.group_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.group_layout.setSpacing(10)
        self.networks_group.setLayout(self.group_layout)
        self.layout.addWidget(self.networks_group, 1, 0, 1, 2)

    def stylesheet_color(self) -> None:
        """
        Задать стили для всего модуля в зависимости от выбранной темы
        """
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global icon_edit
        global icon_delete

        theme = Settings.get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f'{theme}']['stylesheet1']
        stylesheet2 = style[f'{theme}']['stylesheet2']
        stylesheet8 = style[f'{theme}']['stylesheet8']
        icon_edit = style[f'{theme}']['icon_edit']
        icon_delete = style[f'{theme}']['icon_delete']

        try:
            self.setStyleSheet(stylesheet2)
            self.add_btn.setStyleSheet(stylesheet8)
            self.empty1.setStyleSheet(stylesheet2)
            self.networks_group.setStyleSheet(stylesheet2)
            self.show_social_networks()
        except AttributeError:
            pass

    def show_social_networks(self) -> None:
        """
        Отобразить введённые соцсети
        """
        for i in reversed(range(self.group_layout.count())):
            self.group_layout.itemAt(i).widget().deleteLater()

        networks = PhotoDataDB.get_socialnetworks()
        max_sn_name = 0
        for i in range(0, len(networks)):
            soc_net_lbl = QLabel(self)
            soc_net_lbl.setFont(font14)
            if networks[i][0:9] != 'numnumnum':
                soc_net_lbl.setText(f'{networks[i]}')
            else:
                soc_net_lbl.setText(f'{networks[i][9:]}')

            if len(soc_net_lbl.text()) > max_sn_name:
                max_sn_name = len(soc_net_lbl.text())

            self.group_layout.addWidget(soc_net_lbl, i, 0, 1, 1)

            btn_red = QToolButton(self)
            btn_red.setStyleSheet(stylesheet1)
            btn_red.setFixedSize(int(50*system_scale)+1, int(50*system_scale)+1)
            btn_red.setIcon(QtGui.QIcon(icon_edit))
            btn_red.setToolTip('Редактировать название')
            btn_red.setObjectName(networks[i])
            btn_red.clicked.connect(self.func_red)
            self.group_layout.addWidget(btn_red, i, 1, 1, 1)

            btn_del = QToolButton(self)
            btn_del.setStyleSheet(stylesheet1)
            btn_del.setFixedSize(int(50*system_scale)+1, int(50*system_scale)+1)
            btn_del.setIcon(QtGui.QIcon(icon_delete))
            btn_del.setToolTip('Удалить соцсеть')
            btn_del.setObjectName(networks[i])
            btn_del.clicked.connect(self.func_del)
            self.group_layout.addWidget(btn_del, i, 2, 1, 1)

        try:
            soc_net_lbl.setFixedWidth(int((max_sn_name*15) * system_scale) + 1)
            self.networks_group.setFixedWidth(soc_net_lbl.width() + btn_del.width() + btn_red.width() + self.group_layout.spacing() * 4 + 10)
            self.networks_group.setFixedHeight(self.add_btn.height() + len(networks) * 60)
        except (AttributeError, RuntimeError):
            pass
        self.resize(self.networks_group.width(), self.add_btn.height() + self.networks_group.height() + 10)
        self.resize_signal.emit(self.networks_group.width(), self.add_btn.height() + self.networks_group.height() + 10)

    def add_func(self) -> None:
        """
        Добавление соцсети
        """
        dialog_add = AddSN()
        dialog_add.social_network_changed.connect(self.social_network_changed.emit)
        if dialog_add.exec():
            pass

        self.show_social_networks()

    def func_red(self) -> None:
        """
        Редактирование имени соцсети
        """
        net_name = self.sender().objectName()
        red_dialog = RedSN(net_oldname=net_name)
        red_dialog.social_network_changed.connect(self.social_network_changed.emit)
        if red_dialog.exec():
            pass

        self.show_social_networks()

    def func_del(self) -> None:
        """
        Удаление соцсети
        """
        net_name = self.sender().objectName()
        del_dialog = DelSN(net_name=net_name)
        del_dialog.social_network_changed.connect(self.social_network_changed.emit)
        if del_dialog.exec():
            pass

        self.show_social_networks()


class AddSN(QDialog):
    """
    Добавление новой соцсети
    """
    social_network_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(AddSN, self).__init__()
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.text_lbl = QLabel(self)

        self.enter_name = QLineEdit(self)

        self.btn_ok = QPushButton(self)

        self.btn_cnl = QPushButton(self)

        self.make_gui()

    def make_gui(self) -> None:
        self.setWindowTitle('Добавить соцсеть')
        self.resize(600, 90)
        self.setStyleSheet(stylesheet2)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.text_lbl.setText('Введите название соцсети:')
        self.text_lbl.setFont(font14)
        self.text_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.text_lbl, 0, 0, 1, 1)

        self.enter_name.setFont(font14)
        self.enter_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.enter_name, 0, 1, 1, 1)

        self.enter_name.setFont(font14)
        self.enter_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.enter_name, 0, 1, 1, 1)

        self.btn_ok.setText('Ввод')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cnl, 1, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    def func_ok(self) -> None:
        self.check_empty()

    def check_empty(self) -> None:
        """
        Проверка заполнения полей ввода
        """
        if self.enter_name.text() != '':
            self.do_func()
        else:
            return

    def do_func(self) -> None:
        """
        После подтверждения добавления
        """
        sql_str = f'ALTER TABLE socialnetworks ADD COLUMN {self.enter_name.text()} TEXT DEFAULT \'No value\''
        try:
            cur.execute(sql_str)
        except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
            textwithnum = 'numnumnum' + self.enter_name.text()
            sql_str = f'ALTER TABLE socialnetworks ADD COLUMN {textwithnum} TEXT DEFAULT \'No value\''
            cur.execute(sql_str)
        conn.commit()
        logging.info(f"New social network added {self.enter_name.text()}")

        self.social_network_changed.emit()
        self.accept()


class RedSN(QDialog):
    """
    Переименование соцсети
    """
    social_network_changed = QtCore.pyqtSignal()

    def __init__(self, net_oldname: str):
        super(RedSN, self).__init__()
        self.net_oldname = net_oldname

        self.layout = QGridLayout(self)

        self.old_name_lbl = QLabel(self)
        self.old_name = QLineEdit(self)
        self.new_name_lbl = QLabel(self)
        self.new_name = QLineEdit(self)
        self.btn_ok = QPushButton(self)
        self.btn_cnl = QPushButton(self)

        self.make_gui()

    def make_gui(self) -> None:
        self.setWindowTitle('Редактирование названия')
        self.resize(600, 90)
        self.setStyleSheet(stylesheet2)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.setLayout(self.layout)

        self.old_name_lbl.setText('Старое название:')
        self.old_name_lbl.setFont(font14)
        self.old_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        if self.net_oldname[0:9] != 'numnumnum':
            self.old_name.setText(self.net_oldname)
        else:
            self.old_name.setText(self.net_oldname[9:])
        self.old_name.setDisabled(True)
        self.old_name.setFont(font14)
        self.old_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.new_name_lbl.setText('Новое название:')
        self.new_name_lbl.setFont(font14)
        self.new_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.new_name_lbl, 1, 0, 1, 1)

        self.new_name.setFont(font14)
        self.new_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.new_name, 1, 1, 1, 1)

        self.btn_ok.setText('Ввод')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.func_ok)

        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cnl, 2, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    def func_ok(self) -> None:
        """
        Запуск проверки check_empty
        :return:
        """
        self.check_empty()

    def check_empty(self) -> None:
        """
        Проверка заполнения полей ввода
        """
        if self.new_name.text() != '':
            self.do_func()
        else:
            return

    def do_func(self) -> None:
        """
        После проверки на пустоту - редактировать
        """
        sql_str = f'ALTER TABLE socialnetworks RENAME COLUMN {self.net_oldname} TO {self.new_name.text()}'
        try:
            cur.execute(sql_str)
        except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
            textwithnum = 'numnumnum' + self.new_name.text()
            sql_str = f'ALTER TABLE socialnetworks RENAME COLUMN {self.net_oldname} TO {textwithnum}'
            cur.execute(sql_str)
        conn.commit()
        logging.info(f"Social network {self.net_oldname} renamed into {self.new_name.text()}")

        self.social_network_changed.emit()
        self.accept()


class DelSN(QDialog):
    """
    Удалить соцсеть
    """
    social_network_changed = QtCore.pyqtSignal()

    def __init__(self, net_name: str):
        super(DelSN, self).__init__()
        self.net_name = net_name

        self.layout = QGridLayout(self)

        self.old_name_lbl = QLabel(self)
        self.old_name = QLineEdit(self)
        self.btn_ok = QPushButton(self)
        self.btn_cnl = QPushButton(self)

        self.make_gui()

    def make_gui(self) -> None:
        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Редактирование названия')
        self.resize(600, 80)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.setLayout(self.layout)

        self.old_name_lbl.setText('Вы уверены, что хотите удалить:')
        self.old_name_lbl.setFont(font14)
        self.old_name_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.old_name_lbl, 0, 0, 1, 1)

        if self.net_name[0:9] != 'numnumnum':
            self.old_name.setText(self.net_name)
        else:
            self.old_name.setText(self.net_name[9:])
        self.old_name.setDisabled(True)
        self.old_name.setFont(font14)
        self.old_name.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.old_name, 0, 1, 1, 1)

        self.btn_ok.setText('Подтвердить')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 2, 0, 1, 1)
        self.btn_ok.clicked.connect(self.do_func)

        self.btn_cnl.setText('Отмена')
        self.btn_cnl.setFont(font14)
        self.btn_cnl.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cnl, 2, 1, 1, 1)
        self.btn_cnl.clicked.connect(lambda: self.close())

    def do_func(self) -> None:
        """
        После подтверждения удаления. Само удаление
        """
        sql_str = f'ALTER TABLE socialnetworks DROP COLUMN {self.net_name}'
        cur.execute(sql_str)
        conn.commit()

        logging.info(f"Social network {self.net_name} deleted")

        self.social_network_changed.emit()
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SocialNetworks()
    win.show()
    sys.exit(app.exec_())
