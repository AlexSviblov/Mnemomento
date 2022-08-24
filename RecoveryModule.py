import json
import os
import sys
import shutil
import time

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal

import Settings
import SynhronizeDBMedia


font14 = QtGui.QFont('Times', 14)


# объект окна настроек
class RecoveryWin(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()

        # Создание окна
        self.setWindowTitle('Настройки')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        recovery = RecoveryWidget()
        self.setCentralWidget(recovery)
        self.resize(recovery.size())

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet6

        if Settings.get_theme_color() == 'light':
            stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0"
            stylesheet2 = "border: 0px; color: #000000; background-color: #F0F0F0"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}"
            stylesheet6 = "QTableView{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;gridline-color: #A9A9A9;}"
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1c1c1c"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #1c1c1c"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #696969; border-style: solid; background-color: #1c1c1c; color: #D3D3D3;}"
            stylesheet6 = "QTableView{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1c1c1c; gridline-color: #696969;}"


class RecoveryWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Восстановление')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        # self.resize(800, 800)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)




        self.resize(800, 220)


