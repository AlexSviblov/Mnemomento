import logging
import sys
import os
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pathlib import Path
import shutil
import json
import ErrorsAndWarnings
import PhotoDataDB
import Screenconfig
import Metadata
import Settings
import Thumbnail
import SocialNetworks
import math
import EditFiles


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()
icon_explorer = str()
icon_view = str()
icon_edit = str()
icon_delete = str()


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


class ConstWidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.stylesheet_color()

        self.own_dir = os.getcwd()
        resolution = Screenconfig.monitor_info()
        self.monitor_width = resolution[0]
        self.monitor_height = resolution[1]

        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.setWindowTitle("Тестовое окно")

        self.layoutoutside = QGridLayout(self)
        self.layoutoutside.setSpacing(10)

        self.layout_type = QGridLayout(self)
        self.layout_type.setHorizontalSpacing(5)
        self.layout_type.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.pic = QtWidgets.QLabel()  # создание объекта большой картинки
        self.pic.hide()
        self.pic.setAlignment(Qt.AlignCenter)

        self.layout_inside_thumbs = QGridLayout(self)  # создание внутреннего слоя для подвижной области
        self.groupbox_thumbs = QGroupBox(self)  # создание группы объектов для помещения в него кнопок
        self.groupbox_thumbs.setStyleSheet(stylesheet1)
        self.groupbox_thumbs.setLayout(self.layout_inside_thumbs)

        self.scroll_area = QScrollArea(self)  # создание подвижной области
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.groupbox_thumbs)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(stylesheet2)

        self.layoutoutside.addWidget(self.scroll_area, 1, 0, 2, 2)  # помещение подвижной области на слой
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)  # задание размеров подвижной области и её внутренностей
        self.scroll_area.setFixedWidth(200*self.thumb_row)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(50)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.groupbox_sort, 0, 1, 1, 3)

        self.fill_sort_groupbox()
        self.fill_sort_date()
        self.groupbox_sort.setLayout(self.layout_type)

        self.date_show_thumbnails()

        self.metadata_show = QtWidgets.QTableWidget()
        self.metadata_show.setColumnCount(2)
        self.metadata_show.setFont(font14)
        self.metadata_show.setStyleSheet(stylesheet6)

        self.metadata_show.horizontalHeader().setVisible(False)
        self.metadata_show.verticalHeader().setVisible(False)

        self.metadata_header = self.metadata_show.horizontalHeader()
        self.metadata_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.metadata_show.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setDisabled(True)
        self.metadata_show.hide()

        self.last_clicked = ''

        self.resized_signal.connect(self.resize_func)
        self.oldsize = QtCore.QSize(0, 0)

        self.layout_btns = QGridLayout(self)
        self.layout_btns.setSpacing(0)

        self.make_buttons()
        self.groupbox_btns = QGroupBox(self)
        self.groupbox_btns.setLayout(self.layout_btns)
        self.groupbox_btns.setStyleSheet(stylesheet2)
        self.groupbox_btns.setFixedSize(70, 220)
        self.layoutoutside.addWidget(self.groupbox_btns, 0, 4, 3, 1)

        self.socnet_group = QTableWidget(self)
        self.socnet_group.setColumnCount(2)
        self.socnet_group.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.socnet_group.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.socnet_group.horizontalHeader().setVisible(False)
        self.socnet_group.verticalHeader().setVisible(False)
        self.socnet_group.setSelectionMode(QAbstractItemView.NoSelection)
        self.socnet_group.setFocusPolicy(Qt.NoFocus)
        self.socnet_group.setStyleSheet(stylesheet6)
        self.socnet_group.hide()

        self.photo_show = QGroupBox(self)
        self.photo_show.setAlignment(Qt.AlignCenter)
        self.layout_show = QGridLayout(self)
        self.layout_show.setAlignment(Qt.AlignCenter)
        self.layout_show.setHorizontalSpacing(10)
        self.photo_show.setLayout(self.layout_show)
        self.photo_show.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.photo_show, 1, 2, 2, 2)

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet6
        global stylesheet7
        global stylesheet8
        global stylesheet9
        global icon_explorer
        global icon_view
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
            stylesheet3 =   """
                                QHeaderView::section
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    background-color: #F0F0F0;
                                    color: #000000;
                                }
                            """
            stylesheet6 =   """
                                QTableView
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0;
                                    gridline-color: #A9A9A9;
                                }
                            """
            stylesheet7 =   """
                            QTabWidget::pane
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                background-color: #F0F0F0;
                                color: #000000;
                            }
                            QTabBar::tab
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                padding: 5px;
                                color: #000000;
                                min-width: 12em;
                            }
                            QTabBar::tab:selected
                            {
                                border: 2px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                margin-top: -1px;
                                background-color: #C0C0C0;
                                color: #000000;
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
            icon_explorer = os.getcwd() + '/icons/explorer_light.png'
            icon_view = os.getcwd() + '/icons/view_light.png'
            icon_edit = os.getcwd() + '/icons/edit_light.png'
            icon_explorer = os.getcwd() + '/icons/explorer_light.png'
            icon_view = os.getcwd() + '/icons/view_light.png'
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
            stylesheet3 =   """
                                QHeaderView::section
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    background-color: #1C1C1C;
                                    color: #D3D3D3;
                                }
                            """
            stylesheet6 =   """
                                QTableView
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1c1c1c;
                                    gridline-color: #696969;
                                }
                            """
            stylesheet7 =   """
                                QTabWidget::pane
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1C1C1C;
                                    color: #D3D3D3
                                }
                                QTabBar::tab
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    padding: 5px;
                                    color: #D3D3D3;
                                    min-width: 12em;
                                } 
                                QTabBar::tab:selected
                                {
                                    border: 2px;
                                    border-color: #6A6A6A;
                                    border-style: solid;
                                    margin-top: -1px;
                                    background-color: #1F1F1F;
                                    color: #D3D3D3
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
            icon_explorer = os.getcwd() + '/icons/explorer_dark.png'
            icon_view = os.getcwd() + '/icons/view_dark.png'
            icon_edit = os.getcwd() + '/icons/edit_dark.png'
            icon_delete = os.getcwd() + '/icons/delete_dark.png'

        try:
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll_area.setStyleSheet(stylesheet2)
            self.groupbox_sort.setStyleSheet(stylesheet2)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.socnet_group.setStyleSheet(stylesheet6)
            self.photo_show.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.make_buttons()
            self.setStyleSheet(stylesheet2)
            self.group_type.setStyleSheet(stylesheet1)
            self.set_sort_layout()
            self.type_show_thumbnails()
        except AttributeError:
            pass

    # Получение годов
    def get_years(self) -> None:
        self.date_year.clear()
        j = 0
        k = 0
        dir_to_find_year = Settings.get_destination_media() + '/Media/Photo/const/'
        all_files_and_dirs = os.listdir(dir_to_find_year)
        dir_list = list()
        for name in all_files_and_dirs:
            if os.path.isdir(dir_to_find_year + name):
                if len(os.listdir(dir_to_find_year + name)) >= 1:
                    for file in Path(dir_to_find_year + name).rglob('*'):
                        if (os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG")):
                            k = 1
                    if k == 1:
                        k = 0
                        dir_list.append(name)

        dir_list.sort(reverse=True)
        i = 0
        for year in dir_list:
            if dir_list[i] != 'No_Date_Info':
                self.date_year.addItem(str(year))
            else:
                j = 1
            i += 1
        if j == 1:
            self.date_year.addItem('No_Date_Info')
        else:
            pass

    # Получение месяцев в году
    def get_months(self) -> None:
        self.date_month.clear()
        year = self.date_year.currentText()
        dir_to_find_month = Settings.get_destination_media() + '/Media/Photo/const/' + year + '/'
        all_files_and_dirs = os.listdir(dir_to_find_month)
        dir_list = list()
        k = 0
        for name in all_files_and_dirs:
            if os.path.isdir(dir_to_find_month + name):
                if len(os.listdir(dir_to_find_month + name)) >= 1:
                    for file in Path(dir_to_find_month + name).rglob('*'):
                        if (os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG")):
                            k = 1
                    if k == 1:
                        k = 0
                        dir_list.append(name)

        dir_list.sort(reverse=True)
        for month in dir_list:
            self.date_month.addItem(str(month))

    # Получение дней в месяце
    def get_days(self) -> None:
        self.date_day.clear()
        year = self.date_year.currentText()
        month = self.date_month.currentText()
        dir_to_find_day = Settings.get_destination_media() + '/Media/Photo/const/' + year + '/' + month + '/'
        all_files_and_dirs = os.listdir(dir_to_find_day)
        dir_list = list()
        for name in all_files_and_dirs:
            if os.path.isdir(dir_to_find_day + name):
                if len(os.listdir(dir_to_find_day + name)) >= 1:
                    dir_list.append(name)

        dir_list.sort(reverse=True)
        for day in dir_list:
            self.date_day.addItem(str(day))

        self.date_show_thumbnails()

    # функция отображения кнопок с миниатюрами при сортировке по датам
    def date_show_thumbnails(self) -> None:

        year = self.date_year.currentText()
        month = self.date_month.currentText()
        day = self.date_day.currentText()

        thumbnails_list = list()

        self.photo_directory = Settings.get_destination_media() + f'/Media/Photo/const/{year}/{month}/{day}'
        self.thumbnail_directory = Settings.get_destination_thumb() + f'/thumbnail/const/{year}/{month}/{day}'

        flaw_thumbs, excess_thumbs = Thumbnail.research_flaw_thumbnails(self.photo_directory,
                                                                               self.thumbnail_directory)

        Thumbnail.make_or_del_thumbnails(flaw_thumbs, excess_thumbs, self.photo_directory,
                                         self.thumbnail_directory)

        for file in os.listdir(self.thumbnail_directory):  # получение списка созданных миниатюр
            if file.endswith(".jpg") or file.endswith(".JPG"):
                thumbnails_list.append(file)

        num_of_j = math.ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)  # создание кнопки
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(
                        f'{self.thumbnail_directory}/{thumbnails_list[j * self.thumb_row + i]}')  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)  # помещение картинки на кнопку
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumbnails_list[j * self.thumb_row + i][10:]}')  # добавление названия фото
                    self.button.setObjectName(
                        f'{Settings.get_destination_media()}/Media/Photo/const/{year}/{month}/{day}/{thumbnails_list[j * self.thumb_row + i][10:]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)
            else:
                for i in range(0, self.thumb_row):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f'{self.thumbnail_directory}/{thumbnails_list[j * self.thumb_row + i]}')
                    iqon.pixmap(150, 150)
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumbnails_list[j * self.thumb_row + i][10:]}')
                    self.button.setObjectName(
                        f'{Settings.get_destination_media()}/Media/Photo/const/{year}/{month}/{day}/{thumbnails_list[j * self.thumb_row + i][10:]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)

    # функция отображения кнопок с миниатюрами при сортировке по оборудованию
    def eqip_show_thumbnails(self) -> None:
        camera = self.camera_choose.currentText()
        lens = self.lens_choose.currentText()

        camera_exif = Metadata.equip_name_check_reverse(camera, 'camera')
        lens_exif = Metadata.equip_name_check_reverse(lens, 'lens')

        photo_list = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens)

        thumb_names = list()
        thumbnails_list = list()
        for photo in photo_list:
            photo_splitted = photo.split('/')
            thumb_dir = Settings.get_destination_thumb() + f'/thumbnail/const/{photo_splitted[-4]}/{photo_splitted[-3]}/{photo_splitted[-2]}/'
            thumb_names.append(photo_splitted[-1])

            if os.path.exists(thumb_dir + 'thumbnail_' + photo_splitted[-1]):
                thumbnails_list.append(thumb_dir + 'thumbnail_' + photo_splitted[-1])
            else:
                photo_dir = ''
                for i in range(len(photo_splitted) - 1):
                    photo_dir += photo_splitted[i] + '/'
                Thumbnail.make_or_del_thumbnails([f'{photo_splitted[-1]}'], [], photo_dir[:-1],
                                                 thumb_dir[:-1])
                thumbnails_list.append(thumb_dir + 'thumbnail_' + photo_splitted[-1])

        num_of_j = math.ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)  # создание кнопки
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * self.thumb_row + i]}')  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)  # помещение картинки на кнопку
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumb_names[j * self.thumb_row + i]}')  # добавление названия фото
                    self.button.setObjectName(f'{photo_list[j * self.thumb_row + i]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)
            else:
                for i in range(0, self.thumb_row):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * self.thumb_row + i]}')
                    iqon.pixmap(150, 150)
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumb_names[j * self.thumb_row + i]}')
                    self.button.setObjectName(f'{photo_list[j * self.thumb_row + i]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)


        # фотографии списком выбираются из БД, где есть имя файла и каталог
        # при создании кнопки - миниатюры на неё вешается setObjectName с полным путём до фотографии
        # для showinfo и editexif дата берётся из objectName

    # функция отображения кнопок с миниатюрами при сортировке по соцсетям
    def sn_show_thumbnails(self) -> None:
        network = self.socnet_choose.currentText()
        if network == 'Нет данных':
            return
        else:
            pass
        status = self.sn_status.currentText()

        if status == 'Не выбрано':
            status_bd = 'No value'
        elif status == 'Не публиковать':
            status_bd = 'No publicate'
        elif status == 'Опубликовать':
            status_bd = 'Will publicate'
        elif status == 'Опубликовано':
            status_bd = 'Publicated'

        photo_list = PhotoDataDB.get_sn_photo_list(network, status_bd)

        thumb_names = list()
        thumbnails_list = list()
        for photo in photo_list:
            photo_splitted = photo.split('/')
            thumb_dir = Settings.get_destination_thumb() + f'/thumbnail/const/{photo_splitted[-4]}/{photo_splitted[-3]}/{photo_splitted[-2]}/'
            thumb_names.append(photo_splitted[-1])

            if os.path.exists(thumb_dir + 'thumbnail_' + photo_splitted[-1]):
                thumbnails_list.append(thumb_dir + 'thumbnail_' + photo_splitted[-1])
            else:
                photo_dir = ''
                for i in range(len(photo_splitted) - 1):
                    photo_dir += photo_splitted[i] + '/'
                Thumbnail.make_or_del_thumbnails([f'{photo_splitted[-1]}'], [], photo_dir[:-1],
                                                 thumb_dir[:-1])
                thumbnails_list.append(thumb_dir + 'thumbnail_' + photo_splitted[-1])

        num_of_j = math.ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)  # создание кнопки
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * self.thumb_row + i]}')  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)  # помещение картинки на кнопку
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumb_names[j * self.thumb_row + i]}')  # добавление названия фото
                    self.button.setObjectName(f'{photo_list[j * self.thumb_row + i]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)
            else:
                for i in range(0, self.thumb_row):
                    QtCore.QCoreApplication.processEvents()
                    self.button = QtWidgets.QToolButton(self)
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * self.thumb_row + i]}')
                    iqon.pixmap(150, 150)
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumb_names[j * self.thumb_row + i]}')
                    self.button.setObjectName(f'{photo_list[j * self.thumb_row + i]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)

        # фотографии списком выбираются из БД, где есть имя файла и каталог
        # при создании кнопки - миниатюры на неё вешается setObjectName с полным путём до фотографии
        # для showinfo и editexif дата берётся из objectName

    # выбор функции показа миниатюр в зависимости от выбранной группировки
    def type_show_thumbnails(self) -> None:
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()

        for i in reversed(range(self.layout_inside_thumbs.count())):
            self.layout_inside_thumbs.itemAt(i).widget().deleteLater()

        self.socnet_group.clear()
        self.socnet_group.hide()

        group_type = self.group_type.currentText()
        if group_type == 'Дата':
            self.date_show_thumbnails()
        elif group_type == 'Соцсети':
            self.sn_show_thumbnails()
        elif group_type == 'Оборудование':
            self.eqip_show_thumbnails()

    # функция показа большой картинки
    def showinfo(self) -> None:
        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 50)

        self.photo_path = self.sender().objectName()

        if not self.photo_path:
            if type(self.sender()) is EditFiles.EditExifData:
                self.photo_path = self.last_clicked
            else:
                return

        self.socnet_group.clear()

        self.last_clicked = self.photo_path  # полный путь

        self.metadata_show.clear()
        self.metadata_show.hide()

        self.pic.clear()  # очистка от того, что показано сейчас

        photo_directory_parts = self.photo_path.split('/')
        self.photo_directory = ''
        for i in range(0, len(photo_directory_parts) - 1):
            self.photo_directory += photo_directory_parts[i] + '/'

        self.last_clicked_name = photo_directory_parts[-1]
        self.last_clicked_dir = self.photo_directory[:-1]
        # C:\Users\user\PycharmProjects\TestForPhotoPr/Media/Photo/const/2022/01/18/

        self.photo_file = self.photo_path  # получение информации о нажатой кнопке

        jsondata_wr = {'last_opened_photo': self.photo_file}
        with open('last_opened.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif(Metadata.read_exif(self.photo_file), self.last_clicked_name, self.photo_directory)
        self.photo_rotation = metadata['Rotation']
        params = list(metadata.keys())
        params.remove('Rotation')

        rows = 0
        for param in params:
            if metadata[param]:
                rows += 1

        self.metadata_show.setRowCount(rows)

        r = 0
        max_len = 0
        for i in range(len(params)):
            if metadata[params[i]]:
                self.metadata_show.setItem(r, 0, QTableWidgetItem(params[i]))
                self.metadata_show.setItem(r, 1, QTableWidgetItem(str(metadata[params[i]])))
                r += 1
                if len(str(metadata[params[i]])) > max_len:
                    max_len = len(str(metadata[params[i]]))

        self.metadata_show.setColumnWidth(1, max_len*12)

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)

        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
            self.metadata_show.show()
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40, self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
            self.pic.show()
            self.layout_show.addWidget(self.socnet_group, 1, 2, 1, 1)
            self.socnet_group.show()
            self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 60)
        else:  # self.photo_rotation == 'ver'
            self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
            self.metadata_show.show()
            self.layout_show.addWidget(self.socnet_group, 2, 1, 1, 1)
            # self.show_social_networks(self.last_clicked_name, photo_directory)
            self.socnet_group.show()
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 50, self.size().height() - self.groupbox_sort.height() - 30,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
            self.pic.show()
            self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)

        self.show_social_networks(self.last_clicked_name, self.last_clicked_dir)
        # self.set_minimum_size.emit(self.scroll_area.width() + self.metadata_show.width() + self.socnet_group.width() + self.groupbox_btns.width() + 60)
        self.oldsize = self.size()

    # убрать с экрана фото и метаданные после удаления фотографии
    def clear_after_del(self) -> None:
        self.type_show_thumbnails()
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.socnet_group.clear()
        self.socnet_group.hide()

        if self.group_type.currentText() == 'Дата':
            old_year = self.date_year.currentText()
            old_month = self.date_month.currentText()
            old_day = self.date_day.currentText()
            self.fill_sort_date()
            self.date_year.setCurrentText(old_year)
            self.date_month.setCurrentText(old_month)
            self.date_day.setCurrentText(old_day)
        elif self.group_type.currentText() == 'Соцсети':
            old_network = self.socnet_choose.currentText()
            old_status = self.sn_status.currentText()
            self.fill_sort_socnets()
            self.socnet_choose.setCurrentText(old_network)
            self.sn_status.setCurrentText(old_status)
        elif self.group_type.currentText() == 'Оборудование':
            old_camera = self.camera_choose.currentText()
            old_lens = self.lens_choose.currentText()
            self.fill_sort_equipment()
            self.camera_choose.setCurrentText(old_camera)
            self.lens_choose.setCurrentText(old_lens)

    # Действия при изменении размеров окна
    def resizeEvent(self, QResizeEvent) -> None:
        self.resized_signal.emit()

    def resize_func(self) -> None:
        self.resize_photo()

    def resize_photo(self) -> None:
        if not self.pic.isVisible():
            return

        if self.photo_rotation == 'gor':
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40,
                self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
        else:
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 80,
                self.size().height() - self.groupbox_sort.height() - 10,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)

        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 50)

    # Создание кнопок удаления и редактирования
    def make_buttons(self) -> None:
        self.edit_btn = QToolButton(self)
        self.edit_btn.setStyleSheet(stylesheet1)
        self.edit_btn.setIcon(QtGui.QIcon(icon_edit))
        self.edit_btn.setIconSize(QtCore.QSize(50, 50))
        self.edit_btn.setToolTip("Редактирование метаданных")
        self.edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.edit_btn, 0, 0, 1, 1)
        self.edit_btn.clicked.connect(self.edit_exif_func)

        self.del_btn = QToolButton(self)
        self.del_btn.setStyleSheet(stylesheet1)
        self.del_btn.setIcon(QtGui.QIcon(icon_delete))
        self.del_btn.setIconSize(QtCore.QSize(50, 50))
        self.del_btn.setToolTip("Удалить")
        self.del_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.del_btn, 1, 0, 1, 1)
        self.del_btn.clicked.connect(self.del_photo_func)

        self.explorer_btn = QToolButton(self)
        self.explorer_btn.setStyleSheet(stylesheet1)
        self.explorer_btn.setIcon(QtGui.QIcon(icon_explorer))
        self.explorer_btn.setIconSize(QtCore.QSize(50, 50))
        self.explorer_btn.setToolTip("Показать в проводнике")
        self.explorer_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.explorer_btn, 2, 0, 1, 1)
        self.explorer_btn.clicked.connect(self.call_explorer)

        self.open_file_btn = QToolButton(self)
        self.open_file_btn.setStyleSheet(stylesheet1)
        self.open_file_btn.setIcon(QtGui.QIcon(icon_view))
        self.open_file_btn.setIconSize(QtCore.QSize(50, 50))
        self.open_file_btn.setToolTip("Открыть")
        self.open_file_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.open_file_btn, 3, 0, 1, 1)
        self.open_file_btn.clicked.connect(self.open_file_func)

    # открыть фотографию в приложении просмотра
    def open_file_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        path = self.last_clicked
        os.startfile(path)

    # показать фото в проводнике
    def call_explorer(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        open_path = self.last_clicked
        path = open_path.replace('/', '\\')
        exp_str = f'explorer /select,\"{path}\"'
        os.system(exp_str)

    # удаление фото по нажатию кнопки
    def del_photo_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.last_clicked_name
        photodirectory = self.last_clicked_dir
        dialog_del = DelPhotoConfirm(photoname, photodirectory)
        dialog_del.clear_info.connect(self.clear_after_del)
        if dialog_del.exec():
            self.last_clicked = ''

    # редактирование exif
    def edit_exif_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.last_clicked_name
        photodirectory = self.last_clicked_dir

        if self.group_type.currentText() == 'Дата':
            old_year = self.date_year.currentText()
            old_month = self.date_month.currentText()
            old_day = self.date_day.currentText()
        elif self.group_type.currentText() == 'Соцсети':
            old_network = self.socnet_choose.currentText()
            old_status = self.sn_status.currentText()
        elif self.group_type.currentText() == 'Оборудование':
            old_camera = self.camera_choose.currentText()
            old_lens = self.lens_choose.currentText()

        def re_show():
            if self.group_type.currentText() == 'Дата':
                self.showinfo()
            else:
                self.pic.clear()
                self.metadata_show.clear()
                self.metadata_show.hide()

                if self.group_type.currentText() == 'Соцсети':
                    self.socnet_choose.setCurrentText(old_network)
                    self.sn_status.setCurrentText(old_status)
                    self.sn_show_thumbnails()
                elif self.group_type.currentText() == 'Оборудование':
                    self.fill_sort_equipment()
                    self.camera_choose.setCurrentText(old_camera)
                    self.lens_choose.setCurrentText(old_lens)
                    self.eqip_show_thumbnails()

        dialog_edit = EditFiles.EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory,
                                   chosen_group_type=self.group_type.currentText())
        dialog_edit.show()

        if self.group_type.currentText() == 'Дата':
            dialog_edit.movement_signal.connect(lambda y, m, d: self.get_date(y, m, d))

        if self.pic.isVisible():
            dialog_edit.edited_signal.connect(re_show)

        # dialog_edit.edited_signal_no_move.connect(self.pre_show_info)
        dialog_edit.edited_signal_no_move.connect(self.showinfo)

    # при редактировании метаданных могут создаваться новые папки (по датам), а фото будут переноситься - надо обновлять отображение
    def get_date(self, year: str, month: str, day: str) -> None:
        self.socnet_group.clear()
        self.socnet_group.hide()
        self.group_type.setCurrentText('Дата')
        self.get_years()
        self.get_months()
        self.get_days()
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.date_show_thumbnails()
        self.date_year.setCurrentText(year)
        self.date_month.setCurrentText(month)
        self.date_day.setCurrentText(day)

    # отображения статуса фото в соцсетях
    def show_social_networks(self, photoname: str, photodirectory: str) -> None:
        def fill_sn_widgets(sn_names: list[str], sn_tags: dict) -> None:
            i = 0
            self.socnet_group.setRowCount(len(sn_names))
            if not sn_names:
                self.socnet_group.setStyleSheet(stylesheet2)
                self.socnet_group.hide()
                return
            else:
                self.socnet_group.show()

            self.max_name_len = 0
            for name in sn_names:
                if len(name) > self.max_name_len:
                    self.max_name_len = len(name)

                self.sn_lbl = QLabel(self)
                self.sn_lbl.setFont(font14)
                self.sn_lbl.setStyleSheet(stylesheet2)

                if name[:9] != 'numnumnum':
                    self.sn_lbl.setText(f"{name}")
                else:
                    self.sn_lbl.setText(f"{name[9:]}")

                self.sn_lbl.setFixedWidth(len(name)*12)
                self.socnet_group.setCellWidget(i, 0, self.sn_lbl)

                self.sn_tag_choose = QComboBox(self)
                self.sn_tag_choose.setFont(font14)
                self.sn_tag_choose.setStyleSheet(stylesheet9)
                self.sn_tag_choose.setObjectName(name)
                self.sn_tag_choose.addItem('Не выбрано')
                self.sn_tag_choose.addItem('Не публиковать')
                self.sn_tag_choose.addItem('Опубликовать')
                self.sn_tag_choose.addItem('Опубликовано')

                if sn_tags[f'{name}'] == 'No value':
                    self.sn_tag_choose.setCurrentText('Не выбрано')
                elif sn_tags[f'{name}'] == 'No publicate':
                    self.sn_tag_choose.setCurrentText('Не публиковать')
                elif sn_tags[f'{name}'] == 'Will publicate':
                    self.sn_tag_choose.setCurrentText('Опубликовать')
                elif sn_tags[f'{name}'] == 'Publicated':
                    self.sn_tag_choose.setCurrentText('Опубликовано')

                self.sn_tag_choose.currentTextChanged.connect(edit_tags)
                self.sn_tag_choose.currentTextChanged.connect(refresh_thumbs)

                self.socnet_group.setCellWidget(i, 1, self.sn_tag_choose)
                i += 1

                if self.sn_lbl.width() > self.metadata_show.columnWidth(0):
                    self.metadata_show.setColumnWidth(0, self.sn_lbl.width())

            if not sn_names:
                self.socnet_group.setStyleSheet(stylesheet2)
            else:
                self.socnet_group.setStyleSheet(stylesheet6)

            self.socnet_group_header = self.socnet_group.horizontalHeader()

            if self.photo_rotation == 'gor':
                self.socnet_group.setColumnWidth(0, self.max_name_len * 12)
                self.socnet_group.setColumnWidth(1, 180)
            else:
                if self.metadata_show.columnWidth(0) > 100:
                 self.socnet_group.setColumnWidth(0, self.metadata_show.columnWidth(0))
                else:
                    self.socnet_group.setColumnWidth(0, 100)
                if self.metadata_show.columnWidth(1) > 180:
                    self.socnet_group.setColumnWidth(1, self.metadata_show.columnWidth(1))
                else:
                    self.socnet_group.setColumnWidth(1, 180)

            self.socnet_group.setFixedWidth(self.socnet_group.columnWidth(0) + self.socnet_group.columnWidth(1)+2)
            self.socnet_group.setFixedHeight(self.socnet_group.rowCount() * self.socnet_group.rowHeight(0) + 2)

        def edit_tags():
            new_status = self.sender().currentText()
            if new_status == 'Не выбрано':
                new_status_bd = 'No value'
            elif new_status == 'Не публиковать':
                new_status_bd = 'No publicate'
            elif new_status == 'Опубликовать':
                new_status_bd = 'Will publicate'
            elif new_status == 'Опубликовано':
                new_status_bd = 'Publicated'

            network = self.sender().objectName()
            PhotoDataDB.edit_sn_tags(photoname, photodirectory, new_status_bd, network)

        def refresh_thumbs():
            if self.group_type.currentText() == 'Соцсети':
                if self.socnet_choose.currentText() == self.sender().objectName() or self.socnet_choose.currentText() == self.sender().objectName()[
                                                                                                                         9:]:
                    self.type_show_thumbnails()
                else:
                    pass
            else:
                pass

        sn_names, sn_tags = PhotoDataDB.get_social_tags(photoname, photodirectory)

        fill_sn_widgets(sn_names, sn_tags)

    # выбор способа группировки
    def fill_sort_groupbox(self) -> None:
        self.group_type = QComboBox(self)
        self.group_type.addItem('Дата')
        self.group_type.addItem('Соцсети')
        self.group_type.addItem('Оборудование')
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(152)
        self.group_type.setFixedHeight(30)
        self.group_type.setStyleSheet(stylesheet9)

        self.layoutoutside.addWidget(self.group_type, 0, 0, 1, 1)

    # заполнить поле группировки по дате
    def fill_sort_date(self) -> None:
        self.year_lbl = QLabel(self)
        self.year_lbl.setFont(font14)
        self.year_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.year_lbl, 0, 1, 1, 1)

        self.date_year = QComboBox(self)
        self.date_year.setStyleSheet(stylesheet9)
        self.date_year.setFont(font14)
        self.date_year.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_years()
        self.date_year.setFixedWidth(140)
        self.layout_type.addWidget(self.date_year, 0, 2, 1, 1)

        self.month_lbl = QLabel(self)
        self.month_lbl.setFont(font14)
        self.month_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.month_lbl, 0, 3, 1, 1)

        self.date_month = QComboBox(self)
        self.date_month.setFont(font14)
        self.date_month.setStyleSheet(stylesheet9)
        self.date_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_months()
        self.date_month.setFixedWidth(140)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1)

        self.day_lbl = QLabel(self)
        self.day_lbl.setFont(font14)
        self.day_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.day_lbl, 0, 5, 1, 1)

        if not self.year_lbl.text():
            self.year_lbl.setText('Год:')
            self.month_lbl.setText('    Месяц:')
            self.day_lbl.setText('    День:')

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_days()
        self.date_day.setFixedWidth(140)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1)

        self.date_day.setFixedHeight(30)
        self.date_month.setFixedHeight(30)
        self.date_year.setFixedHeight(30)
        self.day_lbl.setFixedHeight(30)
        self.month_lbl.setFixedHeight(30)
        self.year_lbl.setFixedHeight(30)

        self.date_year.currentTextChanged.connect(self.get_months)
        self.date_month.currentTextChanged.connect(self.get_days)
        self.date_day.currentTextChanged.connect(self.type_show_thumbnails)

    # заполнить поле группировки по соцсетям
    def fill_sort_socnets(self) -> None:
        self.socnet_choose = QComboBox(self)
        self.socnet_choose.setFont(font14)
        self.socnet_choose.setFixedHeight(30)
        self.socnet_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.socnet_choose, 0, 1, 1, 1)
        socnets = PhotoDataDB.get_socialnetworks()

        if not socnets:
            self.socnet_choose.addItem('Нет данных')
            self.socnet_choose.setFixedWidth(150)
        else:
            socnet_max_len = 0
            for net in socnets:
                if net[0:9] != 'numnumnum':
                    self.socnet_choose.addItem(f'{net}')
                    if len(net) > socnet_max_len:
                        socnet_max_len = len(net)
                else:
                    self.socnet_choose.addItem(f'{net[9:]}')
                    if len(net) - 9 > socnet_max_len:
                        socnet_max_len = len(net) - 9



            self.socnet_choose.setFixedWidth(socnet_max_len*12+30)

            self.socnet_choose.currentTextChanged.connect(self.type_show_thumbnails)

            self.sn_status = QComboBox(self)
            self.sn_status.setFont(font14)
            self.sn_status.setFixedHeight(30)
            self.sn_status.setStyleSheet(stylesheet9)
            self.sn_status.addItem('Не выбрано')
            self.sn_status.addItem('Не публиковать')
            self.sn_status.addItem('Опубликовать')
            self.sn_status.addItem('Опубликовано')
            self.sn_status.setFixedWidth(164)
            self.layout_type.addWidget(self.sn_status, 0, 2, 1, 1)

            self.sn_status.currentTextChanged.connect(self.type_show_thumbnails)

    # заполнить поле группировки по оборудованию
    def fill_sort_equipment(self) -> None:
        self.camera_choose = QComboBox(self)
        self.camera_choose.setFont(font14)
        self.camera_choose.setFixedHeight(30)
        self.camera_choose.setStyleSheet(stylesheet9)
        self.lens_choose = QComboBox(self)
        self.lens_choose.setFont(font14)
        self.lens_choose.setFixedHeight(30)
        self.lens_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.camera_choose, 0, 1, 1, 1)
        self.layout_type.addWidget(self.lens_choose, 0, 2, 1, 1)

        cameras, lenses = PhotoDataDB.get_equipment()
        camera_max_len = 0
        lens_max_len = 0

        for camera in cameras:
            self.camera_choose.addItem(f'{camera}')
            if len(camera) > camera_max_len:
                camera_max_len = len(camera)

        for lens in lenses:
            self.lens_choose.addItem(f'{lens}')
            if len(lens) > lens_max_len:
                lens_max_len = len(lens)

        self.camera_choose.setFixedWidth(camera_max_len*12)
        self.lens_choose.setFixedWidth(lens_max_len*12)

        self.camera_choose.currentTextChanged.connect(self.type_show_thumbnails)
        self.lens_choose.currentTextChanged.connect(self.type_show_thumbnails)

    # заполнить нужное поле в зависимости от выбранного типа группировки
    def set_sort_layout(self) -> None:

        sort_type = self.group_type.currentText()

        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().deleteLater()

        if sort_type == 'Дата':
            self.fill_sort_date()
        elif sort_type == 'Соцсети':
            self.fill_sort_socnets()
        elif sort_type == 'Оборудование':
            self.fill_sort_equipment()

        self.type_show_thumbnails()

    # обновить дизайн при изменении настроек
    def after_change_settings(self) -> None:
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll_area.setFixedWidth(200 * self.thumb_row)

        self.type_show_thumbnails()


