import json
import os
import sys
import shutil
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal

import PhotoDataDB


font14 = QtGui.QFont('Times', 14)


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()
stylesheet9 = str()
loading_icon = str()


# объект окна настроек
class SettingWin(QMainWindow):
    update_main_widget = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle('Настройки')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        settings = SettingWidget()
        settings.update_main_widget.connect(self.update_main_widget.emit)
        settings.update_main_widget.connect(self.stylesheet_color)
        settings.update_main_widget.connect(lambda: self.setStyleSheet(stylesheet2))
        settings.update_main_widget.connect(settings.update_stylesheet)
        settings.cancel_signal.connect(self.close)
        self.setCentralWidget(settings)
        self.resize(settings.size())

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global stylesheet9
        global loading_icon

        if get_theme_color() == 'light':
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
            loading_icon = os.getcwd() + '/icons/loading_light.gif'
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
            loading_icon = os.getcwd() + '/icons/loading_dark.gif'


# сами настройки (виджет)
class SettingWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.media_space_lbl = QLabel(self)
        self.media_space_lbl.setText('Хранилище фотографий:')
        self.media_space_lbl.setFont(font14)
        self.media_space_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.media_space_lbl, 0, 0, 1, 1)

        self.media_space_line = QLineEdit(self)
        self.media_space_line.setFont(font14)
        self.media_space_line.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.media_space_line, 0, 1, 1, 1)

        self.media_space_choose = QPushButton(self)
        self.media_space_choose.setText('Выбрать путь')
        self.media_space_choose.setFont(font14)
        self.media_space_choose.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.media_space_choose, 0, 2, 1, 1)
        self.media_space_choose.clicked.connect(self.dir_media_choose)

        self.thumbs_space_lbl = QLabel(self)
        self.thumbs_space_lbl.setText('Место хранения миниатюр:')
        self.thumbs_space_lbl.setFont(font14)
        self.thumbs_space_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.thumbs_space_lbl, 1, 0, 1, 1)

        self.thumbs_space_line = QLineEdit(self)
        self.thumbs_space_line.setFont(font14)
        self.thumbs_space_line.setStyleSheet(stylesheet1)
        self.layout.addWidget(self.thumbs_space_line, 1, 1, 1, 1)

        self.thumbs_space_choose = QPushButton(self)
        self.thumbs_space_choose.setText('Выбрать путь')
        self.thumbs_space_choose.setFont(font14)
        self.thumbs_space_choose.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.thumbs_space_choose, 1, 2, 1, 1)
        self.thumbs_space_choose.clicked.connect(self.dir_thumb_choose)

        self.transfer_mode_lbl = QLabel(self)
        self.transfer_mode_lbl.setText('Режим переноса фото:')
        self.transfer_mode_lbl.setFont(font14)
        self.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.transfer_mode_lbl, 2, 0, 1, 1)

        self.transfer_mode_choose = QComboBox(self)
        self.transfer_mode_choose.setFont(font14)
        self.transfer_mode_choose.setStyleSheet(stylesheet9)
        self.transfer_mode_choose.addItem('copy')
        self.transfer_mode_choose.addItem('cut')
        self.layout.addWidget(self.transfer_mode_choose, 2, 1, 1, 1)

        self.num_thumbs_lbl = QLabel(self)
        self.num_thumbs_lbl.setFont(font14)
        self.num_thumbs_lbl.setStyleSheet(stylesheet2)
        self.num_thumbs_lbl.setText('Миниатюр в ряд:')
        self.layout.addWidget(self.num_thumbs_lbl, 3, 0, 1, 1)

        self.num_thumbs_choose = QComboBox(self)
        self.num_thumbs_choose.setFont(font14)
        self.num_thumbs_choose.setStyleSheet(stylesheet1)
        self.num_thumbs_choose.addItem('2')
        self.num_thumbs_choose.addItem('3')
        self.num_thumbs_choose.addItem('4')
        self.layout.addWidget(self.num_thumbs_choose, 3, 1, 1, 1)

        self.theme_lbl = QLabel(self)
        self.theme_lbl.setText('Тема:')
        self.theme_lbl.setFont(font14)
        self.theme_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.theme_lbl, 4, 0, 1, 1)

        self.theme_choose = QComboBox(self)
        self.theme_choose.setFont(font14)
        self.theme_choose.setStyleSheet(stylesheet9)
        self.theme_choose.addItem('light')
        self.theme_choose.addItem('dark')
        self.layout.addWidget(self.theme_choose, 4, 1, 1, 1)
        
        self.socnet_lbl = QLabel(self)
        self.socnet_lbl.setStyleSheet(stylesheet2)
        self.socnet_lbl.setFont(font14)
        self.socnet_lbl.setText("Соцсети включены")
        self.layout.addWidget(self.socnet_lbl, 5, 0, 1, 1)

        self.socnet_choose = QCheckBox(self)
        self.socnet_choose.setFont(font14)
        self.layout.addWidget(self.socnet_choose, 5, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Сохранить')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 10, 0, 1, 1)
        self.btn_ok.clicked.connect(self.check_changes)

        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText('Отмена')
        self.btn_cancel.setFont(font14)
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cancel, 10, 2, 1, 1)
        self.btn_cancel.clicked.connect(self.cancel_signal.emit)

        self.show_settings()

        self.resize(800, 240)

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
        try:
            with open('settings.json', 'r') as json_file:
                settings = json.load(json_file)
        except FileNotFoundError:

            pass
        self.old_media_dir = settings['destination_dir']
        self.old_thumb_dir = settings['thumbs_dir']
        mode = settings['transfer_mode']
        self.old_num_thumbs = settings["thumbs_row"]
        self.old_theme_color = settings["color_theme"]
        self.old_socnet_status = settings["social_networks_status"]
        self.media_space_line.setText(self.old_media_dir)
        self.thumbs_space_line.setText(self.old_thumb_dir)
        self.transfer_mode_choose.setCurrentText(mode)
        self.num_thumbs_choose.setCurrentText(self.old_num_thumbs)
        self.theme_choose.setCurrentText(self.old_theme_color)

        if self.old_socnet_status:
            self.socnet_choose.setChecked(QtCore.Qt.Checked)
        else:
            self.socnet_choose.setChecked(QtCore.Qt.Unchecked)

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
        theme_color = self.theme_choose.currentText()
        socnet_status = self.socnet_choose.checkState()


        jsondata_wr = {'destination_dir': dir_media_chosen, 'thumbs_dir': dir_thumb_chosen,
                       'transfer_mode': transfer_mode, "thumbs_row": num_thumbs, "color_theme": theme_color,
                       'social_networks_status': socnet_status}

        with open('settings.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.parent().stylesheet_color()

        notice_win = Notification(self)
        notice_win.show()

        if dir_thumb_chosen != self.old_thumb_dir or dir_media_chosen != self.old_media_dir or \
                num_thumbs != self.old_num_thumbs or theme_color != self.old_theme_color or \
                socnet_status != self.old_socnet_status:
            self.update_main_widget.emit()

        self.show_settings()

    # обновить собственный вид при изменении настроек вида
    def update_stylesheet(self):
        self.setStyleSheet(stylesheet2)
        self.media_space_lbl.setStyleSheet(stylesheet2)
        self.media_space_line.setStyleSheet(stylesheet1)
        self.media_space_choose.setStyleSheet(stylesheet8)
        self.thumbs_space_lbl.setStyleSheet(stylesheet2)
        self.thumbs_space_line.setStyleSheet(stylesheet1)
        self.thumbs_space_choose.setStyleSheet(stylesheet8)
        self.transfer_mode_choose.setStyleSheet(stylesheet9)
        self.num_thumbs_lbl.setStyleSheet(stylesheet2)
        self.num_thumbs_choose.setStyleSheet(stylesheet1)
        self.theme_lbl.setStyleSheet(stylesheet2)
        self.theme_choose.setStyleSheet(stylesheet9)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.socnet_lbl.setStyleSheet(stylesheet2)


# перенос папок, если изменился путь
class TransferFiles(QDialog):
    photo_transfered = QtCore.pyqtSignal()

    def __init__(self, parent, code, old_media, new_media, old_thumb, new_thumb):
        super(TransferFiles, self).__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(stylesheet2)

        self.old_media = old_media
        self.new_media = new_media
        self.old_thumb = old_thumb
        self.new_thumb = new_thumb

        self.code = code

        self.setWindowTitle("Необходим перенос файлов")
        self.layout_win = QGridLayout(self)
        self.setLayout(self.layout_win)
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
        self.accept_btn.setStyleSheet(stylesheet8)
        self.accept_btn.clicked.connect(self.func_accept)

        self.reject_btn = QPushButton(self)
        self.reject_btn.setText('Отмена')
        self.reject_btn.setFont(font14)
        self.reject_btn.setStyleSheet(stylesheet8)
        self.reject_btn.clicked.connect(self.func_reject)

        self.layout_win.addWidget(self.text_info, 0, 0, 1, 2)
        self.layout_win.addWidget(self.accept_btn, 1, 0, 1, 1)
        self.layout_win.addWidget(self.reject_btn, 1, 1, 1, 1)

    def func_accept(self) -> None:
        self.text_info.hide()
        self.accept_btn.hide()
        self.reject_btn.hide()

        self.label = QLabel(self)
        self.text = QLabel(self)
        self.text.setText('Загрузка, подождите')
        self.text.setStyleSheet(stylesheet2)
        self.text.setFont(font14)
        self.movie = QMovie(loading_icon)
        self.label.setMovie(self.movie)
        self.label.setStyleSheet(stylesheet2)
        self.movie.start()

        self.layout_win.addWidget(self.label, 0, 0, 1, 1)
        self.layout_win.addWidget(self.text, 0, 1, 1, 1)

        self.proccess = DoTransfer(self.code, self.old_media, self.new_media, self.old_thumb, self.new_thumb)
        self.proccess.finished.connect(self.func_finished)

        self.proccess.start()

    def func_finished(self) -> None:
        self.photo_transfered.emit()
        self.proccess = None
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
                shutil.copytree(self.old_media + r'/Media', self.old_media + r'/Media_reserve')
                shutil.copy(os.getcwd() + '/PhotoDB.db', os.getcwd() + '/PhotoDB_reserve.db')

                shutil.move(self.old_media + r'/Media', self.new_media)
                new_catalogs, old_catalogs = PhotoDataDB.transfer_media_ways(self.old_media, self.new_media)
                for i in range(len(new_catalogs)):
                    PhotoDataDB.transfer_media(new_catalogs[i], old_catalogs[i])

                shutil.rmtree(self.old_media + r'/Media_reserve')
                os.remove(os.getcwd() + '/PhotoDB_reserve.db')

            case 2:
                shutil.copytree(self.old_thumb + r'/thumbnail', self.old_thumb + r'/thumbnail_reserve')
                shutil.move(self.old_thumb + r'/thumbnail', self.new_thumb)
                shutil.rmtree(self.old_thumb + r'/thumbnail_reserve')
            case 3:
                shutil.copytree(self.old_media + r'/Media', self.old_media + r'/Media_reserve')
                shutil.copy(os.getcwd() + '/PhotoDB.db', os.getcwd() + '/PhotoDB_reserve.db')
                shutil.copytree(self.old_thumb + r'/thumbnail', self.old_thumb + r'/thumbnail_reserve')

                shutil.move(self.old_media + r'/Media', self.new_media)
                new_catalogs, old_catalogs = PhotoDataDB.transfer_media_ways(self.old_media, self.new_media)
                for i in range(len(new_catalogs)):
                    PhotoDataDB.transfer_media(new_catalogs[i], old_catalogs[i])
                shutil.move(self.old_thumb + r'/thumbnail', self.new_thumb)

                shutil.rmtree(self.old_media + r'/Media_reserve')
                os.remove(os.getcwd() + '/PhotoDB_reserve.db')
                shutil.rmtree(self.old_media + r'/thumbnail_reserve')

        self.finished.emit()


# уведомление о сохранении настроек
class Notification(QDialog):
    def __init__(self, parent):
        super(Notification, self).__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Сохранено')
        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Настройки сохранены')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
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


# количество миниатюр в строке
def get_thumbs_rows() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    thumbs_rows = settings['thumbs_rows']
    return thumbs_rows


# режим переноса фото при добавлении
def get_photo_transfer_mode() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    transfer_mode = settings['transfer_mode']
    return transfer_mode


# выбранная визуальная тема
def get_theme_color() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    theme_color = settings['color_theme']
    return theme_color


# включены или отключены соцсети
def get_socnet_status() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    socnet_status = int(settings['social_networks_status'])
    return socnet_status


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingWin()
    win.show()
    sys.exit(app.exec_())
