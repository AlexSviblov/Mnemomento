import logging
import math
import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from math import ceil
from PyQt5.QtCore import Qt
from PIL import Image       # type: ignore[import]
import Screenconfig
import Metadata
import Settings
import Thumbnail
import ErrorsAndWarnings
import json


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


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


# noinspection PyUnresolvedReferences,PyArgumentList
class WidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self, photo_list: list[str]):
        super().__init__()
        self.stylesheet_color()
        self.setStyleSheet(stylesheet2)

        self.own_dir = os.getcwd()
        self.photo_list = photo_list
        self.photo_directory = self.make_photo_dir(self.photo_list)

        self.layoutoutside = QGridLayout(self)
        self.layoutoutside.setSpacing(10)

        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.pic = QtWidgets.QLabel()  # создание объекта большой картинки
        self.pic.hide()
        self.pic.setAlignment(Qt.AlignCenter)

        self.scroll_area_widget = QScrollArea(self)  # создание подвижной области
        self.layoutoutside.addWidget(self.scroll_area_widget, 0, 0, 2, 1)  # помещение подвижной области на слой
        self.layout_inside_thumbs = QGridLayout(self)  # создание внутреннего слоя для подвижной области
        self.groupbox_thumbs = QGroupBox(self)  # создание группы объектов для помещения в него кнопок
        self.groupbox_thumbs.setStyleSheet(stylesheet1)
        self.groupbox_thumbs.setLayout(self.layout_inside_thumbs)
        self.scroll_area_widget.setWidget(self.groupbox_thumbs)
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)  # задание размеров подвижной области и её внутренностей

        self.scroll_area_widget.setFixedWidth(200*self.thumb_row)
        self.scroll_area_widget.setWidgetResizable(True)
        self.scroll_area_widget.setWidget(self.groupbox_thumbs)
        self.scroll_area_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_widget.setStyleSheet(stylesheet2)

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

        self.last_clicked = ''

        self.layout_btns = QGridLayout(self)
        self.layout_btns.setSpacing(0)

        self.make_buttons()

        self.groupbox_btns = QGroupBox(self)
        self.groupbox_btns.setLayout(self.layout_btns)
        self.groupbox_btns.setStyleSheet(stylesheet2)
        self.groupbox_btns.setFixedSize(70, 160)
        self.layoutoutside.addWidget(self.groupbox_btns, 0, 2, 1, 1)

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
        self.layoutoutside.addWidget(self.photo_show, 0, 1, 1, 1)

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

        try:
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll_area_widget.setStyleSheet(stylesheet2)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.photo_show.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.edit_btn.setStyleSheet(stylesheet1)
            self.setStyleSheet(stylesheet2)
            self.show_thumbnails()
            self.make_buttons()
        except AttributeError:
            pass

    # функция отображения кнопок с миниатюрами
    def show_thumbnails(self) -> None:
        for i in reversed(range(self.layout_inside_thumbs.count())):
            self.layout_inside_thumbs.itemAt(i).widget().deleteLater()

        self.thumbnails_list = list()

        for file in os.listdir(Settings.get_destination_thumb() + '/thumbnail/view/'):  # получение списка созданных миниатюр
            if file.endswith(".jpg") or file.endswith(".JPG"):
                self.thumbnails_list.append(file)

        num_of_j = ceil(len(self.thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(self.thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    self.button = QtWidgets.QToolButton(self)  # создание кнопки
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(Settings.get_destination_thumb() + f'/thumbnail/view/{self.thumbnails_list[j * self.thumb_row + i]}')  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)  # помещение картинки на кнопку
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{self.thumbnails_list[j * self.thumb_row + i][10:]}')  # добавление названия фото
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.clicked.connect(self.showinfo)
            else:
                for i in range(0, self.thumb_row):
                    self.button = QtWidgets.QToolButton(self)
                    self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(Settings.get_destination_thumb() + f'/thumbnail/view/{self.thumbnails_list[j * self.thumb_row + i]}')
                    iqon.pixmap(150, 150)
                    self.button.setMinimumHeight(180)
                    self.button.setFixedWidth(160)
                    self.button.setIcon(iqon)
                    self.button.setIconSize(QtCore.QSize(150, 150))
                    self.button.setText(f'{self.thumbnails_list[j * self.thumb_row + i][10:]}')
                    self.layout_inside_thumbs.addWidget(self.button, j, i, 1, 1)
                    self.button.clicked.connect(self.showinfo)

    # функция показа большой картинки
    def showinfo(self) -> None:
        try:
            self.button_text = self.sender().text() # type: ignore[attr-defined]
        except AttributeError:
            if self.last_clicked == '':
                return
            else:
                self.button_text = self.last_clicked

        self.last_clicked = self.button_text

        self.pic.clear()  # очистка от того, что показано сейчас

        # self.photo_file = 'C:/Users/user/Pictures/IMG_0454.jpg'
        self.photo_file = self.photo_directory + self.button_text  # получение информации о нажатой кнопке

        pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif(Metadata.read_exif(self.photo_file), self.button_text, self.photo_directory)

        self.photo_rotation = metadata['Rotation']  # 'ver' or 'gor'
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
                self.metadata_show.setItem(r, 0, QTableWidgetItem(str(params[i])))
                self.metadata_show.setItem(r, 1, QTableWidgetItem(str(metadata[params[i]])))
                r += 1
                if len(metadata[params[i]]) > max_len:
                    max_len = len(metadata[params[i]])

        self.metadata_show.setColumnWidth(1, max_len*12)

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)


        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.metadata_show, 1, 1, 1, 1)
            self.metadata_show.show()

            self.pixmap2 = pixmap.scaled(self.size().width() - self.scroll_area_widget.width() - self.groupbox_btns.width(),
                                    self.size().height() - self.metadata_show.height(), QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
            self.pic.show()
            self.set_minimum_size.emit(self.scroll_area_widget.width() + self.pixmap2.width() + self.groupbox_btns.width() + 60)
        else: # self.photo_rotation == 'ver'
            self.layout_show.addWidget(self.metadata_show, 1, 1, 1, 1)
            self.metadata_show.show()
            self.pixmap2 = pixmap.scaled(self.size().width() - - self.scroll_area_widget.width() - self.groupbox_btns.width() -
                                    self.metadata_show.width(), self.size().height() - 50, QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
            self.pic.show()
            self.set_minimum_size.emit(self.scroll_area_widget.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)

        self.oldsize = self.size()

    # в класс передаётся список файлов, надо получить их директорию
    def make_photo_dir(self, photo_list: list[str]) -> str:
        photo_splitted = photo_list[0].split('/')
        photo_dir = ''
        for i in range(0, len(photo_splitted)-1):
            photo_dir += photo_splitted[i] + '/'

        return photo_dir

    # Действия при изменении размеров окна
    def resizeEvent(self, QResizeEvent):
        self.resized_signal.emit()

    def resize_func(self) -> None:
        raznost = self.oldsize - self.size()
        if abs(raznost.width()) + abs(raznost.height()) < 300:
            pass
        else:
            self.showinfo()

    # создание кнопки редактирования
    def make_buttons(self) -> None:
        self.edit_btn = QToolButton(self)
        self.edit_btn.setIcon(QtGui.QIcon(icon_edit))
        self.edit_btn.setIconSize(QtCore.QSize(50, 50))
        self.edit_btn.setToolTip("Редактирование метаданных")
        # self.edit_btn.setText('RED')
        self.edit_btn.setStyleSheet(stylesheet1)
        self.edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.edit_btn, 0, 0, 1, 1)
        self.edit_btn.clicked.connect(self.edit_photo_func)

        self.explorer_btn = QToolButton(self)
        self.explorer_btn.setStyleSheet(stylesheet1)
        self.explorer_btn.setIcon(QtGui.QIcon(icon_explorer))
        self.explorer_btn.setIconSize(QtCore.QSize(50, 50))
        self.explorer_btn.setToolTip("Показать в проводнике")
        # self.explorer_btn.setText('EXP')
        self.explorer_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.explorer_btn, 1, 0, 1, 1)
        self.explorer_btn.clicked.connect(self.call_explorer)

        self.open_file_btn = QToolButton(self)
        self.open_file_btn.setStyleSheet(stylesheet1)
        self.open_file_btn.setIcon(QtGui.QIcon(icon_view))
        self.open_file_btn.setIconSize(QtCore.QSize(50, 50))
        self.open_file_btn.setToolTip("Открыть")
        # self.open_file_btn.setText('OPN')
        self.open_file_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.open_file_btn, 2, 0, 1, 1)
        self.open_file_btn.clicked.connect(self.open_file_func)

    # функция редактирования
    def edit_photo_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.button_text
        photodirectory = self.photo_directory[:-1]
        dialog_edit = EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory)
        dialog_edit.show()
        dialog_edit.edited_signal.connect(self.showinfo)

    # открыть фотографию в приложении просмотра
    def open_file_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        path = self.photo_file  # 'C:/Users/user/Pictures/IMG_0454.jpg'
        os.startfile(path)

    # показать фото в проводнике
    def call_explorer(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        open_path = self.photo_file # 'C:/Users/user/Pictures/IMG_0454.jpg'
        path = open_path.replace('/', '\\')
        exp_str = f'explorer /select,\"{path}\"'
        os.system(exp_str)

    # обновить дизайн при изменении настроек
    def after_change_settings(self) -> None:
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll_area_widget.setFixedWidth(200 * self.thumb_row)

        self.show_thumbnails()


# редактирование exif
# noinspection PyArgumentList
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

        self.layout.addWidget(self.table, 0, 1, 1, 2)

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
        self.btn_cancel.clicked.connect(self.close)

        self.btn_clear = QPushButton(self)
        self.btn_clear.setText("Очистить")
        self.btn_clear.setStyleSheet(stylesheet8)
        self.btn_clear.setFont(font14)
        self.layout.addWidget(self.btn_clear, 1, 2, 1, 1)
        self.btn_clear.clicked.connect(self.clear_exif_func)

        self.make_tabs_gui()

        self.layout.addWidget(self.tabs, 0, 0, 1, 1)

        self.get_metadata(photoname, photodirectory)
        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # создание всего GUI в разделе, где можно редактировать метаданные
    # noinspection PyUnresolvedReferences
    def make_tabs_gui(self) -> None:
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
        self.timezone_pm_choose.setStyleSheet(stylesheet9)
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
        self.tab_tt_layout.addWidget(self.serialbody_lbl, 9, 0, 1, 1)
        self.tab_tt_layout.addWidget(self.seriallens_lbl, 10, 0, 1, 1)

        self.maker_line = QLineEdit(self)

        self.camera_line = QLineEdit(self)

        self.lens_line = QLineEdit(self)

        self.time_line = QLineEdit(self)
        self.time_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d+[./]\d+')))

        self.iso_line = QLineEdit(self)
        self.iso_line.setValidator(QtGui.QIntValidator(1, 10000000))

        self.fnumber_line = QLineEdit(self)
        self.fnumber_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d+[.]\d+')))

        self.flength_line = QLineEdit(self)
        self.flength_line.setValidator(QtGui.QIntValidator(1, 10000))

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

        self.latitude_fn_line = QLineEdit(self)     # широта
        self.latitude_fn_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$')))
        self.longitude_fn_line = QLineEdit(self)    # долгота
        self.longitude_fn_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$')))


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
        self.latitude_dmc_deg_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:90|[0-9]|[1-8][0-9])')))

        self.latitude_dmc_min_line = QLineEdit(self)  # широта
        self.latitude_dmc_min_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:60|[0-9]|[1-5][0-9])')))

        self.latitude_dmc_sec_line = QLineEdit(self)  # широта
        self.latitude_dmc_sec_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^(?:60(?:(?:\.0{1,6})?)|(?:[0-9]|[1-5][0-9])(?:(?:\.[0-9]{1,6})?))$')))

        self.longitude_dmc_deg_line = QLineEdit(self)  # долгота
        self.longitude_dmc_deg_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:180|[0-9]|[1-9][0-9]|1[0-7][0-9])')))

        self.longitude_dmc_min_line = QLineEdit(self)  # долгота
        self.longitude_dmc_min_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:60|[0-9]|[1-5][0-9])')))

        self.longitude_dmc_sec_line = QLineEdit(self)  # долгота
        self.longitude_dmc_sec_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^(?:60(?:(?:\.0{1,6})?)|(?:[0-9]|[1-5][0-9])(?:(?:\.[0-9]{1,6})?))$')))

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
        self.latitude_dmc_choose.setStyleSheet(stylesheet9)

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
        self.longitude_dmc_choose.setStyleSheet(stylesheet9)

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

        self.mode_check_fn.setCheckState(Qt.Checked)

        self.date_choose.dateTimeChanged.connect(lambda: self.changes_to_indicator(11))
        self.timezone_pm_choose.currentTextChanged.connect(lambda: self.changes_to_indicator(8))
        self.timezone_num_choose.timeChanged.connect(lambda: self.changes_to_indicator(8))
        self.latitude_fn_line.textChanged.connect(lambda: self.changes_to_indicator(7))
        self.longitude_fn_line.textChanged.connect(lambda: self.changes_to_indicator(7))

        self.maker_line.textChanged.connect(lambda: self.changes_to_indicator(0))
        self.camera_line.textChanged.connect(lambda: self.changes_to_indicator(1))
        self.lens_line.textChanged.connect(lambda: self.changes_to_indicator(2))
        self.time_line.textChanged.connect(lambda: self.changes_to_indicator(3))
        self.iso_line.textChanged.connect(lambda: self.changes_to_indicator(4))
        self.fnumber_line.textChanged.connect(lambda: self.changes_to_indicator(5))
        self.flength_line.textChanged.connect(lambda: self.changes_to_indicator(6))
        self.serialbody_line.textChanged.connect(lambda: self.changes_to_indicator(9))
        self.seriallens_line.textChanged.connect(lambda: self.changes_to_indicator(10))

    # Если поле было изменено, в списке "индикатор" меняется значение с индексом, соответствующем полю, с 0 на 1
    def changes_to_indicator(self, index: int) -> None:
        try:
            self.indicator[index] = 1
        except (IndexError, AttributeError):
            pass

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname: str, photodirectory: str) -> None:
        own_dir = os.getcwd()
        data = Metadata.exif_show_edit(photodirectory + '/' + photoname)

        # Дата и время съёмки из формата exif в формат QDateTime
        def date_convert(data: dict[str, str]) -> tuple[int, int, int, int, int, int, str, int, int]:
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

        # изменение размеров окна
        def func_resize() -> None:
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setFixedHeight(1)
            self.table.setFixedSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 2,
                                    self.table.rowCount() * self.table.rowHeight(0))
            self.tabs.setFixedHeight(self.table.height())

            self.setMinimumSize(self.table.columnWidth(0) + self.table.columnWidth(1) + 650,
                                self.table.rowCount() * self.table.rowHeight(0) + self.btn_ok.height() + 60)

        # заполнить поля второй вкладки
        def fill_equip_set() -> None:
            self.maker_line.setText(str(data['Производитель']))
            self.camera_line.setText(str(data['Камера']))
            self.lens_line.setText(str(data['Объектив']))
            self.time_line.setText(str(data['Выдержка']))
            self.iso_line.setText(str(data['ISO']))
            self.fnumber_line.setText(str(data['Диафрагма']))
            self.flength_line.setText(str(data['Фокусное расстояние']))
            self.serialbody_line.setText(str(data['Серийный номер камеры']))
            self.seriallens_line.setText(str(data['Серийный номер объектива']))

        # заполнить вкладку GPS
        def fill_gps() -> None:
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
            self.table.setItem(parameter, 0, QTableWidgetItem(str(keys[parameter])))
            self.table.item(parameter, 0).setFlags(Qt.ItemIsEditable)
            self.table.setItem(parameter, 1, QTableWidgetItem(str(data[keys[parameter]])))

        year, month, day, hour, minute, second, zone_pm, zone_hour, zone_min = date_convert(data)

        date_show = QtCore.QDateTime(year, month, day, hour, minute, second)
        self.date_choose.setDateTime(date_show)

        time_zone_show = QtCore.QTime(zone_hour, zone_min)

        self.timezone_pm_choose.setCurrentText(zone_pm)
        self.timezone_num_choose.setTime(time_zone_show)

        fill_equip_set()
        fill_gps()

        func_resize()

    # при изменении координат GPS в одном из вариантов ввода, поменять в соответствие и другую
    def updating_other_gps(self) -> None:
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

    # считать все поля ввода
    def read_enter(self) -> list[str]:
        maker = self.maker_line.text()
        camera = self.camera_line.text()
        lens = self.lens_line.text()
        time = self.time_line.text()
        iso = self.iso_line.text()
        fnumber = self.fnumber_line.text()
        flenght = self.flength_line.text()
        serialbody = self.serialbody_line.text()
        seriallens = self.seriallens_line.text()

        timezone = self.timezone_pm_choose.currentText() + self.timezone_num_choose.text()
        datetime = self.date_choose.text().replace(".", ":")

        gps = self.latitude_fn_line.text() + ", " + self.longitude_fn_line.text()

        all_meta_entered = [maker, camera, lens, time, iso, fnumber, flenght, gps, timezone,
                            serialbody, seriallens, datetime]

        return all_meta_entered

    # блокировать/разблокировать элементы ввода GPS при выборе разных вариантов ввода
    def block_check_gps(self) -> None:
        if self.sender().text() == "ШД Г.м.с":  # type: ignore[attr-defined]
            if self.mode_check_dmc.checkState() == 2:
                self.mode_check_fn.setCheckState(Qt.Unchecked)
            else:
                self.mode_check_fn.setCheckState(Qt.Checked)

        elif self.sender().text() == "Числом":  # type: ignore[attr-defined]
            if self.mode_check_fn.checkState() == 2:
                self.mode_check_dmc.setCheckState(Qt.Unchecked)
            else:
                self.mode_check_dmc.setCheckState(Qt.Checked)

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

    # процесс записи exif в файл, в обёртке управления "индикатором" и учитывая, было ли изменение даты (для GUI)
    def pre_write_changes(self) -> None:
        all_new_data = self.read_enter()
        for i in range(len(all_new_data)):
            if self.indicator[i] == 1:
                self.write_changes(self.photoname, self.photodirectory, i, all_new_data[i])
            else:
                pass

        if self.indicator[-1] == 0:
            self.get_metadata(self.photoname, self.photodirectory)
        else:
            self.close()

        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # записать новые метаданные
    def write_changes(self, photoname: str, photodirectory: str, editing_type, new_text) -> None:
        # Перезаписать в exif и БД новые метаданные
        def rewriting(photoname: str, photodirectory: str, editing_type: int, new_text: str) -> None:
            Metadata.exif_rewrite_edit(photoname, photodirectory, editing_type, new_text)

        # проверка введённых пользователем метаданных
        def check_enter(editing_type: int, new_text: str) -> None:
            Metadata.exif_check_edit(editing_type, new_text)

        own_dir = os.getcwd()

        # проверка введённых пользователем метаданных
        try:
            check_enter(editing_type, new_text)
        except ErrorsAndWarnings.EditExifError:
            logging.error(f"Invalid try to rewrite metadata {photoname}, {photodirectory}, {editing_type}, {new_text}")
            win_err = ErrorsAndWarnings.EditExifError_win(self)
            win_err.show()
            return

        rewriting(photoname, photodirectory, editing_type, new_text)
        self.edited_signal.emit()

    # очистка exif
    def clear_exif_func(self) -> None:
        def accepted():
            Metadata.clear_exif(self.photoname, self.photodirectory)
            self.get_metadata(self.photoname, self.photodirectory)
            self.edited_signal.emit()

        def rejected():
            win.close()

        win = ConfirmClear(self.parent())
        win.show()
        win.accept_signal.connect(accepted)
        win.reject_signal.connect(rejected)


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
