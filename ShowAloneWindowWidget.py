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
import FilesDirs
import PhotoDataDB
import Screenconfig
import Metadata
import Settings
import Thumbnail


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


class AloneWidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):

        super().__init__()

        self.stylesheet_color()

        self.own_dir = os.getcwd()

        self.setWindowTitle("Тестовое окно")
        self.showMaximized()

        self.setStyleSheet(stylesheet2)

        self.layoutoutside = QGridLayout(self)
        self.layoutoutside.setSpacing(10)

        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.pic = QtWidgets.QLabel()  # создание объекта большой картинки
        self.pic.hide()
        self.pic.setAlignment(Qt.AlignCenter)

        self.scroll = QScrollArea(self)  # создание подвижной области
        self.layoutoutside.addWidget(self.scroll, 1, 0, 2, 2)  # помещение подвижной области на слой
        self.layout_inside_thumbs = QGridLayout(self)  # создание внутреннего слоя для подвижной области
        self.groupbox_thumbs = QGroupBox(self)  # создание группы объектов для помещения в него кнопок
        self.groupbox_thumbs.setStyleSheet(stylesheet1)
        self.groupbox_thumbs.setLayout(self.layout_inside_thumbs)
        self.scroll.setWidget(self.groupbox_thumbs)
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)  # задание размеров подвижной области и её внутренностей

        self.scroll.setFixedWidth(200*self.thumb_row)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.groupbox_thumbs)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(stylesheet2)

        self.layout_directory_choose = QGridLayout(self)
        self.layout_directory_choose.setHorizontalSpacing(5)
        self.layout_directory_choose.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.directory_lbl = QLabel(self)
        self.directory_lbl.setText('Папка для просмотра:')
        self.directory_lbl.setFixedWidth(200)
        self.directory_lbl.setFont(font14)
        self.directory_lbl.setStyleSheet(stylesheet2)
        self.layout_directory_choose.addWidget(self.directory_lbl, 0, 0, 1, 1)

        self.directory_choose = QComboBox(self)
        self.directory_choose.setFont(font14)
        self.directory_choose.setStyleSheet(stylesheet1)
        self.directory_choose.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.fill_directory_combobox()
        self.directory_choose.setFixedHeight(30)
        self.directory_choose.setFixedWidth(self.max_dir_name_len*12 + 40)
        self.layout_directory_choose.addWidget(self.directory_choose, 0, 1, 1, 1)

        self.directory_delete = QPushButton(self)
        self.directory_delete.setText('Удалить папку')
        self.directory_delete.setFont(font14)
        self.directory_delete.setStyleSheet(stylesheet1)
        self.layout_directory_choose.addWidget(self.directory_delete, 0, 2, 1, 1)
        self.directory_delete.clicked.connect(self.del_dir_func)
        self.directory_delete.setFixedWidth(200)

        self.photo_filter = QCheckBox(self)
        self.photo_filter.setText('Фильтр')
        self.photo_filter.setFont(font14)
        self.photo_filter.setStyleSheet(stylesheet2)
        self.layout_directory_choose.addWidget(self.photo_filter, 0, 3, 1, 1)
        self.photo_filter.stateChanged.connect(self.filter_on_off)

        self.socnet_choose = QComboBox(self)
        self.socnet_choose.setFont(font14)
        self.socnet_choose.setStyleSheet(stylesheet1)
        self.layout_directory_choose.addWidget(self.socnet_choose, 0, 4, 1, 1)

        self.sn_status = QComboBox(self)
        self.sn_status.setFont(font14)
        self.sn_status.setStyleSheet(stylesheet1)
        self.sn_status.addItem('Не выбрано')
        self.sn_status.addItem('Не публиковать')
        self.sn_status.addItem('Опубликовать')
        self.sn_status.addItem('Опубликовано')
        self.layout_directory_choose.addWidget(self.sn_status, 0, 5, 1, 1)
        self.socnet_choose.currentTextChanged.connect(self.show_thumbnails)
        self.sn_status.currentTextChanged.connect(self.show_thumbnails)
        self.socnet_choose.hide()
        self.sn_status.hide()

        self.groupbox_directory_choose = QGroupBox(self)
        self.groupbox_directory_choose.setLayout(self.layout_directory_choose)
        self.groupbox_directory_choose.setMaximumHeight(50)
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
        self.layoutoutside.addWidget(self.photo_show, 1, 2, 2, 2)

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
        else:   #Settings.get_theme_color() == 'dark'
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #080808"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #080808"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #696969; border-style: solid; background-color: #080808; color: #D3D3D3;}"
            stylesheet6 = "QTableView{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #080808; gridline-color: #696969;}"

        try:
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll.setStyleSheet(stylesheet2)
            self.directory_lbl.setStyleSheet(stylesheet2)
            self.directory_choose.setStyleSheet(stylesheet1)
            self.directory_delete.setStyleSheet(stylesheet1)
            self.photo_filter.setStyleSheet(stylesheet2)
            self.socnet_choose.setStyleSheet(stylesheet1)
            self.sn_status.setStyleSheet(stylesheet1)
            self.groupbox_directory_choose.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.socnet_group.setStyleSheet(stylesheet6)
            self.photo_show.setStyleSheet(stylesheet2)
            self.show_thumbnails()
            self.edit_btn.setStyleSheet(stylesheet1)
            self.del_btn.setStyleSheet(stylesheet1)
            self.explorer_btn.setStyleSheet(stylesheet1)
            self.open_file_btn.setStyleSheet(stylesheet1)
            self.setStyleSheet(stylesheet2)
        except AttributeError:
            pass

    # показать/скрыть фильтры по соцсетям
    def filter_on_off(self):
        self.socnet_choose.clear()
        if self.photo_filter.checkState() == 0:
            self.socnet_choose.hide()
            self.sn_status.hide()
            # self.empty1.show()

        else:   # self.photo_filter.checkState() == 2:
            # self.empty1.hide()
            socnets = PhotoDataDB.get_socialnetworks()
            if not socnets:
                self.socnet_choose.addItem('Нет данных')
                self.sn_status.hide()
            else:
                net_max_length = 0
                for net in socnets:
                    self.socnet_choose.addItem(f'{net}')
                    if len(net) > net_max_length:
                        net_max_length = len(net)
                    self.socnet_choose.setFixedWidth(net_max_length*12)
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
    def get_current_tag(self):
        status = self.sn_status.currentText()
        if status == 'Не выбрано':
            return 'No value'
        elif status == 'Не публиковать':
            return 'No publicate'
        elif status == 'Опубликовать':
            return 'Will publicate'
        elif status == 'Опубликовано':
            return 'Publicated'

    # функция отображения кнопок с миниатюрами
    def show_thumbnails(self) -> None:
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.pic.clear()
        self.pic.hide()

        for i in reversed(range(self.layout_inside_thumbs.count())):
            self.layout_inside_thumbs.itemAt(i).widget().deleteLater()

        self.socnet_group.clear()
        self.socnet_group.hide()

        self.chosen_directory = self.directory_choose.currentText()

        full_thumbnails_list = list()

        self.photo_directory = Settings.get_destination_media() + f'/Media/Photo/alone/{self.chosen_directory}/'
        self.thumbnail_directory = Settings.get_destination_thumb() + f'/thumbnail/alone/{self.chosen_directory}/'

        nedostatok_thumbs, izbitok_thumbs = Thumbnail.research_need_thumbnails(self.photo_directory, self.thumbnail_directory)

        Thumbnail.make_or_del_thumbnails(nedostatok_thumbs, izbitok_thumbs, self.photo_directory, self.thumbnail_directory)

        for file in os.listdir(self.thumbnail_directory):  # получение списка созданных миниатюр
            if file.endswith(".jpg") or file.endswith(".JPG"):
                full_thumbnails_list.append(file)

        thumbnails_list = list()

        test_list = list()
        if self.photo_filter.checkState() == 2:
            filtered_photo = PhotoDataDB.get_sn_alone_list(self.photo_directory[:-1], self.socnet_choose.currentText(), self.get_current_tag())

            for file in full_thumbnails_list:
                if file[10:] in filtered_photo:
                    thumbnails_list.append(file)
                else:
                    pass
        else:
            thumbnails_list = full_thumbnails_list

        num_of_j = ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
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

    # функция показа большой картинки
    def showinfo(self) -> None:
        self.photo_show.setFixedWidth(self.width() - self.scroll.width() - self.groupbox_btns.width() - 50)

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

        self.photo_file = self.photo_directory + self.button_text  # получение информации о нажатой кнопке

        jsondata_wr = {'last_opened_photo': self.photo_file}
        with open('last_opened.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif_beta(Metadata.read_exif(self.button_text, self.photo_directory, self.own_dir), self.button_text, self.photo_directory)

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

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)

        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
            self.metadata_show.show()
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll.width() - 40, self.size().height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 40,
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
            self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll.width() - 50, self.size().height() - self.groupbox_directory_choose.height() - 30,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 2, 1)
            self.pic.show()

        self.show_social_networks(self.last_clicked, self.photo_directory)
        self.set_minimum_size.emit(self.scroll.width() + self.metadata_show.width() + self.socnet_group.width() + self.groupbox_btns.width() + 120)
        self.oldsize = self.size()

        if self.max_sn_name_len*12 > self.metadata_show.columnWidth(0):
            self.socnet_group.setColumnWidth(0, self.max_sn_name_len*12)
            self.metadata_show.setColumnWidth(0, self.max_sn_name_len*12)

            self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))
            self.socnet_group.setFixedWidth(self.socnet_group.columnWidth(0) + self.socnet_group.columnWidth(1))

    # изменить размер фото при изменении размера окна
    def resizeEvent(self, QResizeEvent):
        self.resized_signal.emit()

    # изменить размер фото при изменении размера окна
    def resize_func(self) -> None:
        self.resize_photo()

    def resize_photo(self):
        if not self.pic.isVisible():
            return

        if self.photo_rotation == 'gor':
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.groupbox_btns.width() - self.scroll.width() - 40,
                self.size().height() - self.groupbox_directory_choose.height() - self.metadata_show.height() - 40,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 2)

        else:
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll.width() - 80,
                self.size().height() - self.groupbox_directory_choose.height() - 30,
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
        self.edit_btn.clicked.connect(self.edit_photo_func)

        self.del_btn = QToolButton(self)
        self.del_btn.setStyleSheet(stylesheet1)
        # self.del_btn.setIcon()
        self.del_btn.setText('DEL')
        self.del_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.del_btn, 1, 0, 1, 1)
        self.del_btn.clicked.connect(self.del_photo_func)

        self.explorer_btn = QToolButton(self)
        self.explorer_btn.setStyleSheet(stylesheet1)
        self.explorer_btn.setText('EXP')
        self.explorer_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.explorer_btn, 2, 0, 1, 1)
        self.explorer_btn.clicked.connect(self.call_explorer)

        self.open_file_btn = QToolButton(self)
        self.open_file_btn.setStyleSheet(stylesheet1)
        self.open_file_btn.setText('OPN')
        self.open_file_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.open_file_btn, 3, 0, 1, 1)
        self.open_file_btn.clicked.connect(self.open_file_func)

    # открыть фотографию в приложении просмотра
    def open_file_func(self):
        if not self.pic.isVisible() or not self.last_clicked:
            return

        path = self.photo_file
        os.startfile(path)

    # показать фото в проводнике
    def call_explorer(self):
        if not self.pic.isVisible() or not self.last_clicked:
            return

        open_path = self.photo_file
        path = open_path.replace('/', '\\')
        exp_str = f'explorer /select,\"{path}\"'
        os.system(exp_str)

    # удаление фото по нажатию кнопки
    def del_photo_func(self):
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.button_text
        photodirectory = self.photo_directory[:-1]
        dialog_del = DelPhotoConfirm(photoname, photodirectory)
        dialog_del.clear_info.connect(self.clear_after_ph_del)
        if dialog_del.exec():
            pass
            self.last_clicked = ''
        elif dialog_del.reject():
            return

    # редактирование exif
    def edit_photo_func(self):
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.button_text
        photodirectory = self.photo_directory[:-1]
        dialog_edit = EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory)
        dialog_edit.show()
        dialog_edit.edited_signal.connect(self.showinfo)

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
    def del_dir_func(self):
        dir_to_del = self.photo_directory[:-1]
        dialog_del = DelDirConfirm(dir_to_del)
        dialog_del.clear_info.connect(self.clear_after_dir_del)
        if dialog_del.exec():
            pass
        elif dialog_del.reject():
            return

    # отображения статуса фото в соцсетях
    def show_social_networks(self, photoname: str, photodirectory: str) -> None:
        def fill_sn_widgets(sn_names: list[str, ...], sn_tags: dict) -> None:
            i = 0
            self.socnet_group.setRowCount(len(sn_names))

            self.max_sn_name_len = 0
            for name in sn_names:
                if len(name) > self.max_sn_name_len:
                    self.max_sn_name_len = len(name)

                self.sn_lbl = QLabel(self)
                self.sn_lbl.setFont(font14)
                self.sn_lbl.setStyleSheet(stylesheet2)

                if name[:9] != 'numnumnum':
                    self.sn_lbl.setText(f"{name}")
                else:
                    self.sn_lbl.setText(f"{name[9:]}")

                self.sn_lbl.setFixedWidth(len(name) * 12)
                self.socnet_group.setCellWidget(i, 0, self.sn_lbl)

                self.sn_tag_choose = QComboBox(self)
                self.sn_tag_choose.setFont(font14)
                self.sn_tag_choose.setStyleSheet(stylesheet1)
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
                    self.socnet_group_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                    self.socnet_group_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                else:
                    self.socnet_group.setColumnWidth(0, self.metadata_show.columnWidth(0))
                    self.socnet_group.setColumnWidth(1, self.metadata_show.columnWidth(1))

                self.socnet_group.setFixedWidth(self.socnet_group.columnWidth(0) + self.socnet_group.columnWidth(1) + 2)
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
            if self.photo_filter.checkState() == 2:
                self.show_thumbnails()

        sn_names, sn_tags = PhotoDataDB.get_social_tags(photoname, photodirectory[:-1])

        fill_sn_widgets(sn_names, sn_tags)

    def after_change_settings(self):
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll.setFixedWidth(200 * self.thumb_row)

        self.show_thumbnails()


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
        btn_ok.setStyleSheet(stylesheet1)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('Отмена')
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet1)

        self.layout.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(lambda: self.do_del(photoname, photodirectory))
        btn_cancel.clicked.connect(self.reject)

    # при подтверждении - удалить фото, его миниатюру и записи в БД
    def do_del(self, photoname: str, photodirectory: str) -> None:
        os.remove(photodirectory + '/' + photoname)
        Thumbnail.delete_thumbnail_alone(photoname, photodirectory)
        PhotoDataDB.del_from_databese(photoname, photodirectory)
        self.clear_info.emit()
        self.accept()


