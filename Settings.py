# TODO: ввод комбинаций горячих клавиш
# комбинация написана на кнопке, при нажатии на неё справа появляется строка ввода, считывается KeyPressEvent и значение вносится в строку.
# под строкой ввода крестик и галочка - отмены или перезаписи новой введённой комбинации
#
# def keyPressEvent(self, e):
#     print(e.key())
#     if e.key() == QtCore.Qt.Key_I:
#         print('I')

import json
import logging
import os
import sys
import shutil
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal

import ErrorsAndWarnings
import PhotoDataDB
import Screenconfig

font14 = QtGui.QFont('Times', 14)


stylesheet1 = str()
stylesheet2 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()
loading_icon = str()


system_scale = Screenconfig.monitor_info()[1]


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
        self.setMinimumSize(1000, 300)

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
        global stylesheet7
        global stylesheet8
        global stylesheet9
        global loading_icon

        theme = get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f'{theme}']['stylesheet1']
        stylesheet2 = style[f'{theme}']['stylesheet2']
        stylesheet7 = style[f'{theme}']['stylesheet7']
        stylesheet8 = style[f'{theme}']['stylesheet8']
        stylesheet9 = style[f'{theme}']['stylesheet9']
        loading_icon = style[f'{theme}']['loading_icon']


# сами настройки (виджет)
class SettingWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1000, 300)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(5)

        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet(stylesheet7)

        self.make_gui()

        self.tabs.setFont(font14)
        self.layout.addWidget(self.tabs, 0, 0, 1, 3)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Сохранить')
        self.btn_ok.setFont(font14)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.check_changes)

        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText('Отмена')
        self.btn_cancel.setFont(font14)
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cancel, 1, 2, 1, 1)
        self.btn_cancel.clicked.connect(self.cancel_signal.emit)

        self.show_settings()

        self.resize(800, 240)

    # создание интерфейса
    def make_gui(self) -> None:
        self.tab_files = QWidget(self)
        self.tab_view = QWidget(self)
        self.tab_hotkeys = QWidget(self)

        def make_files() -> None:
            self.layout_files = QGridLayout(self)

            self.media_space_lbl = QLabel(self)
            self.media_space_lbl.setText('Хранилище фотографий:')
            self.media_space_lbl.setFont(font14)
            self.media_space_lbl.setStyleSheet(stylesheet2)
            self.layout_files.addWidget(self.media_space_lbl, 0, 0, 1, 1)

            self.media_space_line = QLineEdit(self)
            self.media_space_line.setFont(font14)
            self.media_space_line.setStyleSheet(stylesheet1)
            self.layout_files.addWidget(self.media_space_line, 0, 1, 1, 1)

            self.media_space_choose = QPushButton(self)
            self.media_space_choose.setText('Выбрать путь')
            self.media_space_choose.setFont(font14)
            self.media_space_choose.setStyleSheet(stylesheet8)
            self.layout_files.addWidget(self.media_space_choose, 0, 2, 1, 1)
            self.media_space_choose.clicked.connect(self.dir_media_choose)

            self.thumbs_space_lbl = QLabel(self)
            self.thumbs_space_lbl.setText('Место хранения миниатюр:')
            self.thumbs_space_lbl.setFont(font14)
            self.thumbs_space_lbl.setStyleSheet(stylesheet2)
            self.layout_files.addWidget(self.thumbs_space_lbl, 1, 0, 1, 1)

            self.thumbs_space_line = QLineEdit(self)
            self.thumbs_space_line.setFont(font14)
            self.thumbs_space_line.setStyleSheet(stylesheet1)
            self.layout_files.addWidget(self.thumbs_space_line, 1, 1, 1, 1)

            self.thumbs_space_choose = QPushButton(self)
            self.thumbs_space_choose.setText('Выбрать путь')
            self.thumbs_space_choose.setFont(font14)
            self.thumbs_space_choose.setStyleSheet(stylesheet8)
            self.layout_files.addWidget(self.thumbs_space_choose, 1, 2, 1, 1)
            self.thumbs_space_choose.clicked.connect(self.dir_thumb_choose)

            self.transfer_mode_lbl = QLabel(self)
            self.transfer_mode_lbl.setText('Режим переноса фото:')
            self.transfer_mode_lbl.setFont(font14)
            self.setStyleSheet(stylesheet2)
            self.layout_files.addWidget(self.transfer_mode_lbl, 2, 0, 1, 1)

            self.transfer_mode_choose = QComboBox(self)
            self.transfer_mode_choose.setFont(font14)
            self.transfer_mode_choose.setStyleSheet(stylesheet9)
            self.transfer_mode_choose.addItem('copy')
            self.transfer_mode_choose.addItem('cut')
            self.layout_files.addWidget(self.transfer_mode_choose, 2, 1, 1, 1)

            self.logs_lbl = QLabel(self)
            self.logs_lbl.setStyleSheet(stylesheet2)
            self.logs_lbl.setFont(font14)
            self.logs_lbl.setText("Логи")
            self.layout_files.addWidget(self.logs_lbl, 3, 0, 1, 1)

            self.logs_show = QPushButton(self)
            self.logs_show.setStyleSheet(stylesheet8)
            self.logs_show.setFont(font14)
            self.logs_show.setText("Просмотреть логи")
            self.layout_files.addWidget(self.logs_show, 3, 1, 1, 1)
            self.logs_show.clicked.connect(self.call_explorer_logs)

            self.logs_btn = QPushButton(self)
            self.logs_btn.setStyleSheet(stylesheet8)
            self.logs_btn.setFont(font14)
            self.logs_btn.setText('Очистить логи')
            self.layout_files.addWidget(self.logs_btn, 3, 2, 1, 1)
            self.logs_btn.clicked.connect(self.clear_logs)

            self.tab_files.setLayout(self.layout_files)

        def make_view() -> None:
            self.layout_view = QGridLayout(self)

            self.num_thumbs_lbl = QLabel(self)
            self.num_thumbs_lbl.setFont(font14)
            self.num_thumbs_lbl.setStyleSheet(stylesheet2)
            self.num_thumbs_lbl.setText('Миниатюр в ряд:')
            self.layout_view.addWidget(self.num_thumbs_lbl, 0, 0, 1, 1)

            self.num_thumbs_choose = QComboBox(self)
            self.num_thumbs_choose.setFont(font14)
            self.num_thumbs_choose.setStyleSheet(stylesheet1)
            self.num_thumbs_choose.addItem('2')
            self.num_thumbs_choose.addItem('3')
            self.num_thumbs_choose.addItem('4')
            self.layout_view.addWidget(self.num_thumbs_choose, 0, 1, 1, 1)

            self.theme_lbl = QLabel(self)
            self.theme_lbl.setText('Тема:')
            self.theme_lbl.setFont(font14)
            self.theme_lbl.setStyleSheet(stylesheet2)
            self.layout_view.addWidget(self.theme_lbl, 1, 0, 1, 1)

            self.theme_choose = QComboBox(self)
            self.theme_choose.setFont(font14)
            self.theme_choose.setStyleSheet(stylesheet9)
            self.theme_choose.addItem('light')
            self.theme_choose.addItem('dark')
            self.theme_choose.addItem('auto')
            self.layout_view.addWidget(self.theme_choose, 1, 1, 1, 1)

            self.socnet_lbl = QLabel(self)
            self.socnet_lbl.setStyleSheet(stylesheet2)
            self.socnet_lbl.setFont(font14)
            self.socnet_lbl.setText("Соцсети включены")
            self.layout_view.addWidget(self.socnet_lbl, 2, 0, 1, 1)

            self.socnet_choose = QCheckBox(self)
            self.socnet_choose.setFont(font14)
            self.layout_view.addWidget(self.socnet_choose, 2, 1, 1, 1)

            self.sort_type = QLabel(self)
            self.sort_type.setFont(font14)
            self.sort_type.setStyleSheet(stylesheet2)
            self.sort_type.setText("Сортировка фото")
            self.layout_view.addWidget(self.sort_type, 3, 0, 1, 1)

            self.sort_choose = QComboBox(self)
            self.sort_choose.setFont(font14)
            self.sort_choose.setStyleSheet(stylesheet9)
            self.sort_choose.addItem("Имя файла /\\")
            self.sort_choose.addItem("Имя файла \\/")
            self.sort_choose.addItem("Дата съёмки /\\")
            self.sort_choose.addItem("Дата съёмки \\/")
            self.sort_choose.addItem("Дата добавления /\\")
            self.sort_choose.addItem("Дата добавления \\/")
            self.layout_view.addWidget(self.sort_choose, 3, 1, 1, 1)

            self.tab_view.setLayout(self.layout_view)

        def make_hotkeys() -> None:
            self.layout_hotkeys = QGridLayout(self)

            self.open_file_lbl = QLabel(self)
            self.open_file_lbl.setStyleSheet(stylesheet2)
            self.open_file_lbl.setFont(font14)
            self.open_file_lbl.setText("Открыть файл")
            self.layout_hotkeys.addWidget(self.open_file_lbl, 0, 0, 1, 1)

            self.open_file_enter = QPushButton(self)
            self.open_file_enter.setStyleSheet(stylesheet8)
            self.open_file_enter.setFont(font14)
            self.layout_hotkeys.addWidget(self.open_file_enter, 0, 1, 1, 1)

            self.edit_metadata_lbl = QLabel(self)
            self.edit_metadata_lbl.setStyleSheet(stylesheet2)
            self.edit_metadata_lbl.setFont(font14)
            self.edit_metadata_lbl.setText("Редактировать метаданные")
            self.layout_hotkeys.addWidget(self.edit_metadata_lbl, 1, 0, 1, 1)

            self.edit_metadata_enter = QPushButton(self)
            self.edit_metadata_enter.setStyleSheet(stylesheet8)
            self.edit_metadata_enter.setFont(font14)
            self.layout_hotkeys.addWidget(self.edit_metadata_enter, 1, 1, 1, 1)

            self.open_explorer_lbl = QLabel(self)
            self.open_explorer_lbl.setStyleSheet(stylesheet2)
            self.open_explorer_lbl.setFont(font14)
            self.open_explorer_lbl.setText("Открыть директорию с файлом")
            self.layout_hotkeys.addWidget(self.open_explorer_lbl, 2, 0, 1, 1)

            self.open_explorer_enter = QPushButton(self)
            self.open_explorer_enter.setStyleSheet(stylesheet8)
            self.open_explorer_enter.setFont(font14)
            self.layout_hotkeys.addWidget(self.open_explorer_enter, 2, 1, 1, 1)

            self.delete_file_lbl = QLabel(self)
            self.delete_file_lbl.setStyleSheet(stylesheet2)
            self.delete_file_lbl.setFont(font14)
            self.delete_file_lbl.setText("Удалить файл")
            self.layout_hotkeys.addWidget(self.delete_file_lbl, 3, 0, 1, 1)

            self.delete_file_enter = QPushButton(self)
            self.delete_file_enter.setStyleSheet(stylesheet8)
            self.delete_file_enter.setFont(font14)
            self.layout_hotkeys.addWidget(self.delete_file_enter, 3, 1, 1, 1)

            self.do_any_lbl = QLabel(self)
            self.do_any_lbl.setStyleSheet(stylesheet2)
            self.do_any_lbl.setFont(font14)
            self.do_any_lbl.setText("Показать карту/статистику")
            self.layout_hotkeys.addWidget(self.do_any_lbl, 4, 0, 1, 1)

            self.do_any_enter = QPushButton(self)
            self.do_any_enter.setStyleSheet(stylesheet8)
            self.do_any_enter.setFont(font14)
            self.layout_hotkeys.addWidget(self.do_any_enter, 4, 1, 1, 1)

            self.tab_hotkeys.setLayout(self.layout_hotkeys)

        make_files()
        make_view()
        make_hotkeys()

        self.tabs.addTab(self.tab_files, 'Файлы')
        self.tabs.addTab(self.tab_view, 'Внешний вид')
        self.tabs.addTab(self.tab_hotkeys, 'Горячие клавиши')

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
        def show_sort_type(chosen):
            match chosen:
                case "name-up":
                    self.sort_choose.setCurrentText("Имя файла /\\")
                case "name-down":
                    self.sort_choose.setCurrentText("Имя файла \\/")
                case "made-up":
                    self.sort_choose.setCurrentText("Дата съёмки /\\")
                case "made-down":
                    self.sort_choose.setCurrentText("Дата съёмки \\/")
                case "add-up":
                    self.sort_choose.setCurrentText("Дата добавления /\\")
                case "add-down":
                    self.sort_choose.setCurrentText("Дата добавления \\/")
                case _:
                    self.sort_choose.setCurrentText("Имя файла /\\")

        try:
            with open('settings.json', 'r') as json_file:
                settings = json.load(json_file)
        except FileNotFoundError:
            win = ErrorsAndWarnings.SettingsReadError(self)
            win.show()
            return

        self.old_media_dir = settings['files']['destination_dir']
        self.old_thumb_dir = settings['files']['thumbs_dir']
        mode = settings['files']['transfer_mode']
        self.old_num_thumbs = settings['view']["thumbs_row"]
        self.old_theme_color = settings['view']["color_theme"]
        self.old_socnet_status = settings['view']["social_networks_status"]
        self.old_sort_type = settings['view']["sort_type"]
        show_sort_type(settings['view']["sort_type"])

        self.media_space_line.setText(self.old_media_dir)
        self.thumbs_space_line.setText(self.old_thumb_dir)
        self.transfer_mode_choose.setCurrentText(mode)
        self.num_thumbs_choose.setCurrentText(self.old_num_thumbs)
        self.theme_choose.setCurrentText(self.old_theme_color)

        if self.old_socnet_status:
            self.socnet_choose.setChecked(QtCore.Qt.Checked)
        else:
            self.socnet_choose.setChecked(QtCore.Qt.Unchecked)

        try:
            with open('hotkeys.json', 'r') as json_file:
                hotkeys = json.load(json_file)
        except FileNotFoundError:
            win = ErrorsAndWarnings.SettingsReadError(self)
            win.show()
            return

        self.open_file_enter.setText(hotkeys["open_file"])
        self.edit_metadata_enter.setText(hotkeys["edit_metadata"])
        self.open_explorer_enter.setText(hotkeys["open_explorer"])
        self.delete_file_enter.setText(hotkeys["delete_file"])
        self.do_any_enter.setText(hotkeys["show_stat_map"])

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
        def write_sort_type():
            match self.sort_choose.currentText():
                case "Имя файла /\\":
                    return "name-up"
                case "Имя файла \\/":
                    return "name-down"
                case "Дата съёмки /\\":
                    return "made-up"
                case "Дата съёмки \\/":
                    return "made-down"
                case "Дата добавления /\\":
                    return "add-up"
                case "Дата добавления \\/":
                    return "add-down"
                case _:
                    return "name-up"

        dir_media_chosen = self.media_space_line.text()
        dir_thumb_chosen = self.thumbs_space_line.text()
        transfer_mode = self.transfer_mode_choose.currentText()
        num_thumbs = self.num_thumbs_choose.currentText()
        theme_color = self.theme_choose.currentText()
        socnet_status = self.socnet_choose.checkState()
        sort_type = write_sort_type()

        jsondata_wr =   {
                            "files":
                                    {
                                    "destination_dir": dir_media_chosen,
                                    "thumbs_dir": dir_thumb_chosen,
                                    "transfer_mode": transfer_mode
                                    },
                            "view":
                                    {
                                    "thumbs_row": num_thumbs,
                                    "color_theme": theme_color,
                                    "social_networks_status": socnet_status,
                                    "sort_type": sort_type
                                    }
                            }

        with open('settings.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file, sort_keys=True, indent=4, separators=(',', ': '))

        logging.info(f"Settings - Settings changed - {jsondata_wr}")
        self.parent().stylesheet_color()

        notice_win = Notification(self)
        notice_win.show()

        if dir_thumb_chosen != self.old_thumb_dir or dir_media_chosen != self.old_media_dir or \
                num_thumbs != self.old_num_thumbs or theme_color != self.old_theme_color or \
                socnet_status != self.old_socnet_status or sort_type != self.old_sort_type:
            self.update_main_widget.emit()

        self.show_settings()

    # обновить собственный вид при изменении настроек вида
    def update_stylesheet(self) -> None:
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
        self.sort_type.setStyleSheet(stylesheet2)
        self.sort_choose.setStyleSheet(stylesheet9)
        self.logs_lbl.setStyleSheet(stylesheet2)
        self.logs_show.setStyleSheet(stylesheet1)
        self.logs_btn.setStyleSheet(stylesheet1)
        self.tabs.setStyleSheet(stylesheet7)

    # открыть папку с логами, 1 файл указывается в пути, чтобы открыть уже саму папку, а не рабочую папку программы с выделенной папкой "логи"
    def call_explorer_logs(self) -> None:
        path = os.getcwd() + r'\logs'
        file = os.listdir(path)[0]
        full_path = path + '\\' + file
        os.system(f'explorer /select,\"{full_path}\"')

    # очистка папки логов, лог сегодняшнего дня не очищается, так как используется самой программой во время работы
    def clear_logs(self) -> None:
        path = os.getcwd() + r'\logs'
        files = os.listdir(path)
        for file in files:
            try:
                os.remove(path + '\\' + file)
            except PermissionError:
                pass
        logging.info(f"Settings - Logs cleared")


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

        logging.info(f"Settings - Started files transfer to new directory")

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
    destination_media = settings['files']['destination_dir']
    return destination_media


# получить путь хранения миниатюр - для других модулей
def get_destination_thumb() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    destination_thumb = settings['files']['thumbs_dir']
    return destination_thumb


# количество миниатюр в строке
def get_thumbs_row() -> int:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    thumbs_row = int(settings['view']['thumbs_row'])
    return thumbs_row


# режим переноса фото при добавлении
def get_photo_transfer_mode() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    transfer_mode = settings['files']['transfer_mode']
    return transfer_mode


# выбранная визуальная тема
def get_theme_color() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    theme_color = settings['view']['color_theme']
    if theme_color == 'auto':
        import darkdetect
        theme_color = darkdetect.theme().lower()
    return theme_color


# включены или отключены соцсети
def get_socnet_status() -> int:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    socnet_status = int(settings['view']['social_networks_status'])
    return socnet_status


# сортировка фото в основном каталоге
def get_sort_type() -> str:
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)
    sort_type = settings['view']['sort_type']
    return sort_type


# горячие клавиши
def get_hotkeys() -> dict:
    try:
        with open('hotkeys.json', 'r') as json_file:
            hotkeys = json.load(json_file)
        return hotkeys
    except FileNotFoundError:
        hotkeys_default = {
                              "open_file": "Ctrl+S",
                              "edit_metadata": "Ctrl+E",
                              "open_explorer": "Ctrl+D",
                              "delete_file": "Del",
                              "show_stat_map": "Enter"
                          }

        with open('hotkeys.json', 'w') as json_file:
            json.dump(hotkeys_default, json_file, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingWin()
    win.show()
    sys.exit(app.exec_())
