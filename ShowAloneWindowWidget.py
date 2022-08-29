import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
import math
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
    add_photo_signal = QtCore.pyqtSignal()
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.stylesheet_color()

        self.own_dir = os.getcwd()

        self.setWindowTitle("Тестовое окно")

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
        self.layoutoutside.addWidget(self.scroll, 1, 0, 2, 1)  # помещение подвижной области на слой
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
        self.sn_status.setFixedWidth(164)
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
        self.layoutoutside.addWidget(self.photo_show, 1, 1, 2, 3)

        self.btn_add_photos = QPushButton(self)
        self.btn_add_photos.setText("Добавить файлы")
        self.btn_add_photos.setFont(font12)
        self.btn_add_photos.setStyleSheet(stylesheet1)
        self.layout_directory_choose.addWidget(self.btn_add_photos, 0, 6, 1, 1)
        self.btn_add_photos.clicked.connect(self.add_photo_func)

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet6
        global stylesheet7
        global stylesheet8

        if Settings.get_theme_color() == 'light':
            stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0"
            stylesheet2 = "border: 0px; color: #000000; background-color: #F0F0F0"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}"
            stylesheet6 = "QTableView{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;gridline-color: #A9A9A9;}"
            stylesheet7 = "QTabWidget::pane {border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}" \
                          "QTabBar::tab {border: 1px; border-color: #A9A9A9; border-style: solid; padding: 5px; color: #000000; min-width: 12em;} " \
                          "QTabBar::tab:selected {border: 2px; border-color: #A9A9A9; border-style: solid; margin-top: -2px; background-color: #C0C0C0; color: #000000;}"
            stylesheet8 = "QPushButton{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0}" \
                          "QPushButton::pressed{background-color: #D0D0D0; margin-top: -2px}"


        else:   #Settings.get_theme_color() == 'dark'
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #1c1c1c"
            stylesheet3 = r"QHeaderView::section{border: 1px; border-color: #696969; border-style: solid; background-color: #1c1c1c; color: #D3D3D3;}"
            stylesheet6 = "QTableView{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1c1c1c; gridline-color: #696969;}"
            stylesheet7 = "QTabWidget::pane {border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C;  color: #D3D3D3}" \
                          "QTabBar::tab {border: 1px; border-color: #696969; border-style: solid; padding: 5px; color: #D3D3D3; min-width: 12em;} " \
                          "QTabBar::tab:selected {border: 2px; border-color: #6A6A6A; border-style: solid; margin-top: -2px; background-color: #1F1F1F; color: #D3D3D3}"
            stylesheet8 = "QPushButton{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C}" \
                          "QPushButton::pressed{background-color: #1D1D1D; margin-top: -2px}"

        try:
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll.setStyleSheet(stylesheet2)
            self.groupbox_sort.setStyleSheet(stylesheet2)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.socnet_group.setStyleSheet(stylesheet6)
            self.photo_show.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.edit_btn.setStyleSheet(stylesheet1)
            self.del_btn.setStyleSheet(stylesheet1)
            self.explorer_btn.setStyleSheet(stylesheet1)
            self.open_file_btn.setStyleSheet(stylesheet1)
            self.setStyleSheet(stylesheet2)
            self.group_type.setStyleSheet(stylesheet1)
            self.set_sort_layout()

            self.type_show_thumbnails()
        except AttributeError:
            pass

    # показать/скрыть фильтры по соцсетям
    def filter_on_off(self):
        self.socnet_choose.clear()
        if self.photo_filter.checkState() == 0:
            self.socnet_choose.hide()
            self.sn_status.hide()
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
                    self.socnet_choose.setFixedWidth(net_max_length*12+30)
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

        self.photo_file = self.photo_directory + '/' + self.button_text  # получение информации о нажатой кнопке

        jsondata_wr = {'last_opened_photo': self.photo_file}
        with open('last_opened.json', 'w') as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif(Metadata.read_exif(self.button_text, self.photo_directory, self.own_dir), self.button_text, self.photo_directory)

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
        photodirectory = self.photo_directory
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
        photodirectory = self.photo_directory
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
        dir_to_del = self.photo_directory
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
            PhotoDataDB.edit_sn_tags(photoname, photodirectory, new_status_bd, network)
            if self.photo_filter.checkState() == 2:
                self.show_thumbnails()

        sn_names, sn_tags = PhotoDataDB.get_social_tags(photoname, photodirectory)

        fill_sn_widgets(sn_names, sn_tags)

    def after_change_settings(self):
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll.setFixedWidth(200 * self.thumb_row)

        self.show_thumbnails()

    def add_photo_func(self):
        self.add_photo_signal.emit()


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
        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Редактирование метаданных')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.photoname = photoname
        self.photodirectory = photodirectory

        self.layout = QGridLayout(self)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setFont(font12)
        self.table.setDisabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet(stylesheet3)
        self.table.setStyleSheet(stylesheet6)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.table, 0, 1, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText("Записать")
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.pre_write_changes)

        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText("Отмена")
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.btn_cancel.setFont(font14)
        self.layout.addWidget(self.btn_cancel, 1, 1, 1, 1)

        self.make_tabs_gui()

        self.layout.addWidget(self.tabs, 0, 0, 1, 1)

        self.get_metadata(photoname, photodirectory)
        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def make_tabs_gui(self):
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet(stylesheet7)
        self.tab_date = QWidget(self)
        self.tab_technic_settings = QWidget(self)
        self.tab_GPS = QWidget(self)

        self.tabs.addTab(self.tab_date, 'Дата')
        self.tabs.addTab(self.tab_technic_settings, 'Оборудование и настройки')
        self.tabs.addTab(self.tab_GPS, 'GPS')

        self.tabs.setFont(font12)

        self.tab_date_layout = QGridLayout(self)

        self.date_lbl = QLabel(self)
        self.date_lbl.setStyleSheet(stylesheet2)
        self.date_lbl.setText("Дата съёмки:")
        self.date_lbl.setFont(font14)
        self.date_lbl.setStyleSheet(stylesheet2)
        self.tab_date_layout.addWidget(self.date_lbl, 0, 0, 1, 1)

        self.date_choose = QDateTimeEdit(self)
        self.date_choose.setDisplayFormat("yyyy.MM.dd HH:mm:ss")
        self.date_choose.setFont(font14)
        self.date_choose.setStyleSheet(stylesheet1)
        self.tab_date_layout.addWidget(self.date_choose, 0, 1, 1, 2)

        self.timezone_lbl = QLabel(self)
        self.timezone_lbl.setStyleSheet(stylesheet2)
        self.timezone_lbl.setText("Часовой пояс:")
        self.timezone_lbl.setFont(font14)
        self.timezone_lbl.setStyleSheet(stylesheet2)
        self.tab_date_layout.addWidget(self.timezone_lbl, 1, 0, 1, 1)

        self.timezone_pm_choose = QComboBox(self)
        self.timezone_pm_choose.setFont(font14)
        self.timezone_pm_choose.setStyleSheet(stylesheet1)
        self.timezone_pm_choose.addItem("+")
        self.timezone_pm_choose.addItem("-")
        self.timezone_pm_choose.setFixedWidth(50)
        self.tab_date_layout.addWidget(self.timezone_pm_choose, 1, 1, 1, 1)

        self.timezone_num_choose = QTimeEdit(self)
        self.timezone_num_choose.setFont(font14)
        self.timezone_num_choose.setStyleSheet(stylesheet1)
        self.timezone_num_choose.setDisplayFormat("HH:mm")
        self.tab_date_layout.addWidget(self.timezone_num_choose, 1, 2, 1, 1)

        self.tab_date.setLayout(self.tab_date_layout)

        self.tab_tt_layout = QGridLayout(self)

        self.maker_lbl = QLabel(self)
        self.maker_lbl.setText("Производитель:")

        self.camera_lbl = QLabel(self)
        self.camera_lbl.setText("Камера:")

        self.lens_lbl = QLabel(self)
        self.lens_lbl.setText("Объектив:")

        self.time_lbl = QLabel(self)
        self.time_lbl.setText("Выдержка:")

        self.iso_lbl = QLabel(self)
        self.iso_lbl.setText("ISO:")

        self.fnumber_lbl = QLabel(self)
        self.fnumber_lbl.setText("Диафрагма:")

        self.flength_lbl = QLabel(self)
        self.flength_lbl.setText("Фокусное расстояние:")

        self.cammode_lbl = QLabel(self)
        self.cammode_lbl.setText("Режим съёмки:")

        self.flashmode_lbl = QLabel(self)
        self.flashmode_lbl.setText("Режим вспышки:")

        self.serialbody_lbl = QLabel(self)
        self.serialbody_lbl.setText("Серийный номер камеры:")

        self.seriallens_lbl = QLabel(self)
        self.seriallens_lbl.setText("Серийный номер объектива:")

        self.maker_lbl.setStyleSheet(stylesheet2)
        self.maker_lbl.setFont(font12)

        self.camera_lbl.setStyleSheet(stylesheet2)
        self.camera_lbl.setFont(font12)

        self.lens_lbl.setStyleSheet(stylesheet2)
        self.lens_lbl.setFont(font12)

        self.time_lbl.setStyleSheet(stylesheet2)
        self.time_lbl.setFont(font12)

        self.iso_lbl.setStyleSheet(stylesheet2)
        self.iso_lbl.setFont(font12)

        self.fnumber_lbl.setStyleSheet(stylesheet2)
        self.fnumber_lbl.setFont(font12)

        self.flength_lbl.setStyleSheet(stylesheet2)
        self.flength_lbl.setFont(font12)

        self.cammode_lbl.setStyleSheet(stylesheet2)
        self.cammode_lbl.setFont(font12)

        self.flashmode_lbl.setStyleSheet(stylesheet2)
        self.flashmode_lbl.setFont(font12)

        self.serialbody_lbl.setStyleSheet(stylesheet2)
        self.serialbody_lbl.setFont(font12)

        self.seriallens_lbl.setStyleSheet(stylesheet2)
        self.seriallens_lbl.setFont(font12)

        self.tab_tt_layout.addWidget(self.maker_lbl, 0, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.camera_lbl, 1, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.lens_lbl, 2, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.time_lbl, 3, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.iso_lbl, 4, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.fnumber_lbl, 5, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.flength_lbl, 6, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.cammode_lbl, 7, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.flashmode_lbl, 8, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.serialbody_lbl, 9, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.seriallens_lbl, 10, 0, 1, 1)

        self.maker_line = QLineEdit(self)

        self.camera_line = QLineEdit(self)

        self.lens_line = QLineEdit(self)

        self.time_line = QLineEdit(self)

        self.iso_line = QLineEdit(self)

        self.fnumber_line = QLineEdit(self)

        self.flength_line = QLineEdit(self)

        self.cammode_line = QLineEdit(self)

        self.flashmode_line = QLineEdit(self)

        self.serialbody_line = QLineEdit(self)

        self.seriallens_line = QLineEdit(self)

        self.maker_line.setStyleSheet(stylesheet1)
        self.maker_line.setFont(font12)

        self.camera_line.setStyleSheet(stylesheet1)
        self.camera_line.setFont(font12)

        self.lens_line.setStyleSheet(stylesheet1)
        self.lens_line.setFont(font12)

        self.time_line.setStyleSheet(stylesheet1)
        self.time_line.setFont(font12)

        self.iso_line.setStyleSheet(stylesheet1)
        self.iso_line.setFont(font12)

        self.fnumber_line.setStyleSheet(stylesheet1)
        self.fnumber_line.setFont(font12)

        self.flength_line.setStyleSheet(stylesheet1)
        self.flength_line.setFont(font12)

        self.cammode_line.setStyleSheet(stylesheet1)
        self.cammode_line.setFont(font12)

        self.flashmode_line.setStyleSheet(stylesheet1)
        self.flashmode_line.setFont(font12)

        self.serialbody_line.setStyleSheet(stylesheet1)
        self.serialbody_line.setFont(font12)

        self.seriallens_line.setStyleSheet(stylesheet1)
        self.seriallens_line.setFont(font12)

        self.tab_tt_layout.addWidget(self.maker_line, 0, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.camera_line, 1, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.lens_line, 2, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.time_line, 3, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.iso_line, 4, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.fnumber_line, 5, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.flength_line, 6, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.cammode_line, 7, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.flashmode_line, 8, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.serialbody_line, 9, 1, 1, 1)
        self.tab_tt_layout.addWidget(self.seriallens_line, 10, 1, 1, 1)

        self.tab_technic_settings.setLayout(self.tab_tt_layout)

        self.tab_layout_gps = QGridLayout(self)

        self.mode_check_dmc = QCheckBox(self)
        self.mode_check_dmc.setText("ШД Г.м.с")
        self.mode_check_dmc.setFont(font12)
        self.mode_check_dmc.setStyleSheet(stylesheet2)
        self.mode_check_dmc.stateChanged.connect(self.block_check_gps)

        self.mode_check_fn = QCheckBox(self)
        self.mode_check_fn.setText("Числом")
        self.mode_check_fn.setFont(font12)
        self.mode_check_fn.setStyleSheet(stylesheet2)
        self.mode_check_fn.stateChanged.connect(self.block_check_gps)

        self.latitude_fn_lbl = QLabel(self)  # широта
        self.latitude_fn_lbl.setText("Широта:")

        self.longitude_fn_lbl = QLabel(self)  # долгота
        self.longitude_fn_lbl.setText("Долгота:")

        self.latitude_fn_line = QLineEdit(self)  # широта
        self.longitude_fn_line = QLineEdit(self)  # долгота

        self.latitude_fn_lbl.setFont(font12)
        self.longitude_fn_lbl.setFont(font12)
        self.latitude_fn_line.setFont(font12)
        self.longitude_fn_line.setFont(font12)

        self.latitude_fn_lbl.setStyleSheet(stylesheet2)
        self.longitude_fn_lbl.setStyleSheet(stylesheet2)
        self.latitude_fn_line.setStyleSheet(stylesheet1)
        self.longitude_fn_line.setStyleSheet(stylesheet1)

        self.tab_layout_gps.addWidget(self.mode_check_fn, 0, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_fn_lbl, 1, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_fn_line, 1, 1, 1, 7)
        self.tab_layout_gps.addWidget(self.longitude_fn_lbl, 2, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_fn_line, 2, 1, 1, 7)

        self.longitude_fn_line.textChanged.connect(self.updating_other_gps)
        self.latitude_fn_line.textChanged.connect(self.updating_other_gps)

        self.latitude_dmc_lbl = QLabel(self)  # широта
        self.latitude_dmc_lbl.setText("Широта:")

        self.longitude_dmc_lbl = QLabel(self)  # долгота
        self.longitude_dmc_lbl.setText("Долгота:")

        self.latitude_dmc_choose = QComboBox(self)
        self.latitude_dmc_choose.addItem("Север")
        self.latitude_dmc_choose.addItem("Юг")
        self.latitude_dmc_choose.setFixedWidth(80)

        self.longitude_dmc_choose = QComboBox(self)
        self.longitude_dmc_choose.addItem("Восток")
        self.longitude_dmc_choose.addItem("Запад")
        self.longitude_dmc_choose.setFixedWidth(80)

        self.latitude_dmc_deg_lbl = QLabel(self)  # широта
        self.latitude_dmc_deg_lbl.setText("Градусы:")

        self.longitude_dmc_min_lbl = QLabel(self)  # долгота
        self.longitude_dmc_min_lbl.setText("Минуты:")

        self.latitude_dmc_sec_lbl = QLabel(self)  # широта
        self.latitude_dmc_sec_lbl.setText("Секунды:")

        self.longitude_dmc_deg_lbl = QLabel(self)  # долгота
        self.longitude_dmc_deg_lbl.setText("Градусы:")

        self.latitude_dmc_min_lbl = QLabel(self)  # широта
        self.latitude_dmc_min_lbl.setText("Минуты:")

        self.longitude_dmc_sec_lbl = QLabel(self)  # долгота
        self.longitude_dmc_sec_lbl.setText("Секунды:")

        self.latitude_dmc_deg_line = QLineEdit(self)  # широта

        self.latitude_dmc_min_line = QLineEdit(self)  # долгота

        self.latitude_dmc_sec_line = QLineEdit(self)  # широта

        self.longitude_dmc_deg_line = QLineEdit(self)  # долгота

        self.longitude_dmc_min_line = QLineEdit(self)  # широта

        self.longitude_dmc_sec_line = QLineEdit(self)  # долгота

        self.tab_layout_gps.addWidget(self.mode_check_dmc, 3, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_lbl, 4, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_choose, 4, 1, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_deg_lbl, 4, 2, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_deg_line, 4, 3, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_min_lbl, 4, 4, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_min_line, 4, 5, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_sec_lbl, 4, 6, 1, 1)
        self.tab_layout_gps.addWidget(self.latitude_dmc_sec_line, 4, 7, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_lbl, 5, 0, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_choose, 5, 1, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_deg_lbl, 5, 2, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_deg_line, 5, 3, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_min_lbl, 5, 4, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_min_line, 5, 5, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_sec_lbl, 5, 6, 1, 1)
        self.tab_layout_gps.addWidget(self.longitude_dmc_sec_line, 5, 7, 1, 1)

        self.mode_check_dmc.setFont(font12)
        self.mode_check_dmc.setStyleSheet(stylesheet2)

        self.latitude_dmc_lbl.setFont(font12)
        self.latitude_dmc_lbl.setStyleSheet(stylesheet2)

        self.latitude_dmc_choose.setFont(font12)
        self.latitude_dmc_choose.setStyleSheet(stylesheet1)

        self.latitude_dmc_deg_lbl.setFont(font12)
        self.latitude_dmc_deg_lbl.setStyleSheet(stylesheet2)

        self.latitude_dmc_deg_line.setFont(font12)
        self.latitude_dmc_deg_line.setStyleSheet(stylesheet1)

        self.latitude_dmc_min_lbl.setFont(font12)
        self.latitude_dmc_min_lbl.setStyleSheet(stylesheet2)

        self.latitude_dmc_min_line.setFont(font12)
        self.latitude_dmc_min_line.setStyleSheet(stylesheet1)

        self.latitude_dmc_sec_lbl.setFont(font12)
        self.latitude_dmc_sec_lbl.setStyleSheet(stylesheet2)

        self.latitude_dmc_sec_line.setFont(font12)
        self.latitude_dmc_sec_line.setStyleSheet(stylesheet1)

        self.longitude_dmc_lbl.setFont(font12)
        self.longitude_dmc_lbl.setStyleSheet(stylesheet2)

        self.longitude_dmc_choose.setFont(font12)
        self.longitude_dmc_choose.setStyleSheet(stylesheet1)

        self.longitude_dmc_deg_lbl.setFont(font12)
        self.longitude_dmc_deg_lbl.setStyleSheet(stylesheet2)

        self.longitude_dmc_deg_line.setFont(font12)
        self.longitude_dmc_deg_line.setStyleSheet(stylesheet1)

        self.longitude_dmc_min_lbl.setFont(font12)
        self.longitude_dmc_min_lbl.setStyleSheet(stylesheet2)

        self.longitude_dmc_min_line.setFont(font12)
        self.longitude_dmc_min_line.setStyleSheet(stylesheet1)

        self.longitude_dmc_sec_lbl.setFont(font12)
        self.longitude_dmc_sec_lbl.setStyleSheet(stylesheet2)

        self.longitude_dmc_sec_line.setFont(font12)
        self.longitude_dmc_sec_line.setStyleSheet(stylesheet1)

        self.latitude_dmc_choose.currentTextChanged.connect(self.updating_other_gps)
        self.longitude_dmc_choose.currentTextChanged.connect(self.updating_other_gps)
        self.latitude_dmc_deg_line.textChanged.connect(self.updating_other_gps)
        self.latitude_dmc_min_line.textChanged.connect(self.updating_other_gps)
        self.latitude_dmc_sec_line.textChanged.connect(self.updating_other_gps)
        self.longitude_dmc_deg_line.textChanged.connect(self.updating_other_gps)
        self.longitude_dmc_min_line.textChanged.connect(self.updating_other_gps)
        self.longitude_dmc_sec_line.textChanged.connect(self.updating_other_gps)

        self.tab_GPS.setLayout(self.tab_layout_gps)

        self.mode_check_fn.setCheckState(2)

        self.date_choose.dateTimeChanged.connect(lambda: self.changes_to_indicator(13))
        self.timezone_pm_choose.currentTextChanged.connect(lambda: self.changes_to_indicator(10))
        self.timezone_num_choose.timeChanged.connect(lambda: self.changes_to_indicator(10))
        self.latitude_fn_line.textChanged.connect(lambda: self.changes_to_indicator(9))
        self.longitude_fn_line.textChanged.connect(lambda: self.changes_to_indicator(9))

        self.maker_line.textChanged.connect(lambda: self.changes_to_indicator(0))
        self.camera_line.textChanged.connect(lambda: self.changes_to_indicator(1))
        self.lens_line.textChanged.connect(lambda: self.changes_to_indicator(2))
        self.time_line.textChanged.connect(lambda: self.changes_to_indicator(3))
        self.iso_line.textChanged.connect(lambda: self.changes_to_indicator(4))
        self.fnumber_line.textChanged.connect(lambda: self.changes_to_indicator(5))
        self.flength_line.textChanged.connect(lambda: self.changes_to_indicator(6))
        self.cammode_line.textChanged.connect(lambda: self.changes_to_indicator(7))
        self.flashmode_line.textChanged.connect(lambda: self.changes_to_indicator(8))
        self.serialbody_line.textChanged.connect(lambda: self.changes_to_indicator(11))
        self.seriallens_line.textChanged.connect(lambda: self.changes_to_indicator(12))

    def changes_to_indicator(self, index):
        try:
            self.indicator[index] = 1
        except (IndexError, AttributeError):
            pass

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname, photodirectory) -> None:
        own_dir = os.getcwd()
        data = Metadata.exif_show_edit(photoname, photodirectory, own_dir)

        def date_convert(data):
            try:
                date_part = data['Время съёмки'].split(' ')[0]
                time_part = data['Время съёмки'].split(' ')[1]
            except IndexError:
                date_part = "0000:00:00"
                time_part = "00:00:00"

            year = int(date_part.split(":")[0])
            month = int(date_part.split(":")[1])
            day = int(date_part.split(":")[2])
            hour = int(time_part.split(":")[0])
            minute = int(time_part.split(":")[1])
            second = int(time_part.split(":")[2])

            try:
                zone_pm = data['Часовой пояс'][0]
                zone_hour = int(data['Часовой пояс'][1:].split(':')[0])
                zone_min = int(data['Часовой пояс'][1:].split(':')[1])
            except IndexError:
                zone_pm = "+"
                zone_hour = int("00")
                zone_min = int("00")

            return year, month, day, hour, minute, second, zone_pm, zone_hour, zone_min

        def func_resize():
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setFixedHeight(1)
            self.table.setFixedSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 2,
                                    self.table.rowCount() * self.table.rowHeight(0))
            self.tabs.setFixedHeight(self.table.height())

            self.setMinimumSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 650,
                                self.table.rowCount() * self.table.rowHeight(0) + self.btn_ok.height() + 50)

        def fill_equip_set():
            self.maker_line.setText(data['Производитель'])
            self.camera_line.setText(data['Камера'])
            self.lens_line.setText(data['Объектив'])
            self.time_line.setText(data['Выдержка'])
            self.iso_line.setText(data['ISO'])
            self.fnumber_line.setText(data['Диафрагма'])
            self.flength_line.setText(data['Фокусное расстояние'])
            self.cammode_line.setText(data['Режим съёмки'])
            self.flashmode_line.setText(data['Режим вспышки'])
            self.serialbody_line.setText(data['Серийный номер камеры'])
            self.seriallens_line.setText(data['Серийный номер объектива'])

        def fill_gps():
            coords_all = data['Координаты']
            try:
                latitude_part = float(coords_all.split(',')[0])
                longitude_part = float(coords_all.split(',')[1])
            except ValueError:
                latitude_part = 0
                longitude_part = 0

            self.latitude_fn_line.setText(str(latitude_part))
            self.longitude_fn_line.setText(str(longitude_part))

            if latitude_part < 0:
                self.latitude_dmc_choose.setCurrentText("Юг")
            else:
                self.latitude_dmc_choose.setCurrentText("Север")

            if longitude_part < 0:
                self.longitude_dmc_choose.setCurrentText("Запад")
            else:
                self.longitude_dmc_choose.setCurrentText("Восток")

            latitude_deg = math.trunc(abs(latitude_part))
            longitude_deg = math.trunc(abs(longitude_part))

            latitude_min = math.trunc((abs(latitude_part) - latitude_deg) * 60)
            longitude_min = math.trunc((abs(longitude_part) - longitude_deg) * 60)

            latitude_sec = round((((abs(latitude_part) - latitude_deg) * 60) - latitude_min) * 60, 3)
            longitude_sec = round((((abs(longitude_part) - longitude_deg) * 60) - longitude_min) * 60, 3)

            self.latitude_dmc_deg_line.setText(str(latitude_deg))
            self.latitude_dmc_min_line.setText(str(latitude_min))
            self.latitude_dmc_sec_line.setText(str(latitude_sec))
            self.longitude_dmc_deg_line.setText(str(longitude_deg))
            self.longitude_dmc_min_line.setText(str(longitude_min))
            self.longitude_dmc_sec_line.setText(str(longitude_sec))

        self.table.setColumnCount(2)
        self.table.setRowCount(len(data))
        keys = list(data.keys())

        for parameter in range(len(data)):
            self.table.setItem(parameter, 0, QTableWidgetItem(keys[parameter]))
            self.table.item(parameter, 0).setFlags(Qt.ItemIsEditable)
            self.table.setItem(parameter, 1, QTableWidgetItem(data[keys[parameter]]))

        year, month, day, hour, minute, second, zone_pm, zone_hour, zone_min = date_convert(data)

        date_show = QtCore.QDateTime(year, month, day, hour, minute, second)
        self.date_choose.setDateTime(date_show)

        time_zone_show = QtCore.QTime(zone_hour, zone_min)

        self.timezone_pm_choose.setCurrentText(zone_pm)
        self.timezone_num_choose.setTime(time_zone_show)

        fill_equip_set()
        fill_gps()

        func_resize()

    def updating_other_gps(self):
        if self.mode_check_dmc.checkState() == 2:
            latitude_ref = self.latitude_dmc_choose.currentText()
            longitude_ref = self.longitude_dmc_choose.currentText()
            latitude_deg = float(self.latitude_dmc_deg_line.text())
            longitude_deg = float(self.longitude_dmc_deg_line.text())
            latitude_min = float(self.latitude_dmc_min_line.text())
            longitude_min = float(self.longitude_dmc_min_line.text())
            latitude_sec = float(self.latitude_dmc_sec_line.text())
            longitude_sec = float(self.longitude_dmc_sec_line.text())

            if latitude_ref == "Юг":
                latitude_pm_coe = -1
            else:  # latitude_ref == "Север"
                latitude_pm_coe = 1

            if longitude_ref == "Восток":
                longitude_pm_coe = 1
            else:  # latitude_ref == "Запад"
                longitude_pm_coe = -1

            latitude = round((latitude_pm_coe * (latitude_deg + latitude_min / 60 + latitude_sec / 3600)), 6)
            longitude = round(longitude_pm_coe * (longitude_deg + longitude_min / 60 + longitude_sec / 3600), 6)

            self.latitude_fn_line.setText(str(latitude))
            self.longitude_fn_line.setText(str(longitude))

        else:  # self.mode_check_fn.checkState() == 2
            try:
                latitude = float(self.latitude_fn_line.text())
                longitude = float(self.longitude_fn_line.text())
            except ValueError:
                latitude = 0
                longitude = 0

            if latitude > 0:
                self.latitude_dmc_choose.setCurrentText("Север")
            else:
                self.latitude_dmc_choose.setCurrentText("Юг")

            if longitude > 0:
                self.longitude_dmc_choose.setCurrentText("Восток")
            else:
                self.longitude_dmc_choose.setCurrentText("Запад")

            latitude_deg = math.trunc(abs(latitude))
            longitude_deg = math.trunc(abs(longitude))

            latitude_min = math.trunc((abs(latitude) - latitude_deg) * 60)
            longitude_min = math.trunc((abs(longitude) - longitude_deg) * 60)

            latitude_sec = round((((abs(latitude) - latitude_deg) * 60) - latitude_min) * 60, 3)
            longitude_sec = round((((abs(longitude) - longitude_deg) * 60) - longitude_min) * 60, 3)

            self.latitude_dmc_deg_line.setText(str(latitude_deg))
            self.latitude_dmc_min_line.setText(str(latitude_min))
            self.latitude_dmc_sec_line.setText(str(latitude_sec))
            self.longitude_dmc_deg_line.setText(str(longitude_deg))
            self.longitude_dmc_min_line.setText(str(longitude_min))
            self.longitude_dmc_sec_line.setText(str(longitude_sec))

    def read_enter(self):
        maker = self.maker_line.text()
        camera = self.camera_line.text()
        lens = self.lens_line.text()
        time = self.time_line.text()
        iso = self.iso_line.text()
        fnumber = self.fnumber_line.text()
        flenght = self.flength_line.text()
        cammode = self.cammode_line.text()
        flashmode = self.flashmode_line.text()
        serialbody = self.serialbody_line.text()
        seriallens = self.seriallens_line.text()

        timezone = self.timezone_pm_choose.currentText() + self.timezone_num_choose.text()
        datetime = self.date_choose.text().replace(".", ":")

        gps = self.latitude_fn_line.text() + ", " + self.longitude_fn_line.text()

        all_meta_entered = [maker, camera, lens, time, iso, fnumber, flenght, cammode, flashmode, gps, timezone,
                            serialbody, seriallens, datetime]

        return all_meta_entered

    def block_check_gps(self):
        if self.sender().text() == "ШД Г.м.с":
            if self.mode_check_dmc.checkState() == 2:
                self.mode_check_fn.setCheckState(0)
            else:
                self.mode_check_fn.setCheckState(2)

        elif self.sender().text() == "Числом":
            if self.mode_check_fn.checkState() == 2:
                self.mode_check_dmc.setCheckState(0)
            else:
                self.mode_check_dmc.setCheckState(2)

        if self.mode_check_fn.checkState() == 2:
            self.longitude_fn_line.setDisabled(False)
            self.latitude_fn_line.setDisabled(False)
            self.latitude_dmc_choose.setDisabled(True)
            self.longitude_dmc_choose.setDisabled(True)
            self.latitude_dmc_deg_line.setDisabled(True)
            self.latitude_dmc_min_line.setDisabled(True)
            self.latitude_dmc_sec_line.setDisabled(True)
            self.longitude_dmc_deg_line.setDisabled(True)
            self.longitude_dmc_min_line.setDisabled(True)
            self.longitude_dmc_sec_line.setDisabled(True)
        elif self.mode_check_dmc.checkState() == 2:
            self.longitude_fn_line.setDisabled(True)
            self.latitude_fn_line.setDisabled(True)
            self.latitude_dmc_choose.setDisabled(False)
            self.longitude_dmc_choose.setDisabled(False)
            self.latitude_dmc_deg_line.setDisabled(False)
            self.latitude_dmc_min_line.setDisabled(False)
            self.latitude_dmc_sec_line.setDisabled(False)
            self.longitude_dmc_deg_line.setDisabled(False)
            self.longitude_dmc_min_line.setDisabled(False)
            self.longitude_dmc_sec_line.setDisabled(False)

    def pre_write_changes(self):
        all_new_data = self.read_enter()
        for i in range(len(all_new_data)):
            print(i)
            print(len(self.indicator))
            if self.indicator[i] == 1:
                self.write_changes(self.photoname, self.photodirectory, i, all_new_data[i])
            else:
                pass

        if self.indicator[-1] == 0:
            self.get_metadata(self.photoname, self.photodirectory)
        else:
            self.close()

        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # записать новые метаданные
    def write_changes(self, photoname: str, photodirectory: str, editing_type, new_text) -> None:
        # Перезаписать в exif и БД новые метаданные
        def rewriting(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_rewrite_edit(photoname, photodirectory, editing_type, new_text, own_dir)
            PhotoDataDB.edit_in_database(photoname, photodirectory, editing_type, new_text)

        # проверка введённых пользователем метаданных
        def check_enter(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_check_edit(photoname, photodirectory, editing_type, new_text, own_dir)

        own_dir = os.getcwd()

        # проверка введённых пользователем метаданных
        try:
            check_enter(photoname, photodirectory, editing_type, new_text, own_dir)
        except Metadata.EditExifError:
            win_err = ErrorsAndWarnings.EditExifError(self)
            win_err.show()
            return

        rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
        self.edited_signal.emit()


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
