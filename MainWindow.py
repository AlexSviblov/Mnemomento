import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *

import OnlyShowWidget
import ShowAloneWindowWidget
import ShowConstWindowWidget
import SocialNetworks
import Thumbnail
import ErNamesDB
import FilesDirs
import json
import os
from pathlib import Path
import ErrorsAndWarnings
import Settings
import RecoveryModule
import logging
import GlobalMap


stylesheet1 = str()
stylesheet2 = str()
stylesheet4 = str()
stylesheet5 = str()
stylesheet8 = str()
stylesheet10 = str()


font16 = QtGui.QFont('Times', 16)
font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)
font10 = QtGui.QFont('Times', 10)
font8 = QtGui.QFont('Times', 8)

logging.basicConfig(filename="logs.txt", format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.stylesheet_color()
        self.setStyleSheet(stylesheet2)

        self.setWindowTitle("ТЕСТ ПРОГРАММЫ")
        # Меньше невозможно сделать окно
        self.setMinimumSize(1366, 768)
        # раскрыть на весь экран
        self.showMaximized()

        self.menubar = QMenuBar(self)
        self.menubar.setFont(font8)
        self.menubar.setStyleSheet(stylesheet4)

        self.add_menu = self.menubar.addMenu('Добавить')
        self.add_menu.setStyleSheet(stylesheet10)

        add_const_files_bar = QAction('Добавить файлы в основной каталог', self)
        add_const_files_bar.triggered.connect(self.func_add_const_files)

        add_const_directory_bar = QAction('Добавить папку в основной каталог', self)
        add_const_directory_bar.triggered.connect(self.func_add_const_dir)

        add_const_alone_directory = QAction('Добавить папку в дополнительный каталог', self)
        add_const_alone_directory.triggered.connect(self.func_add_alone_dir) 

        self.add_menu.addAction(add_const_files_bar)
        self.add_menu.addAction(add_const_directory_bar)
        self.add_menu.addAction(add_const_alone_directory)

        self.view_menu = self.menubar.addMenu('Посмотреть')
        self.view_menu.setStyleSheet(stylesheet10)

        view_dir = QAction('Разовый просмотр папки', self)
        view_dir.triggered.connect(self.func_view_dir)

        view_files = QAction('Разовый просмотр файлов', self)
        view_files.triggered.connect(self.func_view_files)

        view_const_dir = QAction('Просмотр основного каталога', self)
        view_const_dir.triggered.connect(self.show_main_const_widget)

        view_alone_dir = QAction('Просмотр дополнительного каталога', self)
        view_alone_dir.triggered.connect(self.show_main_alone_widget)

        self.view_menu.addAction(view_dir)
        self.view_menu.addAction(view_files)
        self.view_menu.addAction(view_const_dir)
        self.view_menu.addAction(view_alone_dir)

        self.bases_menu = self.menubar.addMenu('Данные')
        self.bases_menu.setStyleSheet(stylesheet10)

        database_ernames_menu = QAction('Исправления метаданных', self)
        database_ernames_menu.triggered.connect(self.db_ernames_view_func)

        social_networks_menu = QAction('Социальные сети', self)
        social_networks_menu.triggered.connect(self.social_networks_func)

        self.bases_menu.addAction(database_ernames_menu)
        self.bases_menu.addAction(social_networks_menu)

        global_map = QAction('Карта', self)
        self.menubar.addAction(global_map)
        global_map.triggered.connect(self.show_global_map)

        settings_menu = QAction('Настройки', self)
        self.menubar.addAction(settings_menu)
        settings_menu.triggered.connect(self.settings_func)

        recovery = QAction('Восстановление', self)
        self.menubar.addAction(recovery)
        recovery.triggered.connect(self.recovery_func)

        self.setMenuBar(self.menubar)

        self.start_show()
        
    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet4
        global stylesheet5
        global stylesheet8
        global stylesheet10

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
            stylesheet4 =   """
                            QMenuBar 
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            }
                            QMenuBar::item::selected
                            {
                                color: #000000;
                                background-color: #C0C0C0
                            }
                            """
            stylesheet5 =   """
                            QProgressBar
                            {
                                border: 1px;
                                border-color: #000000;
                                border-style: solid;
                                background-color: #FFFFFF;
                                color: #000000
                            }
                            QProgressBar::chunk
                            {
                                background-color: #00FF7F;  
                            }
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
            stylesheet10 =  """
                            QMenu
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            }
                            QMenu::item::selected
                            {
                                border: 2px;
                                background-color: #C0C0C0;
                            }
                            """
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
            stylesheet4 =   """
                            QMenuBar 
                            {
                                border: 1px;
                                border-color: #696969;
                                border-style: solid;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            }
                            QMenuBar::item::selected
                            {
                                color: #D3D3D3;
                                background-color: #3F3F3F
                            }
                            """
            stylesheet5 =   """
                            QProgressBar
                            {
                                border: 1px;
                                border-color: #000000;
                                border-style: solid;
                                background-color: #CCCCCC;
                                color: #000000
                            }
                            QProgressBar::chunk
                            {
                                background-color: #1F7515;
                            }
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
            stylesheet10 =  """
                            QMenu
                            {
                                border: 1px;
                                border-color: #696969;
                                border-style: solid;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            }
                            QMenu::item::selected
                            {
                                border: 2px;
                                background-color: #2F2F2F;
                            }
                            """

        self.setStyleSheet(stylesheet2)
        try:
            self.menubar.setStyleSheet(stylesheet4)
            self.view_menu.setStyleSheet(stylesheet10)
            self.add_menu.setStyleSheet(stylesheet10)
            self.bases_menu.setStyleSheet(stylesheet10)
        except AttributeError:
            pass

    # добавить в основной каталог на постоянку файлы
    def func_add_const_files(self) -> None:
        self.add_files_chosen = QFileDialog.getOpenFileNames(self, 'Выбрать файлы', '.', "Image files (*.jpg *.png)")
        file_list = self.add_files_chosen[0]
        if not file_list:
            return

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.add_files_progress = ConstMaker(file_list=file_list)
        self.add_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.add_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.add_files_progress.finished.connect(lambda h: self.finish_thread_add_const(h))
        self.add_files_progress.start()

    # добавить в основной каталог на постоянку папку
    def func_add_const_dir(self) -> None:
        add_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')
        try:
            file_list = FilesDirs.make_files_list_from_dir(add_dir_chosen)
        except FileNotFoundError:
            return

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.add_files_progress = ConstMaker(file_list=file_list)
        self.add_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.add_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.add_files_progress.finished.connect(self.finish_thread_add_const)
        self.add_files_progress.start()

    # добавить в дополнительный каталог папку на постоянку
    def func_add_alone_dir(self) -> None:
        add_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')

        try:
            photo_files_list = FilesDirs.make_files_list_from_dir(add_dir_chosen)
        except FileNotFoundError:
            return

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.add_files_progress = AloneMaker(photo_directory=add_dir_chosen, photo_files_list=photo_files_list, mode="dir", exists_dir='')
        self.add_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.add_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.add_files_progress.finished.connect(lambda files: self.finish_thread_add_alone(files))
        self.add_files_progress.start()

    # добавить в основной каталог на постоянку файлы
    def func_add_alone_files(self, dir_to_add) -> None:
        self.add_files_chosen = QFileDialog.getOpenFileNames(self, 'Выбрать файлы', '.', "Image files (*.jpg *.png)")
        file_list = self.add_files_chosen[0]
        if not file_list:
            return
        path_splitted = file_list[0].split("/")
        photo_directory_buf =''
        for i in range(len(path_splitted) - 1):
            photo_directory_buf += path_splitted[i] + '/'
        photo_directory = photo_directory_buf[:-1]

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.add_files_progress = AloneMaker(photo_directory=photo_directory, photo_files_list=file_list, mode="files", exists_dir=dir_to_add)
        self.add_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.add_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.add_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.add_files_progress.finished.connect(lambda files: self.finish_thread_add_alone(files))
        self.add_files_progress.start()

    # одноразовый просмотр папки
    def func_view_dir(self) -> None:
        self.view_dir_chosen = QFileDialog.getExistingDirectory(self, 'Выбрать папку', '.')

        try:
            self.photo_files_list_view = FilesDirs.make_files_list_from_dir(self.view_dir_chosen)
        except FileNotFoundError:
            return

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.view_files_progress = TimeMaker(photo_files_list=self.photo_files_list_view)
        self.view_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.view_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.view_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.view_files_progress.finished.connect(self.finish_thread_view_dir)
        self.view_files_progress.start()

    # одноразовый просмотр файлов
    def func_view_files(self) -> None:
        self.view_files_chosen = QFileDialog.getOpenFileNames(self, 'Выбрать файлы', '.', "Image files (*.jpg *.png)")
        self.photo_files_list_view = self.view_files_chosen[0]

        if not self.photo_files_list_view:
            return

        self.progressbar = ProgressBar()
        self.setCentralWidget(self.progressbar)

        self.view_files_progress = TimeMaker(photo_files_list=self.photo_files_list_view)
        self.view_files_progress.preprogress.connect(lambda x: self.progressbar.progressbar_set_max(x))
        self.view_files_progress.progress.connect(lambda y: self.progressbar.progressbar_set_value(y))
        self.view_files_progress.info_text.connect(lambda t: self.progressbar.info_set_text(t))
        self.view_files_progress.finished.connect(self.finish_thread_view_dir)
        self.view_files_progress.start()

    # По окончании добавления файлов в основной каталог, запустить виджет его показа
    def finish_thread_add_const(self, files: list) -> None:
        # win = PhotoExistsWarning(self, files)
        if files:
            win = ErrorsAndWarnings.PhotoExists(self, files, "const")
            win.show()
        self.show_main_const_widget()
        self.add_files_progress = None

    # По окончании добавления файлов в дополнительный каталог, запустить виджет его показа
    def finish_thread_add_alone(self, files: str) -> None:
        if files[0] == 'finish':
            self.show_main_alone_widget()
        elif files[0] == "error":
            win = ErrorsAndWarnings.ExistAloneDir(self)
            win.show()
            self.start_show()
        else:
            win = ErrorsAndWarnings.PhotoExists(self, files, "alone")   # type: ignore[assignment]
            win.show()
            self.show_main_alone_widget()
        self.add_files_progress = None

    # По окончании создания миниатюр разового просмотра, запустить виджет показа
    def finish_thread_view_dir(self) -> None:
        self.show_view_dir()
        self.view_files_progress = None

    # Виджет показа основного каталога
    def show_main_const_widget(self) -> None:
        widget = ShowConstWindowWidget.ConstWidgetWindow()
        widget.set_minimum_size.connect(lambda w: self.setMinimumWidth(w))
        self.setCentralWidget(widget)

    # Виджет показа дополнительного каталога
    def show_main_alone_widget(self) -> None:
        widget = ShowAloneWindowWidget.AloneWidgetWindow()
        widget.set_minimum_size.connect(lambda w: self.setMinimumWidth(w))
        widget.add_photo_signal.connect(lambda t_dir: self.func_add_alone_files(t_dir))
        self.setCentralWidget(widget)

    # Показ папки вне каталогов
    def show_view_dir(self) -> None:
        widget = OnlyShowWidget.WidgetWindow(self.photo_files_list_view)
        widget.set_minimum_size.connect(lambda w: self.setMinimumWidth(w))
        self.setCentralWidget(widget)

    def show_global_map(self):
        widget = GlobalMap.GlobalMapWidget()
        self.setCentralWidget(widget)

    # Начальный вид
    def start_show(self) -> None:
        widget = StartShow()
        self.setCentralWidget(widget)
        widget.const_show_signal.connect(self.show_main_const_widget)
        widget.alone_show_signal.connect(self.show_main_alone_widget)
        widget.alone_add_dir_signal.connect(self.func_add_alone_dir)
        widget.const_add_files_signal.connect(self.func_add_const_files)
        widget.const_add_dir_signal.connect(self.func_add_const_dir)

    # Таблица с изменёнными именами
    def db_ernames_view_func(self) -> None:
        try:
            self.window_db = DB_window(self)
        except Exception:
            logging.exception(f"Error in {type(self)} - Cannot open ErrorNames.db")
            er_win = ErrorsAndWarnings.ErNamesDBErrorWin(self)
            er_win.show()
            return

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
            path = Settings.get_destination_media() + "/Media/Photo/const/"
            FilesDirs.clear_empty_dirs(path)
        except FileNotFoundError:
            pass

        try:
            Thumbnail.delete_exists()
            path = Settings.get_destination_thumb() + "/thumbnail/const/"
            FilesDirs.clear_empty_dirs(path)
        except FileNotFoundError:
            pass

    # соцсети
    def social_networks_func(self) -> None:
        self.window_sn = Social_Network_window(self)
        self.window_sn.resize(self.window_sn.size())
        self.window_sn.main_resize_signal.connect(self.resize_sn_window)
        self.window_sn.show()

    # Изменение размера окна таблицы при её редактировании
    def resize_sn_window(self) -> None:
        self.window_sn.resize(self.window_sn.size())
        self.window_sn.adjustSize()

    # настройки
    def settings_func(self) -> None:
        window_set = Settings.SettingWin(self)
        window_set.update_main_widget.connect(self.update_settings_widget)
        window_set.show()

    # восстановление
    def recovery_func(self) -> None:
        self.recovery_win = RecoveryModule.RecoveryWin(self)
        self.recovery_win.show()

    # после изменения в настройках надо обновить текущий виджет
    def update_settings_widget(self) -> None:
        self.stylesheet_color()
        if type(self.centralWidget()) == ShowAloneWindowWidget.AloneWidgetWindow:   #Alone

            chosen_dir = self.centralWidget().directory_choose.currentText()
            self.show_main_alone_widget()
            self.centralWidget().directory_choose.setCurrentText(chosen_dir)

        elif type(self.centralWidget()) == ShowConstWindowWidget.ConstWidgetWindow: #Const
            chosen_mode = self.centralWidget().group_type.currentText()
            if chosen_mode == 'Оборудование':
                chosen_camera = self.centralWidget().camera_choose.currentText()
                chosen_lens = self.centralWidget().lens_choose.currentText()
            elif chosen_mode == 'Соцсети':
                chosen_network = self.centralWidget().socnet_choose.currentText()
                chosen_status = self.centralWidget().sn_status.currentText()
            else: # 'Дата'
                chosen_year = self.centralWidget().date_year.currentText()
                chosen_month = self.centralWidget().date_month.currentText()
                chosen_day = self.centralWidget().date_day.currentText()

            self.show_main_const_widget()
            self.centralWidget().group_type.setCurrentText(chosen_mode)

            if chosen_mode == 'Оборудование':
                self.centralWidget().camera_choose.setCurrentText(chosen_camera)
                self.centralWidget().lens_choose.setCurrentText(chosen_lens)
            elif chosen_mode == 'Соцсети' and Settings.get_socnet_status():
                self.centralWidget().socnet_choose.setCurrentText(chosen_network)
                self.centralWidget().sn_status.setCurrentText(chosen_status)
            elif chosen_mode == 'Дата':
                self.centralWidget().date_year.setCurrentText(chosen_year)
                self.centralWidget().date_month.setCurrentText(chosen_month)
                self.centralWidget().date_day.setCurrentText(chosen_day)
            else:
                # Если были выбраны "Соцсети", но в настройках их отключили
                pass

        elif type(self.centralWidget()) == OnlyShowWidget.WidgetWindow:             #OnlyShow
            self.centralWidget().after_change_settings()
            self.centralWidget().stylesheet_color()
        elif type(self.centralWidget()) == StartShow:
            self.start_show()
        else:
            pass

        try:
            self.window_sn.setStyleSheet(stylesheet2)
            self.window_sn.centralWidget().stylesheet_color()
        except AttributeError:
            pass
        try:
            self.window_db.setStyleSheet(stylesheet2)
            self.window_db.centralWidget().stylesheet_color()
        except AttributeError:
            pass
        try:
            self.recovery_win.stylesheet_color()
        except AttributeError:
            pass


