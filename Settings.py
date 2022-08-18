import json
import os
import sys
import shutil
import time

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal

import PhotoDataDB


font14 = QtGui.QFont('Times', 14)

stylesheet1 = "border: 0px; background-color: #F0F0F0; color: black"
stylesheet2 = "border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: black"
stylesheet4 = "border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #FFFFFF; color: black;"


# объект окна настроек
class SettingWin(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Создание окна
        self.setWindowTitle('Настройки')
        self.setStyleSheet(stylesheet1)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(800, 800)

        settings = SettingWidget()

        self.setCentralWidget(settings)


# сами настройки (виджет)
class SettingWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(800, 800)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.media_space_lbl = QLabel(self)
        self.media_space_lbl.setText('Хранилище фотографий:')
        self.media_space_lbl.setFont(font14)
        self.media_space_lbl.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.media_space_lbl, 0, 0, 1, 1)

        self.media_space_line = QLineEdit(self)
        self.media_space_line.setFont(font14)
        self.media_space_line.setStyleSheet(stylesheet4)
        self.layout.addWidget(self.media_space_line, 0, 1, 1, 1)

        self.media_space_choose = QPushButton(self)
        self.media_space_choose.setText('Выбрать путь')
        self.media_space_choose.setFont(font14)
        self.media_space_choose.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.media_space_choose, 0, 2, 1, 1)
        self.media_space_choose.clicked.connect(self.dir_media_choose)

        self.thumbs_space_lbl = QLabel(self)
        self.thumbs_space_lbl.setText('Место хранения миниатюр:')
        self.thumbs_space_lbl.setFont(font14)
        self.thumbs_space_lbl.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.thumbs_space_lbl, 1, 0, 1, 1)

        self.thumbs_space_line = QLineEdit(self)
        self.thumbs_space_line.setFont(font14)
        self.thumbs_space_line.setStyleSheet(stylesheet4)
        self.layout.addWidget(self.thumbs_space_line, 1, 1, 1, 1)

        self.thumbs_space_choose = QPushButton(self)
        self.thumbs_space_choose.setText('Выбрать путь')
        self.thumbs_space_choose.setFont(font14)
        self.thumbs_space_choose.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.thumbs_space_choose, 1, 2, 1, 1)
        self.thumbs_space_choose.clicked.connect(self.dir_thumb_choose)

        self.transfer_mode_lbl = QLabel(self)
        self.transfer_mode_lbl.setText('Режим переноса фото:')
        self.transfer_mode_lbl.setFont(font14)
        self.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.transfer_mode_lbl, 2, 0, 1, 1)

        self.transfer_mode_choose = QComboBox(self)
        self.transfer_mode_choose.setFont(font14)
        self.transfer_mode_choose.setStyleSheet(stylesheet4)
        self.transfer_mode_choose.addItem('Copy')
        self.transfer_mode_choose.addItem('Cut')
        self.layout.addWidget(self.transfer_mode_choose, 2, 1, 1, 1)

        self.num_thumbs_text = QLabel(self)
        self.num_thumbs_text.setFont(font14)
        self.num_thumbs_text.setStyleSheet(stylesheet1)
        self.num_thumbs_text.setText('Миниатюр в ряд:')
        self.layout.addWidget(self.num_thumbs_text, 3, 0, 1, 1)

        self.num_thumbs_choose = QComboBox(self)
        self.num_thumbs_choose.addItem('2')
        self.num_thumbs_choose.addItem('3')
        self.num_thumbs_choose.addItem('4')
        self.num_thumbs_choose.setFont(font14)
        self.num_thumbs_choose.setStyleSheet(stylesheet4)
        self.layout.addWidget(self.num_thumbs_choose, 3, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Сохранить')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.btn_ok, 10, 0, 1, 1)
        self.btn_ok.clicked.connect(self.check_changes)

        self.show_settings()

    # выбор папки хранения фото
    def dir_media_choose(self) -> None:
        dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '')
        if dir_chosen:
            self.media_space_line.setText(dir_chosen)
        else:
            self.media_space_line.setText(self.old_media_dir)

    # выбор папки хранения миниатюр
    def dir_thumb_choose(self) -> None:
        dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '')
        if dir_chosen:
            self.thumbs_space_line.setText(dir_chosen)
        else:
            self.thumbs_space_line.setText(self.old_thumb_dir)

    # показать записанный сейчас настройки
    def show_settings(self) -> None:
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.old_media_dir = settings['destination_dir']
        self.old_thumb_dir = settings['thumbs_dir']
        mode = settings['transfer_mode']
        num_thumbs = settings["thumbs_row"]
        self.media_space_line.setText(self.old_media_dir)
        self.thumbs_space_line.setText(self.old_thumb_dir)
        self.transfer_mode_choose.setCurrentText(mode)
        self.num_thumbs_choose.setCurrentText(num_thumbs)

    # какие пути изменили, какие нет
    def check_changes(self) -> None:
        code = 0
        if self.old_media_dir != self.media_space_line.text() and not self.old_thumb_dir != self.thumbs_space_line.text():
            code = 1
        elif not self.old_media_dir != self.media_space_line.text() and self.old_thumb_dir != self.thumbs_space_line.text():
            code = 2
        elif self.old_media_dir != self.media_space_line.text() and self.old_thumb_dir != self.thumbs_space_line.text():
            code = 3
        else:
            self.write_settings()

        if code: # if code != 0
            dialog_win = TransferFiles(self, code, self.old_media_dir, self.media_space_line.text(), self.old_thumb_dir,
                                       self.thumbs_space_line.text())
            dialog_win.show()
            dialog_win.photo_transfered.connect(self.write_settings)
            dialog_win.photo_transfered.connect(lambda: dialog_win.close())

    # перезаписать настройки на новые введённые
    def write_settings(self) -> None:
        dir_media_chosen = self.media_space_line.text()
        dir_thumb_chosen = self.thumbs_space_line.text()
        transfer_mode = self.transfer_mode_choose.currentText()
        num_thumbs = self.num_thumbs_choose.currentText()

        jsondata_wr = {'destination_dir': dir_media_chosen, 'thumbs_dir': dir_thumb_chosen,
                       'transfer_mode': transfer_mode, "thumbs_row": num_thumbs}
        with open('settings.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)
        self.show_settings()
        notice_win = Notification(self)
        notice_win.show()


# перенос папок, если изменился путь
class TransferFiles(QDialog):
    photo_transfered = QtCore.pyqtSignal()

    def __init__(self, parent, code, old_media, new_media, old_thumb, new_thumb):
        super(TransferFiles, self).__init__(parent)

        self.setStyleSheet(stylesheet1)

        self.old_media = old_media
        self.new_media = new_media
        self.old_thumb = old_thumb
        self.new_thumb = new_thumb

        self.code = code

        self.setWindowTitle("Необходим перенос файлов")
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.text_info = QLabel(self)
        self.text_info.setFont(font14)

        match code:
            case 1:
                self.text_info.setText('Была изменена директория хранения фотографий')
            case 2:
                self.text_info.setText('Была изменена директория хранения миниатюр')
            case 3:
                self.text_info.setText('Были изменены директории хранения фотографий и  миниатюр')

        self.accept_btn = QPushButton(self)
        self.accept_btn.setText('Начать')
        self.accept_btn.setFont(font14)
        self.accept_btn.setStyleSheet(stylesheet2)
        self.accept_btn.clicked.connect(self.func_accept)

        self.reject_btn = QPushButton(self)
        self.reject_btn.setText('Отмена')
        self.reject_btn.setFont(font14)
        self.reject_btn.setStyleSheet(stylesheet2)
        self.reject_btn.clicked.connect(self.func_reject)

        self.layout.addWidget(self.text_info, 0, 0, 1, 2)
        self.layout.addWidget(self.accept_btn, 1, 0, 1, 1)
        self.layout.addWidget(self.reject_btn, 1, 1, 1, 1)

    def func_accept(self) -> None:
        self.text_info.hide()
        self.accept_btn.hide()
        self.reject_btn.hide()

        self.label = QLabel(self)
        self.text = QLabel(self)
        self.text.setText('Загрузка, подождите')
        self.text.setStyleSheet(stylesheet1)
        self.movie = QMovie("g0R5.gif")
        self.label.setMovie(self.movie)
        self.label.setStyleSheet(stylesheet1)
        self.movie.start()

        self.layout.addWidget(self.label, 0, 0, 1, 1)
        self.layout.addWidget(self.text, 0, 1, 1, 1)

        proccess = DoTransfer(self.code, self.old_media, self.new_media, self.old_thumb, self.new_thumb)
        proccess.finished.connect(self.finished)

        proccess.start()

    def finished(self) -> None:
        self.photo_transfered.emit()
        self.close()

    def func_reject(self) -> None:
        self.reject()


# переброска файлов вынесена в отдельный поток, так как в одном потоке с QDialog, оно ломает GUI
class DoTransfer(QtCore.QThread):

    finished = QtCore.pyqtSignal()

    def __init__(self, code, old_media, new_media, old_thumb, new_thumb):
        QThread.__init__(self)

        self.old_media = old_media
        self.new_media = new_media
        self.old_thumb = old_thumb
        self.new_thumb = new_thumb

        self.code = code
        self._init = False

    def run(self):
        match self.code:
            case 1:
                shutil.move(self.old_media + r'/Media', self.new_media)
                new_catalogs, old_catalogs = PhotoDataDB.transfer_media_ways(self.old_media, self.new_media)
                for i in range(len(new_catalogs)):
                    PhotoDataDB.transfer_media(new_catalogs[i], old_catalogs[i])
            case 2:
                shutil.move(self.old_thumb + r'/thumbnail', self.new_thumb)
            case 3:
                shutil.move(self.old_media + r'/Media', self.new_media)
                new_catalogs, old_catalogs = PhotoDataDB.transfer_media_ways(self.old_media, self.new_media)
                for i in range(len(new_catalogs)):
                    PhotoDataDB.transfer_media(new_catalogs[i], old_catalogs[i])
                shutil.move(self.old_thumb + r'/thumbnail', self.new_thumb)

        self.finished.emit()


# уведомление о сохранении настроек
class Notification(QDialog):
    def __init__(self, parent):
        super(Notification, self).__init__(parent)
        self.setWindowTitle('Сохранено')
        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Настройки сохранены')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet1)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet2)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


# получить путь хранения медиа - для других модулей
def get_destination_media() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    destination_media = settings['destination_dir']

    return destination_media


# получить путь хранения миниатюр - для других модулей
def get_destination_thumb() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    destination_thumb = settings['thumbs_dir']

    return destination_thumb


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingWin()
    win.show()
    sys.exit(app.exec_())
