import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from math import ceil
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


font14 = QtGui.QFont('Times', 14)

stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: black; background-color: #F0F0F0"
stylesheet2 = "border: 0px; color: black; background-color: #F0F0F0"


class ConstWidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):

        super().__init__()

        self.own_dir = os.getcwd()
        resolution = Screenconfig.monitor_info()
        self.monitor_width = resolution[0]
        self.monitor_height = resolution[1]

        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.setWindowTitle("Тестовое окно")
        self.showMaximized()

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
        self.scroll = QScrollArea(self)  # создание подвижной области
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.groupbox_thumbs)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(stylesheet2)

        self.layoutoutside.addWidget(self.scroll, 1, 0, 2, 2)  # помещение подвижной области на слой
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)  # задание размеров подвижной области и её внутренностей
        self.scroll.setFixedWidth(200*self.thumb_row)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(50)
        # self.groupbox_sort.setMaximumWidth(700)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.groupbox_sort, 0, 1, 1, 3)

        self.fill_sort_groupbox()
        self.fill_sort_date()
        self.groupbox_sort.setLayout(self.layout_type)

        self.empty2 = QLabel(self)
        self.empty2.setMaximumWidth(self.monitor_width - self.thumb_row*200)
        self.layoutoutside.addWidget(self.empty2, 1, 2, 2, 1)

        self.date_show_thumbnails()

        self.metadata_show = QtWidgets.QTableWidget()
        self.metadata_show.setColumnCount(2)

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
        self.socnet_group.setStyleSheet(stylesheet1)

        self.photo_show = QGroupBox(self)
        self.photo_show.setAlignment(Qt.AlignCenter)
        self.layout_show = QGridLayout(self)
        self.layout_show.setAlignment(Qt.AlignCenter)
        self.layout_show.setHorizontalSpacing(10)
        self.photo_show.setLayout(self.layout_show)
        self.photo_show.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.photo_show, 1, 2, 2, 2)

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

        nedostatok_thumbs, izbitok_thumbs = Thumbnail.research_need_thumbnails(self.photo_directory,
                                                                               self.thumbnail_directory)

        Thumbnail.make_or_del_thumbnails(nedostatok_thumbs, izbitok_thumbs, self.photo_directory,
                                         self.thumbnail_directory)

        for file in os.listdir(self.thumbnail_directory):  # получение списка созданных миниатюр
            if file.endswith(".jpg") or file.endswith(".JPG"):
                thumbnails_list.append(file)

        num_of_j = ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
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

        num_of_j = ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
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

        num_of_j = ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
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
        self.photo_show.setFixedWidth(self.width() - self.scroll.width() - self.groupbox_btns.width() - 50)

        self.empty2.hide()
        self.photo_path = self.sender().objectName()

        if not self.photo_path:
            if type(self.sender()) is EditExifData:
                self.photo_path = self.last_clicked
            else:
                return

        self.socnet_group.clear()

        self.last_clicked = self.photo_path  # полный путь

        self.metadata_show.clear()
        self.metadata_show.hide()

        self.pic.clear()  # очистка от того, что показано сейчас

        photo_directory_parts = self.photo_path.split('/')
        photo_directory = ''
        for i in range(0, len(photo_directory_parts) - 1):
            photo_directory += photo_directory_parts[i] + '/'

        self.last_clicked_name = photo_directory_parts[-1]
        self.last_clicked_dir = photo_directory
        # C:\Users\user\PycharmProjects\TestForPhotoPr/Media/Photo/const/2022/01/18/

        self.photo_file = self.photo_path  # получение информации о нажатой кнопке

        jsondata_wr = {'last_opened_photo': self.photo_file}
        with open('last_opened.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif_beta(Metadata.read_exif(self.last_clicked_name, photo_directory, self.own_dir),
                                             self.last_clicked_name, photo_directory)

        self.photo_rotation = metadata['Rotation']
        params = list(metadata.keys())
        params.remove('Rotation')

        rows = 0
        for param in params:
            if metadata[param]:
                rows += 1

        self.metadata_show.setRowCount(rows)

        for i in range(rows):
            self.metadata_show.setItem(i, 0, QTableWidgetItem(params[i]))
            self.metadata_show.setItem(i, 1, QTableWidgetItem(metadata[params[i]]))

        self.metadata_show.setFont(font14)

        self.metadata_show.horizontalHeader().setVisible(False)
        self.metadata_show.verticalHeader().setVisible(False)

        self.metadata_header = self.metadata_show.horizontalHeader()
        self.metadata_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)
        self.metadata_show.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setDisabled(True)

        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
            self.metadata_show.show()
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll.width() - 40, self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 2)
            self.pic.show()
            self.layout_show.addWidget(self.socnet_group, 1, 1, 1, 1)
            self.socnet_group.show()
        else:  # self.photo_rotation == 'ver'
            self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
            self.metadata_show.show()
            self.layout_show.addWidget(self.socnet_group, 1, 1, 1, 1)
            self.socnet_group.show()
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll.width() - 50, self.size().height() - self.groupbox_sort.height() - 30,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 2, 1)
            self.pic.show()

        self.show_social_networks(self.last_clicked_name, photo_directory)
        # self.photo_show.setMinimumWidth(self.metadata_show.width()+self.socnet_group.width()+50)
        self.set_minimum_size.emit(self.scroll.width() + self.metadata_show.width() + self.socnet_group.width() + self.groupbox_btns.width() + 120)
        self.oldsize = self.size()
        self.metadata_show.setStyleSheet(stylesheet1)

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

    def resize_photo(self):
        if not self.pic.isVisible():
            return

        if self.photo_rotation == 'gor':
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.groupbox_btns.width() - self.scroll.width() - 40,
                self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 2)

        else:
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll.width() - 80,
                self.size().height() - self.groupbox_sort.height() - 30,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 2, 1)

        self.photo_show.setFixedWidth(self.width() - self.scroll.width() - self.groupbox_btns.width() - 50)

    # Создание кнопок удаления и редактирования
    def make_buttons(self) -> None:
        self.edit_btn = QToolButton(self)
        self.edit_btn.setStyleSheet(stylesheet1)
        # self.edit_btn.setIcon()
        self.edit_btn.setText('RED')
        self.edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.edit_btn, 0, 0, 1, 1)
        self.edit_btn.clicked.connect(self.edit_exif_func)

        self.del_btn = QToolButton(self)
        self.del_btn.setStyleSheet(stylesheet1)
        # self.del_btn.setIcon()
        self.del_btn.setText('DEL')
        self.del_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.del_btn, 1, 0, 1, 1)
        self.del_btn.clicked.connect(self.del_photo_func)

        self.explorer_btn = QToolButton(self)
        self.explorer_btn.setStyleSheet(stylesheet1)
        # self.explorer_btn.setIcon()
        self.explorer_btn.setText('EXP')
        self.explorer_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.explorer_btn, 2, 0, 1, 1)
        self.explorer_btn.clicked.connect(self.call_explorer)

        self.open_file_btn = QToolButton(self)
        self.open_file_btn.setStyleSheet(stylesheet1)
        # self.open_file_btn.setIcon()
        self.open_file_btn.setText('OPN')
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
        photodirectory = self.last_clicked_dir[:-1]
        dialog_del = DelPhotoConfirm(photoname, photodirectory)
        dialog_del.clear_info.connect(self.clear_after_del)
        if dialog_del.exec():
            self.last_clicked = ''
        elif dialog_del.reject():
            return

    # редактирование exif
    def edit_exif_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.last_clicked_name
        photodirectory = self.last_clicked_dir[:-1]

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
                pass
            else:
                for i in reversed(range(self.layout_sn.count())):
                    self.layout_sn.itemAt(i).widget().deleteLater()
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

        dialog_edit = EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory,
                                   chosen_group_type=self.group_type.currentText())
        dialog_edit.show()

        if self.group_type.currentText() == 'Дата':
            dialog_edit.movement_signal.connect(lambda y, m, d: self.get_date(y, m, d))
        else:
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

        def fill_sn_widgets(sn_names: list[str, ...], sn_tags: dict) -> None:
            i = 0
            self.socnet_group.setRowCount(len(sn_names))
            for name in sn_names:
                self.sn_lbl = QLabel(self)
                self.sn_lbl.setFont(font14)
                self.sn_lbl.setStyleSheet(stylesheet2)

                if name[:9] != 'numnumnum':
                    self.sn_lbl.setText(f"{name}")
                else:
                    self.sn_lbl.setText(f"{name[9:]}")

                self.sn_lbl.setFixedWidth(len(name)*15)
                self.socnet_group.setCellWidget(i, 0, self.sn_lbl)

                self.sn_tag_choose = QComboBox(self)
                self.sn_tag_choose.setFont(font14)
                self.sn_tag_choose.setStyleSheet(stylesheet1)
                # self.sn_tag_choose.setFixedWidth(self.metadata_show.columnWidth(1))
                self.sn_tag_choose.setObjectName(name)
                self.sn_tag_choose.addItem('Не выбрано')
                self.sn_tag_choose.addItem('Не публиковать')
                self.sn_tag_choose.addItem('Опубликовать')
                self.sn_tag_choose.addItem('Опубликовано')
                if self.photo_rotation == 'gor':
                    self.sn_tag_choose.setFixedWidth(180)
                else:
                    self.sn_tag_choose.setFixedWidth(self.metadata_show.columnWidth(1))

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
                self.socnet_group.setStyleSheet(stylesheet1)

            self.socnet_group_header = self.socnet_group.horizontalHeader()

            if self.photo_rotation == 'gor':
                self.socnet_group_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                self.socnet_group_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            else:
                self.socnet_group.setColumnWidth(0, self.metadata_show.columnWidth(0))
                self.socnet_group.setColumnWidth(1, self.metadata_show.columnWidth(1))

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
            PhotoDataDB.edit_sn_tags(photoname, photodirectory[:-1], new_status_bd, network)

        def refresh_thumbs():
            if self.group_type.currentText() == 'Соцсети':
                if self.socnet_choose.currentText() == self.sender().objectName() or self.socnet_choose.currentText() == self.sender().objectName()[
                                                                                                                         9:]:
                    self.type_show_thumbnails()
                else:
                    pass
            else:
                pass

        sn_names, sn_tags = PhotoDataDB.get_social_tags(photoname, photodirectory[:-1])

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
        self.group_type.setStyleSheet(stylesheet1)

        self.layoutoutside.addWidget(self.group_type, 0, 0, 1, 1)

    # заполнить поле группировки по дате
    def fill_sort_date(self) -> None:

        self.year_lbl = QLabel(self)
        self.year_lbl.setFont(font14)
        self.layout_type.addWidget(self.year_lbl, 0, 1, 1, 1)

        self.date_year = QComboBox(self)
        self.date_year.setStyleSheet(stylesheet1)
        self.date_year.setFont(font14)
        self.date_year.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_years()
        self.date_year.setFixedWidth(140)
        self.layout_type.addWidget(self.date_year, 0, 2, 1, 1)

        self.month_lbl = QLabel(self)
        self.month_lbl.setFont(font14)
        self.layout_type.addWidget(self.month_lbl, 0, 3, 1, 1)

        self.date_month = QComboBox(self)
        self.date_month.setFont(font14)
        self.date_month.setStyleSheet(stylesheet1)
        self.date_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_months()
        self.date_month.setFixedWidth(140)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1)

        self.day_lbl = QLabel(self)
        self.day_lbl.setFont(font14)
        self.layout_type.addWidget(self.day_lbl, 0, 5, 1, 1)

        if not self.year_lbl.text():
            self.year_lbl.setText('Год:')
            self.month_lbl.setText('    Месяц:')
            self.day_lbl.setText('    День:')

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet1)
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
        self.socnet_choose.setStyleSheet(stylesheet1)
        self.layout_type.addWidget(self.socnet_choose, 0, 1, 1, 1)
        socnets = PhotoDataDB.get_socialnetworks()

        if not socnets:
            self.socnet_choose.addItem('Нет данных')
            self.socnet_choose.setFixedWidth(150)
        else:
            socnet_max_len = 0
            for net in socnets:
                self.socnet_choose.addItem(f'{net}')
                if len(net) > socnet_max_len:
                    socnet_max_len = len(net)

            self.socnet_choose.setFixedWidth(socnet_max_len*15)

            self.socnet_choose.currentTextChanged.connect(self.type_show_thumbnails)

            self.sn_status = QComboBox(self)
            self.sn_status.setFont(font14)
            self.sn_status.setFixedHeight(30)
            self.sn_status.setStyleSheet(stylesheet1)
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
        self.camera_choose.setStyleSheet(stylesheet1)
        self.lens_choose = QComboBox(self)
        self.lens_choose.setFont(font14)
        self.lens_choose.setFixedHeight(30)
        self.lens_choose.setStyleSheet(stylesheet1)
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

        self.camera_choose.setFixedWidth(camera_max_len*15)
        self.lens_choose.setFixedWidth(lens_max_len*15)

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