# при добавлении папки
# noinspection PyArgumentList
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
        self.title_text.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_text, 1, 1, 1, 1)

        self.progressbar = QProgressBar()
        self.progressbar.setFixedWidth(int(self.width()/2))
        self.progressbar.setFont(font16)
        self.progressbar.setStyleSheet(stylesheet5)
        self.progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.progressbar, 2, 1, 1, 1)

        self.transfer_info = QLabel(self)
        self.transfer_info.setFont(font10)
        self.transfer_info.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.transfer_info, 3, 0, 1, 3)

    def progressbar_set_max(self, max: int) -> None:
        self.progressbar.setMaximum(max)

    def progressbar_set_value(self, value: int) -> None:
        self.progressbar.setValue(value)

    def info_set_text(self, text: str) -> None:
        self.transfer_info.setText(f"{text}")


# стартовое окно, при запуске программы
# noinspection PyArgumentList
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
        self.btn_const_cat.setStyleSheet(stylesheet8)
        self.btn_alone_cat.setStyleSheet(stylesheet8)
        self.btn_const_add_dir.setStyleSheet(stylesheet8)
        self.btn_const_add_files.setStyleSheet(stylesheet8)
        self.btn_alone_add_dir.setStyleSheet(stylesheet8)

        self.layout_last = QGridLayout(self)
        self.last_photo = QLabel()
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
        self.group_last.setStyleSheet(stylesheet2)
        self.layout_outside.addWidget(self.group_last, 1, 2, 1, 1)

        try:
            with open('last_opened.json', 'r') as json_file:
                photofile = json.load(json_file)['last_opened_photo']
            pixmap = QtGui.QPixmap(photofile)
            pixmap2 = pixmap.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
            self.last_photo.setPixmap(pixmap2)
        except FileNotFoundError:
            self.last_photo.setText("Фото было перемещено или удалено")

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
        try:
            size, numfiles, fullnum = self.fill_dir_stats(Settings.get_destination_media() + '/Media/Photo/const/')
        except:
            self.const_stats.setText(str_to_show)
            return

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
        try:
            size, numfiles, fullnum = self.fill_dir_stats(Settings.get_destination_media() + '/Media/Photo/alone/')
        except Exception:
            self.alone_stats.setText(str_to_show)
            return
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
# noinspection PyArgumentList
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

    def self_resize(self) -> None:
        self.resize(self.widget_sn.size())
        self.main_resize_signal.emit()


