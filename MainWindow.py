import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *

import OnlyShowWidget
import ShowAloneWindowWidget
import ShowConstWindowWidget
import SocialNetworks
import Thumbnail
import Screenconfig
import ErNamesDB
import FilesDirs
import json
import os
from pathlib import Path
import ErrorsAndWarnings
import Settings


font16 = QtGui.QFont('Times', 16)
font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)
font10 = QtGui.QFont('Times', 10)
font8 = QtGui.QFont('Times', 8)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.stylesheet_color()

        self.setWindowTitle("ТЕСТ ПРОГРАММЫ")
        # Меньше невозможно сделать окно
        self.setMinimumSize(1280, 720)
        # раскрыть на весь экран
        self.showMaximized()

        self.setStyleSheet(stylesheet2)

        self.menubar = QMenuBar(self)
        self.menubar.setFont(font8)
        self.menubar.setStyleSheet(stylesheet1)

        add_menu = self.menubar.addMenu('Добавить')

        add_const_files_bar = QAction('Добавить файлы в общий каталог', self)
        add_const_files_bar.triggered.connect(self.func_add_const_files)

        add_const_directory_bar = QAction('Добавить папку в общий каталог', self)
        add_const_directory_bar.triggered.connect(self.func_add_const_dir)

        add_const_alone_directory = QAction('Добавить папку в дополнительный каталог', self)
        add_const_alone_directory.triggered.connect(self.func_add_alone_dir) 

        add_menu.addAction(add_const_files_bar)
        add_menu.addAction(add_const_directory_bar)
        add_menu.addAction(add_const_alone_directory)

        view_menu = self.menubar.addMenu('Посмотреть')

        view_dir = QAction('Просмотр папки', self)
        view_dir.triggered.connect(self.func_view_dir)

        view_files = QAction('Просмотр файлов', self)
        view_files.triggered.connect(self.func_view_files)

        view_const_dir = QAction('Просмотр основного каталога', self)
        view_const_dir.triggered.connect(self.show_main_const_widget)

        view_alone_dir = QAction('Просмотр дополнительного каталога', self)
        view_alone_dir.triggered.connect(self.show_main_alone_widget)

        view_menu.addAction(view_dir)
        view_menu.addAction(view_files)
        view_menu.addAction(view_const_dir)
        view_menu.addAction(view_alone_dir)

        database_ernames_menu = QAction('База исправлений', self)
        self.menubar.addAction(database_ernames_menu)
        database_ernames_menu.triggered.connect(self.db_ernames_view_func)

        social_networks_menu = QAction('Соц.сети', self)
        self.menubar.addAction(social_networks_menu)
        social_networks_menu.triggered.connect(self.social_networks_func)

        settings = QAction('Настройки', self)
        self.menubar.addAction(settings)
        settings.triggered.connect(self.settings_func)

        self.setMenuBar(self.menubar)

        self.start_show()
        
    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet5
        global stylesheet6
        if Settings.get_theme_color() == 'light':
            stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0"
            stylesheet2 = "border: 0px; color: #000000; background-color: #F0F0F0"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}"
            stylesheet5 = "QProgressBar{border: 1px; border-color: #000000; border-style: solid; background-color: #FFFFFF; color: #000000} QProgressBar::chunk {background-color: #00FF7F; }"
            stylesheet6 = "QTableView{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;gridline-color: #A9A9A9;}"
        else:
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #080808"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #080808"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #696969; border-style: solid; background-color: #080808; color: #D3D3D3;}"
            stylesheet5 = "QProgressBar{border: 1px; border-color: #000000; border-style: solid; background-color: #FFFFFF; color: #000000} QProgressBar::chunk {background-color: #00FF7F; }"
            stylesheet6 = "QTableView{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #080808; gridline-color: #696969;}"

        self.setStyleSheet(stylesheet2)
        try:
            self.menubar.setStyleSheet(stylesheet1)
        except AttributeError:
            pass

    # добавить в основной каталог на постоянку файлы
    def func_add_const_files(self) -> None:
        self.add_files_chosen = QFileDialog.getOpenFileNames(self, 'Выбрать файлы', '.', "Image files (*.jpg *.png)")
        self.file_list = self.add_files_chosen[0]
        if not self.file_list:
            return

        progressbar = ProgressBar()
        self.setCentralWidget(progressbar)

        self.add_files_progress = ConstMaker(file_list=self.file_list)
        self.add_files_progress.preprogress.connect(lambda x: progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: progressbar.progressbar_set_value(y))
        self.add_files_progress.finished.connect(lambda h: self.finish_thread_add_const(h))
        self.add_files_progress.start()

    # добавить в основной каталог на постоянку папку
    def func_add_const_dir(self) -> None:

        self.add_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')
        try:
            self.file_list = FilesDirs.make_files_list_from_dir(self.add_dir_chosen)
        except FileNotFoundError:
            return

        progressbar = ProgressBar()
        self.setCentralWidget(progressbar)

        self.add_dir_progress = ConstMaker(file_list=self.file_list)
        self.add_dir_progress.preprogress.connect(lambda x: progressbar.progressbar_set_max(x))
        self.add_dir_progress.progress.connect(lambda y: progressbar.progressbar_set_value(y))
        self.add_dir_progress.finished.connect(self.finish_thread_add_const)
        self.add_dir_progress.start()

    # добавить в особый каталог папку на постоянку
    def func_add_alone_dir(self) -> None:
        self.add_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')

        try:
            photo_files_list = FilesDirs.make_files_list_from_dir(self.add_dir_chosen)
        except FileNotFoundError:
            return

        progressbar = ProgressBar()
        self.setCentralWidget(progressbar)

        self.add_files_progress = AloneMaker(photo_directory=self.add_dir_chosen, photo_files_list=photo_files_list)
        self.add_files_progress.preprogress.connect(lambda x: progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: progressbar.progressbar_set_value(y))
        self.add_files_progress.finished.connect(lambda text: self.finish_thread_add_alone(text))
        self.add_files_progress.start()

    # одноразовый просмотр папки
    def func_view_dir(self) -> None:
        self.view_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')

        try:
            self.photo_files_list = FilesDirs.make_files_list_from_dir(self.view_dir_chosen)
        except FileNotFoundError:
            return

        progressbar = ProgressBar()
        self.setCentralWidget(progressbar)

        self.view_files_progress = TimeMaker(photo_files_list=self.photo_files_list)
        self.view_files_progress.preprogress.connect(lambda x: progressbar.progressbar_set_max(x))
        self.view_files_progress.progress.connect(lambda y: progressbar.progressbar_set_value(y))
        self.view_files_progress.finished.connect(self.finish_thread_view_dir)
        self.view_files_progress.start()

    # одноразовый просмотр файлов
    def func_view_files(self) -> None:
        self.view_files_chosen = QFileDialog.getOpenFileNames(self, 'Выбрать файлы', '.', "Image files (*.jpg *.png)")
        self.photo_files_list = self.view_files_chosen[0]
        if not self.photo_files_list:
            return

        progressbar = ProgressBar()
        self.setCentralWidget(progressbar)

        self.view_files_progress = TimeMaker(photo_files_list=self.photo_files_list)
        self.view_files_progress.preprogress.connect(lambda x: progressbar.progressbar_set_max(x))
        self.view_files_progress.progress.connect(lambda y: progressbar.progressbar_set_value(y))
        self.view_files_progress.finished.connect(self.finish_thread_view_dir)
        self.view_files_progress.start()

    # По окончании добавления файлов в основной каталог, запустить виджет его показа
    def finish_thread_add_const(self, files: list) -> None:
        # win = PhotoExistsWarning(self, files)
        if files:
            win = ErrorsAndWarnings.PhotoExists(self, files)
            win.show()
        self.show_main_const_widget()

    # По окончании добавления файлов в дополнительный каталог, запустить виджет его показа
    def finish_thread_add_alone(self, text: str) -> None:
        if text == 'finish':
            self.show_main_alone_widget()
        else:
            self.start_show()
            er_win = ErrorsAndWarnings.ExistAloneDir(self)
            er_win.show()

    # По окончании создания миниатюр разового просмотра, запустить виджет показа
    def finish_thread_view_dir(self) -> None:
        self.show_view_dir()

    # Виджет показа основного каталога
    def show_main_const_widget(self) -> None:
        self.widget = ShowConstWindowWidget.ConstWidgetWindow()
        self.widget.set_minimum_size.connect(lambda w: self.setMinimumWidth(w))
        self.setCentralWidget(self.widget)

    # Виджет показа дополнительного каталога
    def show_main_alone_widget(self) -> None:
        self.widget = ShowAloneWindowWidget.AloneWidgetWindow()
        self.widget.set_minimum_size.connect(lambda w: self.setMinimumWidth(w))
        self.setCentralWidget(self.widget)

    # Показ папки вне каталогов
    def show_view_dir(self) -> None:
        self.widget = OnlyShowWidget.WidgetWindow(self.photo_files_list)
        self.setCentralWidget(self.widget)

    # Начальный вид
    def start_show(self) -> None:
        self.widget = StartShow()
        self.setCentralWidget(self.widget)
        self.widget.const_show_signal.connect(self.show_main_const_widget)
        self.widget.alone_show_signal.connect(self.show_main_alone_widget)
        self.widget.alone_add_dir_signal.connect(self.func_add_alone_dir)
        self.widget.const_add_files_signal.connect(self.func_add_const_files)
        self.widget.const_add_dir_signal.connect(self.func_add_const_dir)

    # Таблица с изменёнными именами
    def db_ernames_view_func(self) -> None:
        self.window_db = DB_window(self)
        self.window_db.resize(self.window_db.size())
        self.window_db.main_resize_signal.connect(self.resize_db_window)
        self.window_db.show()

    # Изменение размера окна таблицы при её редактировании
    def resize_db_window(self) -> None:
        self.window_db.resize(self.window_db.size())
        self.window_db.adjustSize()

    # закрытие программы -> удалить созданное для разового просмотра
    def closeEvent(self, event) -> None:
        self.clear_view_close()

    # удалить созданное для разового просмотра
    def clear_view_close(self) -> None:
        try:
            Thumbnail.delete_exists()
        except FileNotFoundError:
            pass

    # соцсети
    def social_networks_func(self) -> None:
        self.window_sn = Social_Network_window(self)
        self.window_sn.resize(self.window_sn.size())
        self.window_sn.main_resize_signal.connect(self.resize_sn_window)
        self.window_sn.show()

    # Изменение размера окна таблицы при её редактировании
    def resize_sn_window(self):
        self.window_sn.resize(self.window_sn.size())
        self.window_sn.adjustSize()

    # настройки
    def settings_func(self) -> None:
        window_set = Settings.SettingWin(self)
        window_set.update_main_widget.connect(self.update_settings_widget)
        window_set.show()

    # после изменения в настройках надо обновить текущий виджет
    def update_settings_widget(self):
        self.stylesheet_color()
        if type(self.centralWidget()) == ShowAloneWindowWidget.AloneWidgetWindow:   #Alone
            self.centralWidget().after_change_settings()
            self.centralWidget().stylesheet_color()
        elif type(self.centralWidget()) == ShowConstWindowWidget.ConstWidgetWindow: #Const
            self.centralWidget().after_change_settings()
            self.centralWidget().stylesheet_color()
        elif type(self.centralWidget()) == OnlyShowWidget.WidgetWindow:             #OnlyShow
            print('OnlyShow')
        elif type(self.centralWidget()) == StartShow:
            self.start_show()
        else:
            print('Other')