# подтвердить удаление фото
class DelPhotoConfirm(QDialog):
    clear_info = QtCore.pyqtSignal()

    def __init__(self, photoname, photodirectory):
        super(DelPhotoConfirm, self).__init__()

        self.photoname = photoname
        self.photodirectory = photodirectory

        self.setWindowTitle('Подтверждение удаления')
        self.resize(400, 100)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.lbl = QLabel()
        self.lbl.setText(f'Вы точно хотите удалить {self.photoname}?')
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.lbl.setFont(QtGui.QFont('Times', 12))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttonBox.button(QDialogButtonBox.Ok).setText('Подтверждение')
        buttonBox.button(QDialogButtonBox.Cancel).setText('Отмена')
        buttonBox.setFont(QtGui.QFont('Times', 12))

        self.layout.addWidget(buttonBox, 1, 0, 1, 1)

        buttonBox.accepted.connect(lambda: self.do_del(photoname, photodirectory))
        buttonBox.rejected.connect(self.reject)

    # при подтверждении - удалить фото, его миниатюру и записи в БД
    def do_del(self, photoname: str, photodirectory: str) -> None:
        os.remove(photodirectory + '/' + photoname)
        Thumbnail.delete_thumbnail_const(photoname, photodirectory)
        PhotoDataDB.del_from_databese(photoname, photodirectory)
        self.clear_info.emit()
        self.accept()


