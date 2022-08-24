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
        self.setWindowTitle('Восстановление')
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
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1c1c1c"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #1c1c1c"


class RecoveryWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet2)
        self.setWindowTitle('Восстановление')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.lbl_len_photos = QLabel(self)
        self.lbl_len_photos.setText("Записей в таблице данных о фотографиях:")
        self.lbl_len_photos.setFont(font14)
        self.lbl_len_photos.setStyleSheet(stylesheet2)

        self.lbl_len_socnets = QLabel(self)
        self.lbl_len_socnets.setText("Записей в таблице о социальных сетях:")
        self.lbl_len_socnets.setFont(font14)
        self.lbl_len_socnets.setStyleSheet(stylesheet2)

        self.lbl_err_photos = QLabel(self)
        self.lbl_err_photos.setText("      Обнаружено ошибок в таблице данных о фотографиях:")
        self.lbl_err_photos.setFont(font14)
        self.lbl_err_photos.setStyleSheet(stylesheet2)

        self.lbl_err_socnets = QLabel(self)
        self.lbl_err_socnets.setText("      Обнаружено ошибок в таблице о социальных сетях:")
        self.lbl_err_socnets.setFont(font14)
        self.lbl_err_socnets.setStyleSheet(stylesheet2)

        self.lbl_len_exists = QLabel(self)
        self.lbl_len_exists.setText("Фотографий в папке хранения:")
        self.lbl_len_exists.setFont(font14)
        self.lbl_len_exists.setStyleSheet(stylesheet2)

        self.len_photos_value = QLineEdit(self)
        self.len_photos_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[0])))
        self.len_photos_value.setDisabled(True)
        self.len_photos_value.setFont(font14)
        self.len_photos_value.setStyleSheet(stylesheet1)

        self.len_socnets_value = QLineEdit(self)
        self.len_socnets_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[1])))
        self.len_socnets_value.setDisabled(True)
        self.len_socnets_value.setFont(font14)
        self.len_socnets_value.setStyleSheet(stylesheet1)

        self.err_photos_value = QLineEdit(self)
        self.err_photos_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[0]))
        self.err_photos_value.setDisabled(True)
        self.err_photos_value.setFont(font14)
        self.err_photos_value.setStyleSheet(stylesheet1)

        self.err_socnets_value = QLineEdit(self)
        self.err_socnets_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[1]))
        self.err_socnets_value.setDisabled(True)
        self.err_socnets_value.setFont(font14)
        self.err_socnets_value.setStyleSheet(stylesheet1)

        self.len_exists_value = QLineEdit(self)
        self.len_exists_value.setText(str(len(SynhronizeDBMedia.research_all_media_photos())))
        self.len_exists_value.setDisabled(True)
        self.len_exists_value.setFont(font14)
        self.len_exists_value.setStyleSheet(stylesheet1)

        self.layout.addWidget(self.lbl_len_photos, 0, 0, 1, 1)
        self.layout.addWidget(self.len_photos_value, 0, 1, 1, 1)
        self.layout.addWidget(self.lbl_len_socnets, 1, 0, 1, 1)
        self.layout.addWidget(self.len_socnets_value, 1, 1, 1, 1)
        self.layout.addWidget(self.lbl_err_photos, 0, 2, 1, 1)
        self.layout.addWidget(self.err_photos_value, 0, 3, 1, 1)
        self.layout.addWidget(self.lbl_err_socnets, 1, 2, 1, 1)
        self.layout.addWidget(self.err_socnets_value, 1, 3, 1, 1)
        self.layout.addWidget(self.lbl_len_exists, 2, 0, 1, 1)
        self.layout.addWidget(self.len_exists_value, 2, 1, 1, 1)



        self.resize(800, 220)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RecoveryWin()
    win.show()
    sys.exit(app.exec_())