# при добавлении папки
class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.layout.setSpacing(0)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.title_text = QLabel(self)
        self.title_text.setText('Процесс обработки файлов')
        self.title_text.setFont(font16)
        self.title_text.setFixedWidth(400)
        self.title_text.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_text, 1, 1, 1, 1)

        self.progressbar = QProgressBar()
        self.progressbar.setFixedWidth(400)
        self.progressbar.setFont(font16)
        self.progressbar.setStyleSheet(stylesheet5)
        self.progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.progressbar, 2, 1, 1, 1)

        self.empty1 = QLabel(self)
        self.empty1.setFixedSize(300, 300)
        self.layout.addWidget(self.empty1, 0, 0, 1, 1)

        self.empty2 = QLabel(self)
        self.empty2.setFixedSize(300, 300)
        self.layout.addWidget(self.empty1, 0, 2, 1, 1)

        self.empty3 = QLabel(self)
        self.empty3.setMinimumSize(200, 200)
        self.layout.addWidget(self.empty1, 3, 0, 1, 1)

        self.empty4 = QLabel(self)
        self.empty4.setMinimumSize(200, 200)
        self.layout.addWidget(self.empty1, 3, 2, 1, 1)

    def progressbar_set_max(self, max):
        self.progressbar.setMaximum(max)

    def progressbar_set_value(self, value):
        self.progressbar.setValue(value)