# подтвердить удаление фото
class DelPhotoConfirm(QDialog):
    clear_info = QtCore.pyqtSignal()

    def __init__(self, photoname, photodirectory):
        super(DelPhotoConfirm, self).__init__()

        self.photoname = photoname
        self.photodirectory = photodirectory

        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Подтверждение удаления')
        self.resize(400, 100)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.lbl = QLabel()
        self.lbl.setText(f'Вы точно хотите удалить {self.photoname}?')
        self.lbl.setFont(font12)
        self.lbl.setStyleSheet(stylesheet2)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl, 0, 0, 1, 2)

        btn_ok = QPushButton(self)
        btn_ok.setText('Подтверждение')
        btn_ok.setFont(font12)
        btn_ok.setStyleSheet(stylesheet8)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('Отмена')
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet8)

        self.layout.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(lambda: self.do_del(photoname, photodirectory))
        btn_cancel.clicked.connect(self.reject)

    # при подтверждении - удалить фото, его миниатюру и записи в БД
    def do_del(self, photoname: str, photodirectory: str) -> None:
        os.remove(photodirectory + '/' + photoname)
        Thumbnail.delete_thumbnail_const(photoname, photodirectory)
        PhotoDataDB.del_from_database(photoname, photodirectory)
        self.clear_info.emit()
        self.accept()