# редактирование exif
class EditExifData(QDialog):

    edited_signal = QtCore.pyqtSignal()
    edited_signal_no_move = QtCore.pyqtSignal()
    movement_signal = QtCore.pyqtSignal(str, str, str)

    def __init__(self, parent, photoname, photodirectory, chosen_group_type):
        super().__init__(parent)
        self.setWindowTitle('Редактирование метаданных')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.photoname = photoname
        self.photodirectory = photodirectory
        self.chosen_group_type = chosen_group_type

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.layout.addWidget(self.table, 0, 0, 1, 1)

        self.indicator = 0
        self.get_metadata(photoname, photodirectory)

        self.table.itemDoubleClicked.connect(self.pre_edit)
        self.table.itemChanged.connect(lambda: self.write_changes(photoname, photodirectory))

    # редактировать только после двойного нажатия (иначе обновление данных вызовет вечную рекурсию)
    def pre_edit(self) -> None:
        self.indicator = 1

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname, photodirectory) -> None:

        own_dir = os.getcwd()
        data = Metadata.exif_show_edit(photoname, photodirectory, own_dir)

        self.table.setColumnCount(2)
        self.table.setRowCount(len(data))
        keys = list(data.keys())
        self.table.setFont(QtGui.QFont('Times', 10))

        for parameter in range(len(data)):
            self.table.setItem(parameter, 0, QTableWidgetItem(keys[parameter]))
            self.table.item(parameter, 0).setFlags(Qt.ItemIsEditable)
            self.table.setItem(parameter, 1, QTableWidgetItem(data[keys[parameter]]))

        self.table.setStyleSheet('color: black')
        self.table.resizeColumnsToContents()
        self.resize(self.table.columnWidth(0) + self.table.columnWidth(1) + 80, 500)

    # записать новые метаданные
    def write_changes(self, photoname: str, photodirectory: str) -> None:
        # Перезаписать в exif и БД новые метаданные
        def rewriting(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_rewrite_edit(photoname, photodirectory, editing_type, new_text, own_dir)
            PhotoDataDB.edit_in_database(photoname, photodirectory, editing_type, new_text)

        # проверка введённых пользователем метаданных
        def check_enter(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_check_edit(photoname, photodirectory, editing_type, new_text, own_dir)

        # Если изменение метаданных в таблице - дело рук программы, а не пользователя (не было предшествующего двойного нажатия)
        if self.indicator == 0:
            pass
        else:
            own_dir = os.getcwd()
            editing_type = self.table.currentRow()
            new_text = self.table.currentItem().text()

            # проверка введённых пользователем метаданных
            try:
                check_enter(photoname, photodirectory, editing_type, new_text, own_dir)
            except Metadata.EditExifError:
                win_err = ErrorsAndWarnings.EditExifError(self)
                win_err.show()
                # self.get_metadata(photoname, photodirectory)
                return

            # Если меняется дата -> проверка на перенос файла в новую папку
            if editing_type == 9:
                if photodirectory[-12:] == 'No_Date_Info':
                    new_date = photodirectory[-38:]
                else:
                    new_date = photodirectory[-10:]
                old_date = new_text[:10]
                new_date_splitted = new_date.split('/')
                old_date_splitted = old_date.split(':')
                if new_date_splitted == old_date_splitted:  # если дата та же, переноса не требуется
                    rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
                    self.indicator = 0
                    self.get_metadata(photoname, photodirectory)
                    self.edited_signal_no_move.emit()
                else:   # другая дата, требуется перенос файла
                    destination = Settings.get_destination_media() + '/Media/Photo/const'
                    year_new = new_date_splitted[0]
                    month_new = new_date_splitted[1]
                    day_new = new_date_splitted[2]

                    year_old = old_date_splitted[0]
                    month_old = old_date_splitted[1]
                    day_old = old_date_splitted[2]
                    old_file_dir = destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old)
                    old_file_fullname = old_file_dir + '/' + photoname
                    new_file_fullname = destination + '/' + str(year_new) + '/' + str(month_new) + '/' + str(day_new) + '/' + photoname
                    if not os.path.isdir(destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old)): # папки назначения нет -> сравнивать не надо
                        if not os.path.isdir(destination + '/' + str(year_old)):
                            os.mkdir(destination + '/' + str(year_old))
                        if not os.path.isdir(destination + '/' + str(year_old) + '/' + str(month_old)):
                            os.mkdir(destination + '/' + str(year_old) + '/' + str(month_old))
                        os.mkdir(destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old))
                        rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
                        shutil.move(new_file_fullname, destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old))
                        PhotoDataDB.catalog_after_transfer(photoname, destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old),
                                                           destination + '/' + str(year_new) + '/' + str(month_new) + '/' + str(day_new))
                        Thumbnail.transfer_diff_date_thumbnail(photoname, new_date_splitted, old_date_splitted)
                        if self.chosen_group_type == 'Дата':
                            self.movement_signal.emit(year_old, month_old, day_old)
                        else:
                            pass
                            # надо обновить метаданные на экране, но проблема в том, что файл уже у другой папке и надо
                            # заново присвоить ему objectName, чтобы снять с его метаданные
                        self.close()
                    else:
                        if not os.path.exists(destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old) + '/' + photoname):
                            rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
                            shutil.move(new_file_fullname, destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old))
                            PhotoDataDB.catalog_after_transfer(photoname, destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old),
                                                               destination + '/' + str(year_new) + '/' + str(month_new) + '/' + str(day_new))
                            Thumbnail.transfer_diff_date_thumbnail(photoname, new_date_splitted, old_date_splitted)
                            if self.chosen_group_type == 'Дата':
                                self.movement_signal.emit(year_old, month_old, day_old)
                            else:
                                pass
                                # надо обновить метаданные на экране, но проблема в том, что файл уже у другой папке и надо
                                # заново присвоить ему objectName, чтобы снять с его метаданные
                            self.close()

                        else:
                            window_equal = EqualNames(self, photoname, old_date_splitted, new_date_splitted, new_text)
                            window_equal.show()
                            if self.chosen_group_type == 'Дата':
                                window_equal.file_rename_transfer_signal.connect(lambda: self.movement_signal.emit(year_old, month_old, day_old))
                            else:
                                pass

                            window_equal.file_rename_transfer_signal.connect(lambda: self.close())

            elif editing_type == 1 or editing_type ==2:
                rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
                self.edited_signal.emit()
            else:
                rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
                self.edited_signal_no_move.emit()

            self.indicator = 0


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
        self.filesname = filesname
        self.old_date = old_date
        self.new_date = new_date

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.text_lbl = QLabel(self)
        self.text_lbl.setText('В каталоге уже есть файл с такими же датой съёмки и именем. Что делать?')
        self.layout.addWidget(self.text_lbl, 0, 0, 1, 4)

        self.old_top_lbl = QLabel(self)
        self.old_top_lbl.setText('Фото уже существующее в папке')
        self.layout.addWidget(self.old_top_lbl, 1, 0, 1, 2)

        self.new_top_lbl = QLabel(self)
        self.new_top_lbl.setText('Фото перемещаемое из-за изменения даты')
        self.layout.addWidget(self.new_top_lbl, 1, 2, 1, 2)

        self.pic_old = QLabel(self)
        self.layout.addWidget(self.pic_old, 2, 0, 1, 2)

        self.pic_new = QLabel(self)
        self.layout.addWidget(self.pic_new, 2, 2, 1, 2)

        self.old_checkbox = QCheckBox(self)
        self.old_checkbox.setObjectName('old_checkbox')
        self.layout.addWidget(self.old_checkbox, 3, 0, 1, 1)

        self.old_name = QLineEdit(self)
        self.old_name.setText(filesname)
        self.layout.addWidget(self.old_name, 3, 1, 1, 1)
        self.old_name.setDisabled(True)

        self.new_checkbox = QCheckBox(self)
        self.new_checkbox.setObjectName('new_checkbox')
        self.layout.addWidget(self.new_checkbox, 3, 2, 1, 1)
        self.new_checkbox.setCheckState(2)

        self.new_name = QLineEdit(self)
        self.new_name.setText(filesname)
        self.layout.addWidget(self.new_name, 3, 3, 1, 1)

        self.old_checkbox.stateChanged.connect(self.check_disable)
        self.new_checkbox.stateChanged.connect(self.check_disable)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Переименовать')
        self.layout.addWidget(self.btn_ok, 4, 0, 1, 2)
        self.btn_ok.clicked.connect(lambda: self.ok_check(self.new_name.text(), self.old_name.text()))


        self.btn_cnl = QPushButton(self)
        self.btn_cnl.setText('Не переносить (отменить изменение даты)')
        self.layout.addWidget(self.btn_cnl, 4, 3, 1, 2)
        self.btn_cnl.clicked.connect(lambda: self.close())

        self.show_photos()

    # показать в уменьшенном виде 2 фото, у которых совпали названия
    def show_photos(self) -> None:
        self.old_photo_dir = Settings.get_destination_media() + '/Media/Photo/const/' + f'{self.old_date[0]}/{self.old_date[1]}/{self.old_date[2]}/'
        self.new_photo_dir = Settings.get_destination_media() + '/Media/Photo/const/' + f'{self.new_date[0]}/{self.new_date[1]}/{self.new_date[2]}/'
        pixmap_old = QtGui.QPixmap(self.old_photo_dir + self.filesname).scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        pixmap_new = QtGui.QPixmap(self.new_photo_dir + self.filesname).scaled(300, 300, QtCore.Qt.KeepAspectRatio)
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
            new_new_name = self.new_name.text()

            if os.path.exists(self.old_photo_dir + new_new_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)
                err_win.show()
                return

            os.rename(self.new_photo_dir + self.filesname, self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg')
            shutil.move(self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir)
            os.rename(self.old_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir + new_new_name)

            PhotoDataDB.filename_after_transfer(self.filesname, new_enter_text, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 0)
            Thumbnail.transfer_equal_date_thumbnail(self.filesname, self.filesname, self.old_date, self.new_date, new_new_name, 'new')
            Metadata.exif_rewrite_edit(new_new_name, self.old_photo_dir, 9, self.full_exif_date, os.getcwd())
            PhotoDataDB.edit_in_database(new_new_name, self.old_photo_dir[:-1], 9, self.full_exif_date)
        else:       # переименовывается файл в папке назначения
            new_old_name = self.old_name.text()

            if os.path.exists(self.old_photo_dir + new_old_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)
                err_win.show()
                return

            os.rename(self.old_photo_dir + self.filesname, self.old_photo_dir + new_old_name)
            shutil.move(self.new_photo_dir + self.filesname, self.old_photo_dir)
            PhotoDataDB.filename_after_transfer(self.filesname, old_enter_text, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 1)
            Thumbnail.transfer_equal_date_thumbnail(self.filesname, self.filesname, self.old_date, self.new_date, new_old_name, 'old')
            Metadata.exif_rewrite_edit(self.filesname, self.old_photo_dir, 9, self.full_exif_date, os.getcwd())
            PhotoDataDB.edit_in_database(self.filesname, self.old_photo_dir[:-1], 9, self.full_exif_date)
        self.file_rename_transfer_signal.emit()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ConstWidgetWindow()
    form.show()
    app.exec_()