# стартовое окно, при запуске программы
class StartShow(QWidget):

    const_show_signal = QtCore.pyqtSignal()
    alone_show_signal = QtCore.pyqtSignal()
    const_add_dir_signal = QtCore.pyqtSignal()
    const_add_files_signal = QtCore.pyqtSignal()
    alone_add_dir_signal = QtCore.pyqtSignal()

    def __init__(self):

        super().__init__()
        self.setWindowTitle("TEST")

        self.layout_outside = QGridLayout(self)

        font16 = QtGui.QFont('Times', 16)
        font14 = QtGui.QFont('Times', 14)
        font12 = QtGui.QFont('Times', 12)
        font10 = QtGui.QFont('Times', 10)


        self.layout_buttons = QGridLayout(self)

        self.empty1 = QLabel()
        self.empty1.setMinimumSize(5, 5)
        self.empty1.setMaximumSize(400, 400)
        self.layout_outside.addWidget(self.empty1, 0, 0, 1, 1)

        self.empty2 = QLabel()
        self.empty2.setMinimumSize(5, 5)
        self.empty2.setMaximumSize(400, 400)
        self.layout_outside.addWidget(self.empty2, 0, 3, 1, 1)

        self.empty3 = QLabel()
        self.empty3.setMinimumSize(5, 5)
        self.empty3.setMaximumSize(400, 400)
        self.layout_outside.addWidget(self.empty3, 3, 0, 1, 1)

        self.empty4 = QLabel()
        self.empty4.setMinimumSize(5, 5)
        self.empty4.setMaximumSize(400, 400)
        self.layout_outside.addWidget(self.empty4, 3, 3, 1, 1)

        self.btn_const_cat = QPushButton(self)
        self.btn_const_cat.setText('Основной каталог')
        self.btn_const_cat.setFont(font16)
        self.layout_buttons.addWidget(self.btn_const_cat, 0, 0, 1, 2)

        self.btn_alone_cat = QPushButton(self)
        self.btn_alone_cat.setText('Дополнительный каталог')
        self.btn_alone_cat.setFont(font14)
        self.layout_buttons.addWidget(self.btn_alone_cat, 0, 2, 1, 1)

        self.btn_const_add_dir = QPushButton(self)
        self.btn_const_add_dir.setText('Добавить папку')
        self.btn_const_add_dir.setFont(font12)
        self.layout_buttons.addWidget(self.btn_const_add_dir, 1, 0, 1, 1)

        self.btn_const_add_files = QPushButton(self)
        self.btn_const_add_files.setText('Добавить файлы')
        self.btn_const_add_files.setFont(font12)
        self.layout_buttons.addWidget(self.btn_const_add_files, 1, 1, 1, 1)

        self.btn_alone_add_dir = QPushButton(self)
        self.btn_alone_add_dir.setText('Добавить отдельную папку')
        self.btn_alone_add_dir.setFont(font10)

        self.layout_buttons.addWidget(self.btn_alone_add_dir, 1, 2, 1, 1)

        self.alone_stats = QLabel(self)
        self.layout_buttons.addWidget(self.alone_stats, 2, 2, 1, 1)
        self.fill_alone_stats()
        self.alone_stats.setAlignment(QtCore.Qt.AlignTop)

        self.const_stats = QLabel(self)
        self.fill_const_stats()
        self.const_stats.setAlignment(QtCore.Qt.AlignTop)
        self.layout_buttons.addWidget(self.const_stats, 2, 0, 1, 2)

        self.group_buttons = QGroupBox(self)
        self.group_buttons.setLayout(self.layout_buttons)
        self.layout_outside.addWidget(self.group_buttons, 1, 1, 1, 1)
        self.empty1.setStyleSheet(stylesheet2)
        self.empty2.setStyleSheet(stylesheet2)
        self.empty3.setStyleSheet(stylesheet2)
        self.empty4.setStyleSheet(stylesheet2)
        self.group_buttons.setStyleSheet(stylesheet2)
        self.btn_const_cat.setStyleSheet(stylesheet1)
        self.btn_alone_cat.setStyleSheet(stylesheet1)
        self.btn_const_add_dir.setStyleSheet(stylesheet1)
        self.btn_const_add_files.setStyleSheet(stylesheet1)
        self.btn_alone_add_dir.setStyleSheet(stylesheet1)

        self.layout_last = QGridLayout(self)
        with open('last_opened.json', 'r') as json_file:
            photofile = json.load(json_file)['last_opened_photo']
        try:
            self.last_photo = QLabel()
            pixmap = QtGui.QPixmap(photofile)
            pixmap2 = pixmap.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
            self.last_photo.setPixmap(pixmap2)
            self.last_photo.setAlignment(QtCore.Qt.AlignTop)
            self.layout_last.addWidget(self.last_photo, 1, 0, 1, 1)
            self.last_text = QLabel()
            self.last_text.setText('Последнее просмотренное фото:\n')
            self.last_text.setFont(font12)
            self.last_text.setFixedHeight(20)
            self.last_text.setAlignment(QtCore.Qt.AlignTop)
            self.layout_last.addWidget(self.last_text, 0, 0, 1, 1)

            self.group_last = QGroupBox(self)
            self.group_last.setFixedWidth(430)
            self.group_last.setLayout(self.layout_last)
            self.group_last.setStyleSheet("border:0;")
            self.layout_outside.addWidget(self.group_last, 1, 2, 1, 1)
        except FileNotFoundError:
            pass

        self.btn_const_cat.setMinimumSize(400, 80)
        self.btn_alone_cat.setMinimumSize(300, 80)

        self.btn_const_cat.clicked.connect(lambda: self.const_show_signal.emit())
        self.btn_alone_cat.clicked.connect(lambda: self.alone_show_signal.emit())
        self.btn_alone_add_dir.clicked.connect(lambda: self.alone_add_dir_signal.emit())
        self.btn_const_add_files.clicked.connect(lambda: self.const_add_files_signal.emit())
        self.btn_const_add_dir.clicked.connect(lambda: self.const_add_dir_signal.emit())

    # Собрать и вывести статистику основного каталога
    def fill_const_stats(self) -> None:
        str_to_show = ''
        size, numfiles, fullnum = self.fill_dir_stats(Settings.get_destination_media() + '/Media/Photo/const/')
        if size < 1024:
            str_size = f'Объём основного каталога: {round(size, 3)} байт\n'
        elif size < 1024**2:
            str_size = f'Объём основного каталога: {round(size/1024, 3)} килобайт\n'
        elif size < 1024**3:
            str_size = f'Объём основного каталога: {round(size/(1024**2), 3)} мегабайт\n'
        else:
            str_size = f'Объём основного каталога: {round(size / (1024 ** 3), 3)} гигабайт\n'
        str_to_show += str_size
        str_numfiles = f'Фотографий в основном каталоге: {numfiles}\n'
        str_to_show += str_numfiles

        self.const_stats.setText(str_to_show)
        self.const_stats.setFont(font12)

    # Собрать и вывести статистику дополнительного каталога
    def fill_alone_stats(self) -> None:
        str_to_show = ''
        size, numfiles, fullnum = self.fill_dir_stats(Settings.get_destination_media() + '/Media/Photo/alone/')
        numdir = fullnum - numfiles
        if size < 1024:
            str_size = f'Объём дополнительного каталога: {round(size, 3)} байт\n'
        elif size < 1024**2:
            str_size = f'Объём дополнительного каталога: {round(size/1024, 3)} килобайт\n'
        elif size < 1024**3:
            str_size = f'Объём дополнительного каталога: {round(size/(1024**2), 3)} мегабайт\n'
        else:
            str_size = f'Объём дополнительного каталога: {round(size/(1024**3), 3)} гигабайт\n'

        str_to_show += str_size

        str_numfiles = f'Фотографий в дополнительном каталоге: {numfiles}\n'
        str_to_show += str_numfiles
        str_numdirs = f'Папок в дополнительном каталоге: {numdir}\n'
        str_to_show += str_numdirs
        self.alone_stats.setText(str_to_show)
        self.alone_stats.setFont(font10)

    # получить данные о занятой памяти, количестве файлов и файлов + подпапок
    def fill_dir_stats(self, path: str) -> tuple[int, int, int]:
        fsize = 0
        numfile = 0
        iteration = 0
        for file in Path(path).rglob('*'):
            if (os.path.isfile(file)):
                fsize += os.path.getsize(file)
                numfile += 1
            iteration += 1
        return fsize, numfile, iteration