# совпали имена файлов при переносе по новой дате в exif
class EqualNames(QDialog):

    file_rename_transfer_signal = QtCore.pyqtSignal()

    def __init__(self, parent, filesname, old_date, new_date, full_exif_date):
        super(EqualNames, self).__init__(parent)
        self.full_exif_date = full_exif_date

        # Создание окна
        self.setWindowTitle('Конфликт имён файлов')
        self.resize(600, 90)

        # new - в котором изменили дату
        # old - который уже есть в папке с этой датой
        self.file_full_name = filesname
        self.filename = filesname.split('.')[0]
        self.format = filesname.split('.')[1]
        self.old_date = old_date
        self.new_date = new_date

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.text_lbl = QLabel(self)
        self.text_lbl.setText('В каталоге уже есть файл с такими же датой съёмки и именем. Что делать?')
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setFont(font12)
        self.text_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.text_lbl, 0, 0, 1, 4)

        self.old_top_lbl = QLabel(self)
        self.old_top_lbl.setText('Фото уже существующее в папке')
        self.old_top_lbl.setFont(font12)
        self.old_top_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.old_top_lbl, 1, 0, 1, 2)

        self.new_top_lbl = QLabel(self)
        self.new_top_lbl.setText('Фото перемещаемое из-за изменения даты')
        self.new_top_lbl.setFont(font12)
        self.new_top_lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.new_top_lbl, 1, 2, 1, 2)

        self.pic_old = QLabel(self)
        self.pic_old.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.pic_old, 2, 0, 1, 2)

        self.pic_new = QLabel(self)
        self.pic_new.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.pic_new, 2, 2, 1, 2)

        self.old_checkbox = QCheckBox(self)
        self.old_checkbox.setObjectName('old_checkbox')
        self.layout.addWidget(self.old_checkbox, 3, 0, 1, 1)

        self.old_name = QLineEdit(self)
        self.old_name.setText(self.filename)
        self.old_name.setStyleSheet(stylesheet1)
        self.old_name.setFont(font12)
        self.layout.addWidget(self.old_name, 3, 1, 1, 1)
        self.old_name.setDisabled(True)

        self.new_checkbox = QCheckBox(self)
        self.new_checkbox.setObjectName('new_checkbox')
        self.layout.addWidget(self.new_checkbox, 3, 2, 1, 1)
        self.new_checkbox.setCheckState(2)

        self.new_name = QLineEdit(self)
        self.new_name.setText(self.filename)
        self.new_name.setStyleSheet(stylesheet1)
        self.new_name.setFont(font12)
        self.layout.addWidget(self.new_name, 3, 3, 1, 1)

        self.old_checkbox.stateChanged.connect(self.check_disable)
        self.new_checkbox.stateChanged.connect(self.check_disable)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Переименовать')
        self.btn_ok.setFont(font12)
        self.btn_ok.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_ok, 4, 0, 1, 2)
        self.btn_ok.clicked.connect(lambda: self.ok_check(self.new_name.text(), self.old_name.text()))

        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Не переносить (отменить изменение даты)')
        self.btn_cnl.setFont(font12)
        self.btn_cnl.setStyleSheet(stylesheet8)
        self.layout.addWidget(self.btn_cnl, 4, 2, 1, 2)
        self.btn_cnl.clicked.connect(lambda: self.close())

        self.show_photos()

    # показать в уменьшенном виде 2 фото, у которых совпали названия
    def show_photos(self) -> None:
        self.old_photo_dir = Settings.get_destination_media() + '/Media/Photo/const/' + f'{self.old_date[0]}/{self.old_date[1]}/{self.old_date[2]}/'
        self.new_photo_dir = Settings.get_destination_media() + '/Media/Photo/const/' + f'{self.new_date[0]}/{self.new_date[1]}/{self.new_date[2]}/'
        pixmap_old = QtGui.QPixmap(self.old_photo_dir + self.file_full_name).scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        pixmap_new = QtGui.QPixmap(self.new_photo_dir + self.file_full_name).scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        self.pic_old.setPixmap(pixmap_old)
        self.pic_new.setPixmap(pixmap_new)

    # какое фото выбрано для переименования, а какое остаётся со своим имеем
    def check_disable(self) -> None:
        last_changed = self.sender().objectName()
        if last_changed == 'old_checkbox':
            if self.old_checkbox.checkState():  # поставили галочку
                self.new_name.setDisabled(True)
                self.old_name.setDisabled(False)
                self.new_checkbox.setCheckState(0)
            else:
                self.new_name.setDisabled(False)
                self.old_name.setDisabled(True)
                self.new_checkbox.setCheckState(2)
        else:   # last_changed == 'new_checkbox'
            if self.new_checkbox.checkState():  # поставили галочку
                self.new_name.setDisabled(False)
                self.old_name.setDisabled(True)
                self.old_checkbox.setCheckState(0)
            else:
                self.new_name.setDisabled(True)
                self.old_name.setDisabled(False)
                self.old_checkbox.setCheckState(2)

    # проверка ввода названий
    def ok_check(self, new_enter_text: str, old_enter_text: str) -> None:

        if new_enter_text == old_enter_text:
            err_win = ErrorsAndWarnings.ExistFileRenameError1(self)
            err_win.show()
            return

        if self.new_checkbox.checkState():  # переименовывается переносимый файл
            new_new_name = self.new_name.text() + '.' + self.format

            if os.path.exists(self.old_photo_dir + new_new_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)     # type: ignore[assignment]
                err_win.show()
                return

            os.rename(self.new_photo_dir + self.file_full_name, self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg')
            shutil.move(self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir)
            os.rename(self.old_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir + new_new_name)

            PhotoDataDB.filename_after_transfer(self.file_full_name, new_new_name, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 0)
            Thumbnail.transfer_equal_date_thumbnail(self.file_full_name, self.file_full_name, self.old_date, self.new_date, new_new_name, 'new')
            Metadata.exif_rewrite_edit(new_new_name, self.old_photo_dir, 13, self.full_exif_date)
            PhotoDataDB.edit_in_database(new_new_name, self.old_photo_dir[:-1], 13, self.full_exif_date)
        else:       # переименовывается файл в папке назначения
            new_old_name = self.old_name.text() + '.' + self.format

            if os.path.exists(self.old_photo_dir + new_old_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)     # type: ignore[assignment]
                err_win.show()
                return

            os.rename(self.old_photo_dir + self.file_full_name, self.old_photo_dir + new_old_name)
            shutil.move(self.new_photo_dir + self.file_full_name, self.old_photo_dir)

            PhotoDataDB.filename_after_transfer(self.file_full_name, new_old_name, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 1)
            Thumbnail.transfer_equal_date_thumbnail(self.file_full_name, self.file_full_name, self.old_date, self.new_date, new_old_name, 'old')
            Metadata.exif_rewrite_edit(new_old_name, self.old_photo_dir, 13, self.full_exif_date)
            PhotoDataDB.edit_in_database(new_old_name, self.old_photo_dir[:-1], 13, self.full_exif_date)
        self.file_rename_transfer_signal.emit()
        self.close()


# Окошко подтверждения желания очистить метаданные
class ConfirmClear(QDialog):
    accept_signal = QtCore.pyqtSignal()
    reject_signal = QtCore.pyqtSignal()
    def __init__(self, parent):
        super(ConfirmClear, self).__init__(parent)

        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Подтверждение очистки')
        self.resize(400, 100)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.lbl = QLabel()
        self.lbl.setText(f'Вы точно хотите очистить метаданные?')
        self.lbl.setFont(font12)
        self.lbl.setStyleSheet(stylesheet2)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl, 0, 0, 1, 2)

        btn_ok = QPushButton(self)
        btn_ok.setText('Подтверждение')
        btn_ok.setFont(font12)
        btn_ok.setStyleSheet(stylesheet8)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('Отмена')
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet8)

        self.layout.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(self.accept_signal.emit)
        btn_ok.clicked.connect(self.close)
        btn_cancel.clicked.connect(self.reject_signal.emit)
        btn_cancel.clicked.connect(self.close)