# редактирование exif
class EditExifData(QDialog):

    edited_signal = QtCore.pyqtSignal()

    def __init__(self, parent, photoname, photodirectory):
        super().__init__(parent)
        self.setWindowTitle('Редактирование метаданных')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.photoname = photoname
        self.photodirectory = photodirectory

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setFont(font12)
        self.table.verticalHeader().setVisible(False)
        # self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet(stylesheet3)
        self.table.setStyleSheet(stylesheet6)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.table, 0, 0, 1, 1, alignment=Qt.AlignCenter)

        self.indicator = 0
        self.get_metadata(photoname, photodirectory)

        self.table.itemDoubleClicked.connect(self.pre_edit)
        self.table.itemChanged.connect(lambda: self.write_changes(photoname, photodirectory))

    # редактировать только после двойного нажатия (иначе обновление данных вызовет вечную рекурсию)
    def pre_edit(self):
        self.indicator = 1

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname, photodirectory):

        own_dir = os.getcwd()
        data = Metadata.exif_show_edit(photoname, photodirectory, own_dir)

        self.table.setColumnCount(2)
        self.table.setRowCount(len(data))
        keys = list(data.keys())

        for parameter in range(len(data)):
            self.table.setItem(parameter, 0, QTableWidgetItem(keys[parameter]))
            self.table.item(parameter, 0).setFlags(Qt.ItemIsEditable)
            self.table.setItem(parameter, 1, QTableWidgetItem(data[keys[parameter]]))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setFixedHeight(1)
        self.table.setFixedSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 2, self.table.rowCount()*self.table.rowHeight(0))
        self.resize(self.table.columnWidth(0) + self.table.columnWidth(1) + 2, self.table.rowCount()*self.table.rowHeight(0))
        self.setFixedSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 50, self.table.rowCount()*self.table.rowHeight(0)+50)

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

            rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
            self.edited_signal.emit()

            # Если меняется дата -> проверка на перенос файла в новую папку
            self.indicator = 0


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
        btn_ok.setStyleSheet(stylesheet1)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('Отмена')
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet1)

        self.layout.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(self.do_del)
        btn_cancel.clicked.connect(self.reject)

    # при подтверждении - удалить всех фото из папки, его миниатюру и записи в БД
    def do_del(self) -> None:
        Thumbnail.delete_thumb_dir(self.photodirectory)
        PhotoDataDB.del_alone_dir(self.photodirectory)
        FilesDirs.del_alone_dir(self.photodirectory)

        self.clear_info.emit()
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AloneWidgetWindow()
    form.show()
    app.exec_()