# окно просмотра базы неверных имён
class DB_window(QMainWindow):
    main_resize_signal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet(stylesheet2)
        self.setWindowTitle("База исправлений")
        self.widget_db = ErNamesDB.ViewBDDialog(self)
        self.setCentralWidget(self.widget_db)

        self.resize(self.widget_db.size())
        self.widget_db.resized_signal.connect(self.self_resize)

    def self_resize(self) -> None:
        self.resize(self.widget_db.size())
        self.main_resize_signal.emit()


# просмотр окна соцсетей
class Social_Network_window(QMainWindow):
    main_resize_signal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Соц.сети")
        self.widget_sn = SocialNetworks.SocialNetworks(self)
        self.setCentralWidget(self.widget_sn)
        self.setStyleSheet(stylesheet2)

        self.resize(self.widget_sn.size())
        self.widget_sn.resize_signal.connect(self.self_resize)

    def self_resize(self):
        self.resize(self.widget_sn.size())
        self.main_resize_signal.emit()


# добавление в основной каталог
class ConstMaker(QtCore.QThread):

    preprogress = pyqtSignal(int)
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, file_list):
        QThread.__init__(self)

        self._init = False

        self.files_list = file_list

        self.len_file_list = len(file_list)
        self.preprogress.emit(self.len_file_list)

    def run(self):
        j = 0
        files_exist = list()
        for file in self.files_list:
            fileexists = FilesDirs.transfer_const_photos(file)
            j += 1
            self.progress.emit(round(100*(j/self.len_file_list)))
            if fileexists:
                files_exist.append(fileexists)
            else:
                pass

        if Settings.get_photo_transfer_mode() == "cut":
            file_dir = ''
            file_full = self.files_list[0].split(r'/')
            for i in range(len(file_full) - 1):
                file_dir += file_full[i] + '/'
            if not os.listdir(file_dir):
                os.rmdir(file_dir)

        self.finished.emit(files_exist)