# добавление в основной каталог
# noinspection PyUnresolvedReferences
class ConstMaker(QtCore.QThread):
    info_text = pyqtSignal(str)
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
            self.info_text.emit(f"Идёт обработка файла {file}")
            fileexists = FilesDirs.transfer_const_photos(file)
            j += 1
            self.progress.emit(round(100*(j/self.len_file_list)))
            self.info_text.emit(f"Обработка файла {file} завершена")
            if fileexists:
                files_exist.append(fileexists)
                self.info_text.emit(f"Файл {file} уже существует")
            else:
                pass

        if Settings.get_photo_transfer_mode() == "cut":
            self.info_text.emit(f"Определение статуса папки")
            file_dir = ''
            file_full = self.files_list[0].split(r'/')
            for i in range(len(file_full) - 1):
                file_dir += file_full[i] + '/'
            if not os.listdir(file_dir):
                os.rmdir(file_dir)
                self.info_text.emit(f"Опустевшая папка {file_dir} удалена")
            else:
                self.info_text.emit(f"Папка {file_dir} не была удалена, так как не опустела")

        self.finished.emit(files_exist)


# добавление в дополнительный каталог
# noinspection PyUnresolvedReferences
class AloneMaker(QtCore.QThread):
    info_text = pyqtSignal(str)
    preprogress = pyqtSignal(int)
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, photo_directory, photo_files_list, mode, exists_dir):
        QThread.__init__(self)

        self._init = False

        self.photo_directory = photo_directory

        self.files_list = photo_files_list

        self.mode = mode
        self.exists_dir = exists_dir

        self.len_file_list = len(photo_files_list)
        self.preprogress.emit(self.len_file_list)

    def run(self):
        if not os.path.isdir(Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1]) and self.mode == "dir":
            self.info_text.emit(f"Создание директории {self.photo_directory.split('/')[-1]} в программе")
            os.mkdir(Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1])

            j = 0
            for file in self.files_list:
                self.info_text.emit(f"Идёт обработка файла {file}")
                FilesDirs.transfer_alone_photos(self.photo_directory, file)
                j += 1
                self.progress.emit(round(100 * (j / self.len_file_list)))
                self.info_text.emit(f"Обработка файла {file} завершена")

            if Settings.get_photo_transfer_mode() == "cut":
                self.info_text.emit(f"Определение статуса папки")
                if not os.listdir(self.photo_directory):
                    self.info_text.emit(f"Опустевшая папка {self.photo_directory} удалена")
                    os.rmdir(self.photo_directory)
                else:
                    self.info_text.emit(f"Папка {self.photo_directory} не была удалена")

            self.finished.emit(['finish'])

        elif os.path.isdir(Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1]) and self.mode == "dir":
            self.finished.emit(['error'])
        else: # self.mode == "files"
            j = 0
            file_exists = []
            for file in self.files_list:
                self.info_text.emit(f"Идёт обработка файла {file}")
                desination_dir = Settings.get_destination_media() + '/Media/Photo/alone/' + self.photo_directory.split('/')[-1]
                file_name = file.split('/')[-1]
                if os.path.exists(desination_dir + '/' + file_name):
                    file_exists.append(file)
                else:
                    FilesDirs.transfer_alone_photos(self.photo_directory, file, exists_dir_name=self.exists_dir, type_add='files')
                j += 1
                self.progress.emit(round(100 * (j / self.len_file_list)))
                self.info_text.emit(f"Обработка файла {file} завершена")
            if file_exists:
                self.finished.emit(file_exists)
            else:
                self.finished.emit(['finish'])


# создание временных файлов для разового просмотра
class TimeMaker(QtCore.QThread):
    info_text = pyqtSignal(str)
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
            self.info_text.emit(f"Идёт обработка файла {file}")
            Thumbnail.make_thumbnails_view(file)
            self.info_text.emit(f"Обработка файла {file} завершена")
            j += 1
            self.progress.emit(round(100 * (j / self.len_file_list)))

        self.finished.emit('finish')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    do = 0
    with open('settings.json', 'r') as json_file:
        settings = json.load(json_file)

        if os.path.isdir(settings["destination_dir"]) and os.path.isdir(settings["thumbs_dir"]):
            pass
        else:
            do = 1
    if do:
        with open('settings.json', 'w') as json_file:
            bsl = '\\'
            new_set = {"destination_dir": f"{os.getcwd().replace(bsl, '/')}", "thumbs_dir": f"{os.getcwd().replace(bsl, '/')}", "transfer_mode": "copy", "thumbs_row": "2", "color_theme": "light", "social_networks_status": 2}
            json.dump(new_set, json_file)

    try:
        win = MainWindow()
        win.show()
    except:
        logging.exception(f"ALL PROGRAM ERROR")

    sys.exit(app.exec_())
