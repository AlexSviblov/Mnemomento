import logging
import os
import folium
import json
import math
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

import EditFiles
import FilesDirs
import PhotoDataDB
import Metadata
import Screenconfig
import Settings
import Thumbnail


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


system_scale = Screenconfig.monitor_info()[1]


class AloneWidgetWindow(QWidget):
    add_photo_signal = QtCore.pyqtSignal(str)
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.stylesheet_color()

        self.own_dir = os.getcwd()
        self.setMaximumSize(Screenconfig.monitor_info()[0][0], Screenconfig.monitor_info()[0][1] - 63)

        self.setStyleSheet(stylesheet2)

        self.layoutoutside = QGridLayout(self)
        self.layoutoutside.setSpacing(10)

        self.thumb_row = Settings.get_thumbs_row()
        self.soc_net_setting = Settings.get_socnet_status()

        self.pic = QtWidgets.QLabel()  # создание объекта большой картинки
        self.pic.hide()
        self.pic.setAlignment(Qt.AlignCenter)

        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

        self.scroll_area = QScrollArea(self)  # создание подвижной области
        self.layoutoutside.addWidget(self.scroll_area, 1, 0, 2, 1)  # помещение подвижной области на слой
        self.layout_inside_thumbs = QGridLayout(self)  # создание внутреннего слоя для подвижной области
        self.groupbox_thumbs = QGroupBox(self)  # создание группы объектов для помещения в него кнопок
        self.groupbox_thumbs.setStyleSheet(stylesheet1)
        self.groupbox_thumbs.setLayout(self.layout_inside_thumbs)
        self.scroll_area.setWidget(self.groupbox_thumbs)
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)  # задание размеров подвижной области и её внутренностей

        self.scroll_area.setFixedWidth(200*self.thumb_row)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.groupbox_thumbs)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(stylesheet2)

        self.layout_directory_choose = QGridLayout(self)
        self.layout_directory_choose.setHorizontalSpacing(5)
        self.layout_directory_choose.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.directory_lbl = QLabel(self)
        self.directory_lbl.setText('Папка для просмотра:')
        self.directory_lbl.setFixedWidth(int(200*system_scale)+1)
        self.directory_lbl.setFont(font14)
        self.directory_lbl.setStyleSheet(stylesheet2)
        self.layout_directory_choose.addWidget(self.directory_lbl, 0, 0, 1, 1)

        self.directory_choose = QComboBox(self)
        self.directory_choose.setFont(font14)
        self.directory_choose.setStyleSheet(stylesheet9)
        self.directory_choose.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.fill_directory_combobox()
        self.directory_choose.setFixedHeight(int(30*system_scale)+1)
        self.directory_choose.setFixedWidth(int((self.max_dir_name_len*12 + 40)*system_scale))
        self.layout_directory_choose.addWidget(self.directory_choose, 0, 1, 1, 1)

        self.directory_delete = QPushButton(self)
        self.directory_delete.setText('Удалить папку')
        self.directory_delete.setFont(font14)
        self.directory_delete.setStyleSheet(stylesheet8)
        self.layout_directory_choose.addWidget(self.directory_delete, 0, 2, 1, 1)
        self.directory_delete.clicked.connect(self.del_dir_func)
        self.directory_delete.setFixedWidth(int(200*system_scale)+1)

        self.photo_filter = QCheckBox(self)
        self.photo_filter.setText('Фильтр')
        self.photo_filter.setFont(font14)
        self.photo_filter.setStyleSheet(stylesheet2)
        if self.soc_net_setting:
            self.layout_directory_choose.addWidget(self.photo_filter, 0, 3, 1, 1)
            self.photo_filter.stateChanged.connect(self.filter_on_off)
        else:
            self.photo_filter.hide()

        self.socnet_choose = QComboBox(self)
        self.socnet_choose.setFont(font14)
        self.socnet_choose.setStyleSheet(stylesheet9)
        self.layout_directory_choose.addWidget(self.socnet_choose, 0, 4, 1, 1)

        self.sn_status = QComboBox(self)
        self.sn_status.setFont(font14)
        self.sn_status.setStyleSheet(stylesheet9)
        self.sn_status.addItem('Не выбрано')
        self.sn_status.addItem('Не публиковать')
        self.sn_status.addItem('Опубликовать')
        self.sn_status.addItem('Опубликовано')
        self.sn_status.setFixedWidth(int(164*system_scale)+1)
        self.layout_directory_choose.addWidget(self.sn_status, 0, 5, 1, 1)
        self.socnet_choose.currentTextChanged.connect(self.show_thumbnails)
        self.sn_status.currentTextChanged.connect(self.show_thumbnails)
        self.socnet_choose.hide()
        self.sn_status.hide()

        self.groupbox_directory_choose = QGroupBox(self)
        self.groupbox_directory_choose.setLayout(self.layout_directory_choose)
        self.groupbox_directory_choose.setMaximumHeight(int(50*system_scale)+1)
        self.groupbox_directory_choose.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.groupbox_directory_choose, 0, 0, 1, 4)

        self.metadata_show = QtWidgets.QTableWidget()
        self.metadata_show.setColumnCount(2)
        self.metadata_show.setFont(font14)
        self.metadata_show.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setDisabled(True)
        self.metadata_show.horizontalHeader().setVisible(False)
        self.metadata_show.verticalHeader().setVisible(False)
        self.metadata_header = self.metadata_show.horizontalHeader()
        self.metadata_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.metadata_show.setStyleSheet(stylesheet6)

        self.directory_choose.currentTextChanged.connect(self.show_thumbnails)

        self.last_clicked = ''

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

        self.show_thumbnails()

        self.resized_signal.connect(self.resize_func)
        self.oldsize = QtCore.QSize(0, 0)

        self.photo_show = QGroupBox(self)
        self.photo_show.setAlignment(Qt.AlignCenter)
        self.layout_show = QGridLayout(self)
        self.layout_show.setAlignment(Qt.AlignCenter)
        self.layout_show.setHorizontalSpacing(10)
        self.photo_show.setLayout(self.layout_show)
        self.photo_show.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.photo_show, 1, 1, 2, 3)

        self.btn_add_photos = QPushButton(self)
        self.btn_add_photos.setText("Добавить файлы")
        self.btn_add_photos.setFont(font14)
        self.btn_add_photos.setStyleSheet(stylesheet8)
        self.layout_directory_choose.addWidget(self.btn_add_photos, 0, 6, 1, 1)
        self.btn_add_photos.clicked.connect(self.add_files_to_dir)
        self.btn_add_photos.setFixedWidth(int(200*system_scale)+1)

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self) -> None:
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

        theme = Settings.get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f'{theme}']['stylesheet1']
        stylesheet2 = style[f'{theme}']['stylesheet2']
        stylesheet3 = style[f'{theme}']['stylesheet3']
        stylesheet6 = style[f'{theme}']['stylesheet6']
        stylesheet7 = style[f'{theme}']['stylesheet7']
        stylesheet8 = style[f'{theme}']['stylesheet8']
        stylesheet9 = style[f'{theme}']['stylesheet9']
        icon_explorer = style[f'{theme}']['icon_explorer']
        icon_view = style[f'{theme}']['icon_view']
        icon_edit = style[f'{theme}']['icon_edit']
        icon_delete = style[f'{theme}']['icon_delete']

        try:
            self.setStyleSheet(stylesheet2)
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll_area.setStyleSheet(stylesheet2)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.socnet_group.setStyleSheet(stylesheet6)
            self.photo_show.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.groupbox_directory_choose.setStyleSheet(stylesheet2)
            self.sn_status.setStyleSheet(stylesheet9)
            self.socnet_choose.setStyleSheet(stylesheet9)
            self.photo_filter.setStyleSheet(stylesheet2)
            self.directory_delete.setStyleSheet(stylesheet8)
            self.directory_choose.setStyleSheet(stylesheet9)
            self.directory_lbl.setStyleSheet(stylesheet2)
            self.btn_add_photos.setStyleSheet(stylesheet8)
            self.make_buttons()
            self.show_thumbnails()
        except AttributeError:
            pass

    # показать/скрыть фильтры по соцсетям
    def filter_on_off(self) -> None:
        self.socnet_choose.clear()
        if self.photo_filter.checkState() == 0:
            self.socnet_choose.hide()
            self.sn_status.hide()
        else:   # self.photo_filter.checkState() == 2:
            socnets = PhotoDataDB.get_socialnetworks()
            if not socnets:
                self.socnet_choose.addItem('Нет данных')
                self.sn_status.hide()
            else:
                net_max_length = 0
                for net in socnets:
                    if net[0:9] != 'numnumnum':
                        self.socnet_choose.addItem(f'{net}')
                        if len(net) > net_max_length:
                            net_max_length = len(net)
                    else:
                        self.socnet_choose.addItem(f'{net[9:]}')
                        if len(net) - 9 > net_max_length:
                            net_max_length = len(net) - 9
                    self.socnet_choose.setFixedWidth(int((net_max_length*12+30)*system_scale)+1)
            self.socnet_choose.show()
            self.sn_status.show()

    # заполнить список папок
    def fill_directory_combobox(self) -> None:
        photo_alone_dir = Settings.get_destination_media() + '/Media/Photo/alone/'
        all_files_and_dirs = os.listdir(photo_alone_dir)
        dir_list = list()
        self.max_dir_name_len = 0
        for name in all_files_and_dirs:
            if os.path.isdir(photo_alone_dir+name):
                dir_list.append(name)
                if len(name) > self.max_dir_name_len:
                    self.max_dir_name_len = len(name)

        dir_list.sort(reverse=True)
        for directory in dir_list:
            self.directory_choose.addItem(str(directory))

    # преобразование тега соцсети в формат БД
    def get_current_tag(self) -> str:
        status = self.sn_status.currentText()
        match status:
            case 'Не выбрано':
                return_status = 'No value'
            case 'Не публиковать':
                return_status = 'No publicate'
            case 'Опубликовать':
                return_status = 'Will publicate'
            case 'Опубликовано':
                return_status = 'Publicated'
        return return_status

    # функция отображения кнопок с миниатюрами
    def show_thumbnails(self) -> None:
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.pic.clear()
        self.pic.hide()
        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass

        for i in reversed(range(self.layout_inside_thumbs.count())):
            self.layout_inside_thumbs.itemAt(i).widget().deleteLater()

        self.socnet_group.clear()
        self.socnet_group.hide()

        self.chosen_directory = self.directory_choose.currentText()

        full_thumbnails_list = list()

        self.photo_directory = Settings.get_destination_media() + f'/Media/Photo/alone/{self.chosen_directory}'
        self.thumbnail_directory = Settings.get_destination_thumb() + f'/thumbnail/alone/{self.chosen_directory}'

        flaw_thumbs, excess_thumbs = Thumbnail.research_flaw_thumbnails(self.photo_directory, self.thumbnail_directory)

        Thumbnail.make_or_del_thumbnails(flaw_thumbs, excess_thumbs, self.photo_directory, self.thumbnail_directory)

        for file in os.listdir(self.thumbnail_directory):  # получение списка созданных миниатюр
            if file.endswith(".jpg") or file.endswith(".JPG"):
                full_thumbnails_list.append(file)

        thumbnails_list = list()

        if self.photo_filter.checkState() == 2:
            filtered_photo = PhotoDataDB.get_sn_alone_list(self.photo_directory, self.socnet_choose.currentText(), self.get_current_tag())

            for file in full_thumbnails_list:
                if file[10:] in filtered_photo:
                    thumbnails_list.append(file)
                else:
                    pass
        else:
            thumbnails_list = full_thumbnails_list

        num_of_j = math.ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    self.button = QtWidgets.QToolButton(self)  # создание кнопки
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(f'{self.thumbnail_directory}/{thumbnails_list[j * self.thumb_row + i]}')  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)  # помещение картинки на кнопку
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{thumbnails_list[j * self.thumb_row + i][10:]}')  # добавление названия фото
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)
                    QtCore.QCoreApplication.processEvents()
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
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.setStyleSheet(stylesheet1)
                    self.button.clicked.connect(self.showinfo)
                    QtCore.QCoreApplication.processEvents()

    def make_map(self) -> None:
        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass

        if self.gps_coordinates:
            self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()
            gps_dict = self.gps_coordinates
            gps_coords = [float(gps_dict.split(',')[0]), float(gps_dict.split(',')[1])]

            self.map_gps = folium.Map(location=gps_coords, zoom_start=14)
            folium.Marker(gps_coords, popup=self.button_text, icon=folium.Icon(color='red')).add_to(self.map_gps)
            self.map_gps_widget.setHtml(self.map_gps.get_root().render())
            if self.photo_rotation == 'gor':
                self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
                if self.soc_net_setting:
                    self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - self.socnet_group.width() - 40)
                    self.map_gps_widget.setFixedHeight(self.metadata_show.height())
                else:
                    self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - 40)
                    self.map_gps_widget.setFixedHeight(self.metadata_show.height())
            else: # self.photo_rotation == 'ver'
                self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
                if self.soc_net_setting:
                    self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                    self.map_gps_widget.setFixedHeight(self.height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - self.socnet_group.height() - 100)
                else:
                    self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                    self.map_gps_widget.setFixedHeight(
                        self.height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 100)
            self.map_gps_widget.show()
        else:
            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass

    # функция показа большой картинки
    def showinfo(self) -> None:
        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 50)

        try:
            self.button_text = self.sender().text()
        except AttributeError:
            if self.last_clicked == '':
                return
            else:
                self.button_text = self.last_clicked

        self.last_clicked = self.button_text

        self.metadata_show.clear()
        self.metadata_show.hide()

        self.pic.clear()  # очистка от того, что показано сейчас

        self.photo_file = self.photo_directory + '/' + self.button_text  # получение информации о нажатой кнопке

        jsondata_wr = {'last_opened_photo': self.photo_file}
        with open('last_opened.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        try:
            metadata = Metadata.fast_filter_exif(Metadata.fast_read_exif(self.photo_file), self.button_text, self.photo_directory)
        except (UnicodeDecodeError, UnicodeEncodeError, ValueError):
            metadata = Metadata.filter_exif(Metadata.read_exif(self.photo_file), self.button_text, self.photo_directory)

        self.photo_rotation = metadata['Rotation']

        try:
            self.gps_coordinates = metadata['GPS']
        except KeyError:
            self.gps_coordinates = ''
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
                self.metadata_show.setItem(r, 1, QTableWidgetItem(metadata[params[i]]))
                r += 1
                if len(metadata[params[i]]) > max_len:
                    max_len = len(metadata[params[i]])

        self.metadata_show.setColumnWidth(1, max_len*12)

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)

        if self.soc_net_setting:
            if self.photo_rotation == 'gor':
                self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
                self.metadata_show.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40, self.size().height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 40,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
                self.pic.show()
                self.layout_show.addWidget(self.socnet_group, 1, 2, 1, 1)
                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 60)
            else:  # self.photo_rotation == 'ver'
                self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
                self.metadata_show.show()
                self.layout_show.addWidget(self.socnet_group, 2, 1, 1, 1)
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 50, self.size().height() - self.groupbox_directory_choose.height() - 30,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
                self.pic.show()
                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)
            self.show_social_networks(self.last_clicked, self.photo_directory)
            if self.pixmap2.width() > self.metadata_show.width() + self.socnet_group.width():
                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 100)
            else:
                self.set_minimum_size.emit(self.scroll_area.width() + self.metadata_show.width() + self.socnet_group.width() + self.groupbox_btns.width() + 100)
        else:
            if self.photo_rotation == 'gor':
                self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
                self.metadata_show.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40, self.size().height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 40,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
                self.pic.show()
                if self.pixmap2.width() > self.metadata_show.width():
                    self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 60)
                else:
                    self.set_minimum_size.emit(self.scroll_area.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)
            else:  # self.photo_rotation == 'ver'
                self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
                self.metadata_show.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 50, self.size().height() - self.groupbox_directory_choose.height() - 30,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
                self.pic.show()
                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)
        QtCore.QCoreApplication.processEvents()
        self.make_map()
        self.oldsize = self.size()

    # изменить размер фото при изменении размера окна
    def resizeEvent(self, QResizeEvent):
        self.resized_signal.emit()

    # изменить размер фото при изменении размера окна
    def resize_func(self) -> None:
        self.resize_photo()
        self.resize_map()

    def resize_photo(self) -> None:
        if not self.pic.isVisible():
            return

        if self.photo_rotation == 'gor':
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40,
                self.size().height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 40,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
        else:
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 80,
                self.size().height() - self.groupbox_directory_choose.height() - 30,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)

        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 50)

    def resize_map(self) -> None:
        try:
            if not self.map_gps_widget.isVisible():
                return
            else:
                pass
        except (RuntimeError, AttributeError):
            return

        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
            if self.soc_net_setting:
                self.map_gps_widget.setFixedWidth(
                    self.pic.width() - self.metadata_show.width() - self.socnet_group.width() - 40)
                self.map_gps_widget.setFixedHeight(self.metadata_show.height())
            else:
                self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - 40)
                self.map_gps_widget.setFixedHeight(self.metadata_show.height())
        else:  # self.photo_rotation == 'ver'
            self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
            if self.soc_net_setting:
                self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                self.map_gps_widget.setFixedHeight(
                    self.height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - self.socnet_group.height() - 100)
            else:
                self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                self.map_gps_widget.setFixedHeight(
                    self.height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 100)
        self.map_gps_widget.show()

    # Создание кнопок удаления и редактирования
    def make_buttons(self) -> None:
        self.edit_btn = QToolButton(self)
        self.edit_btn.setStyleSheet(stylesheet1)
        self.edit_btn.setIcon(QtGui.QIcon(icon_edit))
        self.edit_btn.setIconSize(QtCore.QSize(50, 50))
        self.edit_btn.setToolTip("Редактирование метаданных")
        self.edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.edit_btn, 0, 0, 1, 1)
        self.edit_btn.clicked.connect(self.edit_photo_func)

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

        hotkeys = Settings.get_hotkeys()

        self.edit_shortcut = QShortcut(QKeySequence(hotkeys["edit_metadata"]), self)
        self.edit_shortcut.activated.connect(self.edit_photo_func)

        self.del_shortcut = QShortcut(QKeySequence(hotkeys["delete_file"]), self)
        self.del_shortcut.activated.connect(self.del_photo_func)

        self.explorer_shortcut = QShortcut(QKeySequence(hotkeys["open_explorer"]), self)
        self.explorer_shortcut.activated.connect(self.call_explorer)

        self.open_shortcut = QShortcut(QKeySequence(hotkeys["open_file"]), self)
        self.open_shortcut.activated.connect(self.open_file_func)

    # открыть фотографию в приложении просмотра
    def open_file_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        path = self.photo_file
        os.startfile(path)

    # показать фото в проводнике
    def call_explorer(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        open_path = self.photo_file
        path = open_path.replace('/', '\\')
        exp_str = f'explorer /select,\"{path}\"'
        os.system(exp_str)

    # удаление фото по нажатию кнопки
    def del_photo_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.button_text
        photodirectory = self.photo_directory
        dialog_del = DelPhotoConfirm(photoname, photodirectory)
        dialog_del.clear_info.connect(self.clear_after_ph_del)
        if dialog_del.exec():
            pass
            self.last_clicked = ''

    # редактирование exif
    def edit_photo_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        def renamed_re_show(new_name):
            self.show_thumbnails()

            button_text = new_name
            for i in reversed(range(self.layout_inside_thumbs.count())):
                if self.layout_inside_thumbs.itemAt(i).widget().text() == button_text:
                    self.layout_inside_thumbs.itemAt(i).widget().click()
                    break

        photoname = self.button_text
        photodirectory = self.photo_directory

        if not os.path.exists(f"{photodirectory}/{photoname}"):
            return

        dialog_edit = EditFiles.EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory, chosen_group_type='None')
        dialog_edit.show()
        dialog_edit.edited_signal.connect(self.showinfo)
        dialog_edit.renamed_signal.connect(lambda n: renamed_re_show(n))

    # убрать с экрана фото и метаданные после удаления фотографии
    def clear_after_ph_del(self) -> None:
        self.show_thumbnails()
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()

    # убрать с экрана фото и метаданные после удаления директории
    def clear_after_dir_del(self) -> None:
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.directory_choose.clear()
        self.fill_directory_combobox()

    # удаление выбранной директории
    def del_dir_func(self) -> None:
        dir_to_del = self.photo_directory
        dialog_del = DelDirConfirm(dir_to_del)
        dialog_del.clear_info.connect(self.clear_after_dir_del)
        if dialog_del.exec():
            pass

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

                self.sn_lbl.setFixedWidth(int((len(name) * 12)*system_scale)+1)
                self.socnet_group.setCellWidget(i, 0, self.sn_lbl)

                self.sn_tag_choose = QComboBox(self)
                self.sn_tag_choose.setFont(font14)
                self.sn_tag_choose.setStyleSheet(stylesheet9)
                self.sn_tag_choose.setObjectName(name)
                self.sn_tag_choose.addItem('Не выбрано')
                self.sn_tag_choose.addItem('Не публиковать')
                self.sn_tag_choose.addItem('Опубликовать')
                self.sn_tag_choose.addItem('Опубликовано')

                match sn_tags[f'{name}']:
                    case 'No value':
                        self.sn_tag_choose.setCurrentText('Не выбрано')
                    case 'No publicate':
                        self.sn_tag_choose.setCurrentText('Не публиковать')
                    case 'Will publicate':
                        self.sn_tag_choose.setCurrentText('Опубликовать')
                    case 'Publicated':
                        self.sn_tag_choose.setCurrentText('Опубликовано')

                self.sn_tag_choose.currentTextChanged.connect(edit_tags)

                self.socnet_group.setCellWidget(i, 1, self.sn_tag_choose)
                i += 1

                if self.sn_lbl.width() > self.metadata_show.columnWidth(0):
                    self.metadata_show.setColumnWidth(0, self.sn_lbl.width())

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

                self.socnet_group.setFixedWidth(self.socnet_group.columnWidth(0) + self.socnet_group.columnWidth(1) + 2)
                self.socnet_group.setFixedHeight(self.socnet_group.rowCount() * self.socnet_group.rowHeight(0) + 2)

        def edit_tags():
            match self.sender().currentText():
                case 'Не выбрано':
                    new_status_bd = 'No value'
                case 'Не публиковать':
                    new_status_bd = 'No publicate'
                case 'Опубликовать':
                    new_status_bd = 'Will publicate'
                case 'Опубликовано':
                    new_status_bd = 'Publicated'

            network = self.sender().objectName()
            PhotoDataDB.edit_sn_tags(photoname, photodirectory, new_status_bd, network)
            if self.photo_filter.checkState() == 2:
                self.show_thumbnails()

        sn_names, sn_tags = PhotoDataDB.get_social_tags(photoname, photodirectory)

        fill_sn_widgets(sn_names, sn_tags)

    # обновить дизайн при изменении настроек
    def after_change_settings(self) -> None:
        self.thumb_row = Settings.get_thumbs_row()

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll_area.setFixedWidth(200 * self.thumb_row)

        self.show_thumbnails()

    # нажатие "добавить файлы", контроль наличия хоть какой-то папки
    def add_files_to_dir(self) -> None:
        if self.directory_choose.currentText():
            self.add_photo_signal.emit(self.directory_choose.currentText())
        else:
            pass


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
        logging.info(f"File removing {photodirectory + '/' + photoname}")
        os.remove(photodirectory + '/' + photoname)
        Thumbnail.delete_thumbnail_alone(photoname, photodirectory)
        PhotoDataDB.del_from_database(photoname, photodirectory)
        self.clear_info.emit()
        self.accept()


# подтвердить удаление выбранной папки
class DelDirConfirm(QDialog):
    clear_info = QtCore.pyqtSignal()

    def __init__(self, photodirectory):
        super(DelDirConfirm, self).__init__()
        self.photodirectory = photodirectory

        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Подтверждение удаления')
        self.resize(400, 100)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.lbl = QLabel()
        dir_name = self.photodirectory.split('/')[-1]
        self.lbl.setText(f'Вы точно хотите удалить папку {dir_name}?')
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

        btn_ok.clicked.connect(self.do_del)
        btn_cancel.clicked.connect(self.reject)

    # при подтверждении - удалить всех фото из папки, его миниатюру и записи в БД
    def do_del(self) -> None:
        logging.info(f"Directory removing {self.photodirectory}")
        Thumbnail.delete_thumb_dir(self.photodirectory)
        PhotoDataDB.del_alone_dir(self.photodirectory)
        FilesDirs.del_alone_dir(self.photodirectory)

        self.clear_info.emit()
        self.accept()


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