# добавление в дополнительный каталог
class AloneMaker(QtCore.QThread):

    preprogress = pyqtSignal(int)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, photo_directory, photo_files_list):
        QThread.__init__(self)

        self._init = False

        self.photo_directory = photo_directory

        self.files_list = photo_files_list

        self.len_file_list = len(photo_files_list)
        self.preprogress.emit(self.len_file_list)

    def run(self):
        if not os.path.isdir(Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1]):
            os.mkdir(Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1])

            j = 0
            for file in self.files_list:
                FilesDirs.transfer_alone_photos(self.photo_directory, file)
                j += 1
                self.progress.emit(round(100 * (j / self.len_file_list)))

            if Settings.get_photo_transfer_mode() == "cut":
                if not os.listdir(self.photo_directory):
                    os.rmdir(self.photo_directory)

            self.finished.emit('finish')
        else:
            self.finished.emit('error')


# создание временных файлов для разового просмотра
class TimeMaker(QtCore.QThread):

    preprogress = pyqtSignal(int)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, photo_files_list):
        QThread.__init__(self)

        self._init = False

        self.files_list = photo_files_list

        self.len_file_list = len(photo_files_list)
        self.preprogress.emit(self.len_file_list)

    def run(self):
        Thumbnail.delete_exists()
        j = 0
        for file in self.files_list:
            Thumbnail.make_thumbnails_view(file)
            j += 1
            self.progress.emit(round(100 * (j / self.len_file_list)))

        self.finished.emit('finish')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
