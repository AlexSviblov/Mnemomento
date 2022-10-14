import os
import sys
import folium
import json
import math
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pathlib import Path

import PhotoDataDB
import Screenconfig
import Metadata
import Settings
import Thumbnail
import EditFiles


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()
loading_icon = str()


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)
font10 = QtGui.QFont('Times', 10)
font8 = QtGui.QFont('Times', 8)


class ManyPhotoEdit(QWidget):

    def __init__(self):
        super().__init__()
        self.stylesheet_color()
        self.table_positions = dict()
        self.setWindowTitle("Редактирование метаданных")

        self.layout_outside = QGridLayout(self)
        self.setLayout(self.layout_outside)
        self.layout_outside.setSpacing(10)

        self.layout_type = QGridLayout(self)
        self.layout_type.setAlignment(Qt.AlignLeft)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(50)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.layout_outside.addWidget(self.groupbox_sort, 0, 1, 1, 4)

        self.groupbox_sort.setLayout(self.layout_type)

        self.groupbox_choose = QGroupBox(self)
        self.layout_choose = QGridLayout(self)
        self.groupbox_choose.setLayout(self.layout_choose)
        self.layout_outside.addWidget(self.groupbox_choose, 1, 0, 4, 2)

        self.filtered_photo_table = QTableWidget(self)
        self.filtered_photo_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.filtered_photo_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.filtered_photo_table.horizontalHeader().setVisible(False)
        self.filtered_photo_table.verticalHeader().setVisible(False)
        self.filtered_photo_table.setFixedWidth(264)
        self.filtered_photo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.filtered_photo_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.scroll_filtered_area = QScrollArea(self)  # создание подвижной области
        self.scroll_filtered_area.setWidgetResizable(True)
        self.scroll_filtered_area.setWidget(self.filtered_photo_table)
        self.scroll_filtered_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_filtered_area.setFixedWidth(264)
        self.scroll_filtered_area.setStyleSheet(stylesheet1)

        self.layout_choose.addWidget(self.scroll_filtered_area, 0, 0, 4, 1)

        self.edit_photo_table = QTableWidget(self)
        self.edit_photo_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit_photo_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit_photo_table.horizontalHeader().setVisible(False)
        self.edit_photo_table.verticalHeader().setVisible(False)
        self.edit_photo_table.setFixedWidth(132)
        self.edit_photo_table.setColumnCount(1)
        self.edit_photo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.edit_photo_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.scroll_edit_area = QScrollArea(self)  # создание подвижной области
        self.scroll_edit_area.setWidgetResizable(True)
        self.scroll_edit_area.setWidget(self.edit_photo_table)
        self.scroll_edit_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_edit_area.setFixedWidth(132)
        self.scroll_edit_area.setStyleSheet(stylesheet1)

        self.layout_choose.addWidget(self.scroll_edit_area, 0, 2, 4, 1)

        self.new_data_groupbox = QGroupBox(self)
        self.layout_new_data = QGridLayout(self)
        self.new_data_groupbox.setLayout(self.layout_new_data)
        self.layout_outside.addWidget(self.new_data_groupbox, 1, 2, 1, 1)
        self.new_data_groupbox.setStyleSheet(stylesheet1)

        self.empty2 = QLabel(self)
        self.layout_outside.addWidget(self.empty2, 2, 2, 1, 2)
        
        self.write_buttons_groupbox = QGroupBox(self)
        self.layout_btns = QGridLayout(self)
        self.write_buttons_groupbox.setLayout(self.layout_btns)
        self.layout_outside.addWidget(self.write_buttons_groupbox, 4, 2, 1, 2)
        self.write_buttons_groupbox.setFixedHeight(80)

        # self.compare_scroll = QScrollArea(self)
        self.table_compare = QTableWidget(self)
        self.table_compare.setFixedHeight(254)
        # self.compare_scroll.setWidget(self.table_compare)
        # self.layout_outside.addWidget(self.compare_scroll, 2, 2, 1, 2)
        self.layout_outside.addWidget(self.table_compare, 3, 2, 1, 2)
        self.make_compare_table()

        self.fill_sort_groupbox()
        self.fill_sort_date()

        self.show_filtered_thumbs()
        self.make_new_data_enter()
        self.make_buttons()

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self) -> None:
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet6
        global stylesheet7
        global stylesheet8
        global stylesheet9
        global loading_icon

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
                                QTableWidget
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0;
                                    gridline-color: #A9A9A9;
                                }
                                QTableCornerButton::section 
                                {
                                    background-color: #F0F0F0;
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
                                QTableCornerButton::section 
                                {
                                    background-color: #1c1c1c;
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
                                    color: #D3D3D3;
                                    background-color: #1C1C1C;
                                }
                                QComboBox QAbstractItemView
                                {
                                    selection-background-color: #4F4F4F;
                                }
                            """
            loading_icon = os.getcwd() + '/icons/loading_dark.gif'

        try:
            self.setStyleSheet(stylesheet2)
        except AttributeError:
            pass

    # создание элементов ввода новых данных
    def make_new_data_enter(self) -> None:
        self.new_make_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_make_check, 0, 0, 1, 1)
        self.new_make_check.setStyleSheet(stylesheet2)
        self.new_make_check.setFont(font12)

        self.new_make_line = QLineEdit(self)
        self.layout_new_data.addWidget(self.new_make_line, 0, 1, 1, 2)
        self.new_make_line.setStyleSheet(stylesheet1)
        self.new_make_line.setFont(font12)

        self.new_model_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_model_check, 1, 0, 1, 1)
        self.new_model_check.setStyleSheet(stylesheet2)
        self.new_model_check.setFont(font12)

        self.new_model_line = QLineEdit(self)
        self.layout_new_data.addWidget(self.new_model_line, 1, 1, 1, 2)
        self.new_model_line.setStyleSheet(stylesheet1)
        self.new_model_line.setFont(font12)

        self.new_lens_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_lens_check, 2, 0, 1, 1)
        self.new_lens_check.setStyleSheet(stylesheet2)
        self.new_lens_check.setFont(font12)

        self.new_lens_line = QLineEdit(self)
        self.layout_new_data.addWidget(self.new_lens_line, 2, 1, 1, 2)
        self.new_lens_line.setStyleSheet(stylesheet1)
        self.new_lens_line.setFont(font12)

        self.new_bodynum_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_bodynum_check, 3, 0, 1, 1)
        self.new_bodynum_check.setStyleSheet(stylesheet2)
        self.new_bodynum_check.setFont(font12)

        self.new_bodynum_line = QLineEdit(self)
        self.layout_new_data.addWidget(self.new_bodynum_line, 3, 1, 1, 2)
        self.new_bodynum_line.setStyleSheet(stylesheet1)
        self.new_bodynum_line.setFont(font12)

        self.new_lensnum_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_lensnum_check, 4, 0, 1, 1)
        self.new_lensnum_check.setStyleSheet(stylesheet2)
        self.new_lensnum_check.setFont(font12)

        self.new_lensnum_line = QLineEdit(self)
        self.layout_new_data.addWidget(self.new_lensnum_line, 4, 1, 1, 2)
        self.new_lensnum_line.setStyleSheet(stylesheet1)
        self.new_lensnum_line.setFont(font12)

        self.new_datetime_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_datetime_check, 5, 0, 1, 1)
        self.new_datetime_check.setStyleSheet(stylesheet2)
        self.new_datetime_check.setFont(font12)

        self.new_datetime_line = QDateTimeEdit(self)
        self.layout_new_data.addWidget(self.new_datetime_line, 5, 1, 1, 2)
        self.new_datetime_line.setDisplayFormat("yyyy.MM.dd HH:mm:ss")
        self.new_datetime_line.setStyleSheet(stylesheet1)
        self.new_datetime_line.setFont(font12)

        self.new_offset_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_offset_check, 6, 0, 1, 1)
        self.new_offset_check.setStyleSheet(stylesheet2)
        self.new_offset_check.setFont(font12)

        self.new_offset_pm_line = QComboBox(self)
        self.layout_new_data.addWidget(self.new_offset_pm_line, 6, 1, 1, 1, alignment=Qt.AlignRight)
        self.new_offset_pm_line.setStyleSheet(stylesheet9)
        self.new_offset_pm_line.setFont(font12)
        self.new_offset_pm_line.addItem('+')
        self.new_offset_pm_line.addItem('-')
        self.new_offset_pm_line.setFixedWidth(80)
        self.new_offset_line = QTimeEdit(self)
        self.layout_new_data.addWidget(self.new_offset_line, 6, 2, 1, 1)
        self.new_offset_line.setStyleSheet(stylesheet1)
        self.new_offset_line.setFont(font12)

        self.new_gps_check = QCheckBox(self)
        self.layout_new_data.addWidget(self.new_gps_check, 7, 0, 1, 1)
        self.new_gps_check.setStyleSheet(stylesheet2)
        self.new_gps_check.setFont(font12)

        self.new_gps_lat_line = QLineEdit(self) # широта
        self.layout_new_data.addWidget(self.new_gps_lat_line, 7, 1, 1, 1)
        self.new_gps_lat_line.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp('^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,4})?))$')))
        self.new_gps_lat_line.setStyleSheet(stylesheet1)
        self.new_gps_lat_line.setFont(font12)

        self.new_gps_lon_line = QLineEdit(self) # долгота
        self.layout_new_data.addWidget(self.new_gps_lon_line, 7, 2, 1, 1)
        self.new_gps_lon_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(
                '^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,4})?))$')))
        self.new_gps_lon_line.setStyleSheet(stylesheet1)
        self.new_gps_lon_line.setFont(font12)

        self.new_make_check.setText('Производитель')
        self.new_model_check.setText('Модель')
        self.new_lens_check.setText('Объектив')
        self.new_bodynum_check.setText('Серийный номер камеры')
        self.new_lensnum_check.setText('Серийный номер объектива')
        self.new_datetime_check.setText('Дата и время')
        self.new_offset_check.setText('Часовой пояс')
        self.new_gps_check.setText('Координаты')

        self.new_make_line.setDisabled(True)
        self.new_model_line.setDisabled(True)
        self.new_lens_line.setDisabled(True)
        self.new_bodynum_line.setDisabled(True)
        self.new_lensnum_line.setDisabled(True)
        self.new_datetime_line.setDisabled(True)
        self.new_offset_line.setDisabled(True)
        self.new_offset_pm_line.setDisabled(True)
        self.new_gps_lat_line.setDisabled(True)
        self.new_gps_lon_line.setDisabled(True)

        self.new_make_check.stateChanged.connect(self.new_line_locker)
        self.new_model_check.stateChanged.connect(self.new_line_locker)
        self.new_lens_check.stateChanged.connect(self.new_line_locker)
        self.new_bodynum_check.stateChanged.connect(self.new_line_locker)
        self.new_lensnum_check.stateChanged.connect(self.new_line_locker)
        self.new_datetime_check.stateChanged.connect(self.new_line_locker)
        self.new_offset_check.stateChanged.connect(self.new_line_locker)
        self.new_gps_check.stateChanged.connect(self.new_line_locker)

    # блокировать/разрешать ввод в поле ввода, если не нажата/нажата галочка в чекбоксе
    def new_line_locker(self) -> None:
        match self.sender().text():
            case "Производитель":
                lines = [self.new_make_line]
            case "Модель":
                lines = [self.new_model_line]
            case "Объектив":
                lines = [self.new_lens_line]
            case "Серийный номер камеры":
                lines = [self.new_bodynum_line]
            case "Серийный номер объектива":
                lines = [self.new_lensnum_line]
            case "Дата и время":
                lines = [self.new_datetime_line]
            case "Часовой пояс":
                lines = [self.new_offset_line, self.new_offset_pm_line]
            case "Координаты":
                lines = [self.new_gps_lat_line, self.new_gps_lon_line]

        if self.sender().checkState():
            for line in lines:
                line.setDisabled(False)
        else:
            for line in lines:
                line.setDisabled(True)

        if self.sender().text() == "Координаты":
            if self.sender().checkState():
                self.make_map(1)
            else:
                self.make_map(0)

    # создание карты и метки на ней
    def make_map(self, status: int) -> None:
        if not status:
            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass
        else:
            self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

            self.map_gps = folium.Map(location=(0, 0), zoom_start=1)

            self.popup = folium.LatLngPopup()
            self.map_gps.add_child(self.popup)
            self.map_gps_widget.setHtml(self.map_gps.get_root().render())

            self.layout_outside.addWidget(self.map_gps_widget, 1, 3, 1, 1)

    # кнопки переноса всех фото между таблицами
    def make_buttons(self) -> None:
        self.btn_move_all_right = QPushButton(self)
        self.btn_move_all_right.setText(">>")
        self.btn_move_all_right.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_all_right, 1, 1, 1, 1)
        self.btn_move_all_right.clicked.connect(self.transfer_all_to_edit)
        self.btn_move_all_right.setStyleSheet(stylesheet8)
        self.btn_move_all_right.setFont(font12)

        self.btn_move_all_left = QPushButton(self)
        self.btn_move_all_left.setText("<<")
        self.btn_move_all_left.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_all_left, 2, 1, 1, 1)
        self.btn_move_all_left.clicked.connect(self.transfer_all_to_filtered)
        self.btn_move_all_left.setStyleSheet(stylesheet8)
        self.btn_move_all_left.setFont(font12)
        
        self.btn_clear_all = QPushButton(self)
        self.btn_clear_all.setText('Очистить')
        self.layout_btns.addWidget(self.btn_clear_all, 0, 2, 1, 1)
        self.btn_clear_all.clicked.connect(self.func_clear)
        self.btn_clear_all.setStyleSheet(stylesheet8)
        self.btn_clear_all.setFont(font12)
        self.btn_clear_all.setFixedHeight(50)

        self.btn_write = QPushButton(self)
        self.btn_write.setText('Записать')
        self.layout_btns.addWidget(self.btn_write, 0, 0, 1, 1)
        self.btn_write.clicked.connect(self.write_data)
        self.btn_write.setStyleSheet(stylesheet8)
        self.btn_write.setFont(font12)
        self.btn_write.setFixedHeight(50)

        self.empty1 = QLabel(self)
        self.layout_btns.addWidget(self.empty1, 0, 1, 1, 1)

        self.loading_lbl = QLabel()
        self.movie = QtGui.QMovie(loading_icon)
        self.loading_lbl.setMovie(self.movie)
        self.loading_lbl.setStyleSheet(stylesheet2)
        self.movie.start()
        self.loading_lbl.hide()

    # выбор способа группировки
    def fill_sort_groupbox(self) -> None:
        self.group_type = QComboBox(self)
        self.group_type.addItem('Дата')
        self.group_type.addItem('Оборудование')
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(152)
        self.group_type.setFixedHeight(30)
        self.group_type.setStyleSheet(stylesheet9)

        self.layout_outside.addWidget(self.group_type, 0, 0, 1, 1)

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
        self.date_month.setFixedWidth(140)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1)

        self.day_lbl = QLabel(self)
        self.day_lbl.setFont(font14)
        self.day_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.day_lbl, 0, 5, 1, 1)

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_day.setFixedWidth(140)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1)

        if not self.year_lbl.text():
            self.year_lbl.setText('Год:')
            self.month_lbl.setText('    Месяц:')
            self.day_lbl.setText('    День:')

        self.date_day.setFixedHeight(30)
        self.date_month.setFixedHeight(30)
        self.date_year.setFixedHeight(30)
        self.day_lbl.setFixedHeight(30)
        self.month_lbl.setFixedHeight(30)
        self.year_lbl.setFixedHeight(30)

        self.date_year.currentTextChanged.connect(lambda: self.fill_date('month'))
        self.date_month.currentTextChanged.connect(lambda: self.fill_date('day'))
        self.date_day.currentTextChanged.connect(self.show_filtered_thumbs)

        self.fill_date('date')

    # заполнение полей сортировки по дате
    def fill_date(self, mode: str) -> None:
        # Получение годов
        def get_years() -> None:
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
            self.date_year.addItem('All')

        # Получение месяцев в году
        def get_months() -> None:
            self.date_month.clear()
            year = self.date_year.currentText()
            if year == 'All':
                self.date_month.addItem('All')
            else:
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
                self.date_month.addItem('All')

        # Получение дней в месяце
        def get_days() -> None:
            self.date_day.clear()
            year = self.date_year.currentText()
            month = self.date_month.currentText()
            if year == 'All' or month == 'All':
                self.date_day.addItem('All')
            else:
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
                self.date_day.addItem('All')

        match mode:
            case 'date':
                get_years()
                get_months()
                get_days()
            case 'year':
                get_years()
            case 'month':
                get_months()
            case 'day':
                get_days()
            case _:
                get_years()
                get_months()
                get_days()

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
        self.camera_choose.addItem('All')

        for lens in lenses:
            self.lens_choose.addItem(f'{lens}')
            if len(lens) > lens_max_len:
                lens_max_len = len(lens)
        self.lens_choose.addItem('All')

        self.camera_choose.setFixedWidth(camera_max_len*12)
        self.lens_choose.setFixedWidth(lens_max_len*12)

        self.camera_choose.currentTextChanged.connect(self.show_filtered_thumbs)
        self.lens_choose.currentTextChanged.connect(self.show_filtered_thumbs)

    # заполнить нужное поле в зависимости от выбранного типа группировки
    def set_sort_layout(self) -> None:
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().hide()
            self.layout_type.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        match self.group_type.currentText():
            case 'Дата':
                self.fill_sort_date()
            case 'Оборудование':
                self.fill_sort_equipment()

        self.show_filtered_thumbs()

    # преобразовать пути фотографий из БД в пути миниатюр для отображения
    def photo_to_thumb_path(self, photo_list: list[str]) -> list[str]:
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

        return thumbnails_list

    # показывать в левой таблице фото по группировке
    def show_filtered_thumbs(self) -> None:
        try:
            self.btn_move_all_left.setDisabled(True)
            self.btn_move_all_right.setDisabled(True)
            self.btn_clear_all.setDisabled(True)
            self.btn_write.setDisabled(True)
            for i in reversed(range(self.layout_type.count())):
                self.layout_type.itemAt(i).widget().setDisabled(True)
        except AttributeError:
            pass

        for i in range(self.table_compare.columnCount()):
            self.table_compare.removeColumn(i)

        for i in range(self.filtered_photo_table.rowCount()):
            for j in range(self.filtered_photo_table.columnCount()):
                try:
                    self.filtered_photo_table.cellWidget(i, j).deleteLater()
                except (AttributeError, RuntimeError):
                    pass
        self.filtered_photo_table.setRowCount(0)

        for k in range(self.edit_photo_table.rowCount()):
            try:
                self.edit_photo_table.cellWidget(k, 0).deleteLater()
            except (AttributeError, RuntimeError):
                pass
        self.edit_photo_table.setRowCount(0)

        match self.group_type.currentText():
            case 'Дата':
                year = self.date_year.currentText()
                month = self.date_month.currentText()
                day = self.date_day.currentText()

                photo_list = PhotoDataDB.get_date_photo_list(year, month, day)

            case 'Оборудование':
                camera = self.camera_choose.currentText()
                lens = self.lens_choose.currentText()

                if camera == 'All':
                    camera_exif = 'All'
                else:
                    camera_exif = Metadata.equip_name_check_reverse(camera, 'camera')

                if lens == 'All':
                    lens_exif = 'All'
                else:
                    lens_exif = Metadata.equip_name_check_reverse(lens, 'lens')

                photo_list = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens)

        if not photo_list:
            return

        thumbnails_list = self.photo_to_thumb_path(photo_list)

        columns = 2
        rows = math.ceil(len(thumbnails_list) / columns)

        self.filtered_photo_table.setColumnCount(columns)
        self.filtered_photo_table.setRowCount(rows)

        for j in range(0, rows):
            if j == rows - 1:
                for i in range(0, len(thumbnails_list) - columns*(rows-1)):
                    self.item = QToolButton()
                    self.item.setFixedSize(130, 130)
                    self.item.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * columns + i]}')  # создание объекта картинки
                    iqon.pixmap(100, 100)
                    self.item.setIcon(iqon)
                    self.item.setIconSize(QtCore.QSize(100, 100))
                    filename_show = thumbnails_list[j * columns + i].split('/')[-1][10:]
                    self.item.setText(f'{filename_show}')
                    self.item.setObjectName(f'{photo_list[j * columns + i]}')
                    self.filtered_photo_table.setCellWidget(j, i, self.item)
                    # self.item.clicked.connect(lambda: self.filtered_photo_table.setCurrentCell(j, i))
                    self.item.clicked.connect(self.transfer_one_to_edit)
                    QtCore.QCoreApplication.processEvents()
            else:
                for i in range(0, columns):
                    self.item = QToolButton()
                    self.item.setFixedSize(130, 130)
                    self.item.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f'{thumbnails_list[j * columns + i]}')  # создание объекта картинки
                    iqon.pixmap(100, 100)
                    self.item.setIcon(iqon)
                    self.item.setIconSize(QtCore.QSize(100, 100))
                    filename_show = thumbnails_list[j * columns + i].split('/')[-1][10:]
                    self.item.setText(f'{filename_show}')
                    self.item.setObjectName(f'{photo_list[j * columns + i]}')
                    self.filtered_photo_table.setCellWidget(j, i, self.item)
                    # self.item.clicked.connect(lambda: self.filtered_photo_table.setCurrentCell(j, i))
                    self.item.clicked.connect(self.transfer_one_to_edit)
                    QtCore.QCoreApplication.processEvents()

        try:
            self.btn_move_all_left.setDisabled(False)
            self.btn_move_all_right.setDisabled(False)
            self.btn_clear_all.setDisabled(False)
            self.btn_write.setDisabled(False)
            for i in reversed(range(self.layout_type.count())):
                self.layout_type.itemAt(i).widget().setDisabled(False)
        except AttributeError:
            pass

    # перенос всех отфильтрованных фото в таблицу редактирования
    def transfer_all_to_edit(self) -> None:
        self.btn_move_all_left.setDisabled(True)
        self.btn_move_all_right.setDisabled(True)
        self.btn_clear_all.setDisabled(True)
        self.btn_write.setDisabled(True)
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().setDisabled(True)

        for i in range(self.filtered_photo_table.rowCount()):
            for j in range(self.filtered_photo_table.columnCount()):
                try:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                    if not self.filtered_photo_table.cellWidget(i, j).isEnabled():
                        pass
                    else:
                        photo_path = self.filtered_photo_table.cellWidget(i, j).objectName()
                        self.filtered_photo_table.cellWidget(i, j).setDisabled(True)
                        item = QToolButton(self)
                        item.setFixedSize(130, 130)
                        item.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

                        item_iqon = QtGui.QIcon(self.photo_to_thumb_path([photo_path])[0])
                        item_text = photo_path.split('/')[-1]
                        item_objectname = photo_path

                        item.setIcon(item_iqon)
                        item.setIconSize(QtCore.QSize(100, 100))
                        item.setText(item_text)
                        item.setObjectName(item_objectname)

                        self.edit_photo_table.setRowCount(self.edit_photo_table.rowCount() + 1)
                        self.edit_photo_table.setCellWidget(self.edit_photo_table.rowCount() - 1, 0, item)

                        QtCore.QCoreApplication.processEvents()
                        self.table_one_add(photo_path)
                        item.clicked.connect(self.transfer_one_to_filtered)
                        QtCore.QCoreApplication.processEvents()
                except AttributeError:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                    pass
        self.btn_move_all_left.setDisabled(False)
        self.btn_move_all_right.setDisabled(False)
        self.btn_clear_all.setDisabled(False)
        self.btn_write.setDisabled(False)
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().setDisabled(False)

    # перенос всех фото из таблицы редактирования в таблицу просто отфильтрованных
    def transfer_all_to_filtered(self) -> None:
        for k in range(self.edit_photo_table.rowCount()):
            photo_path = self.edit_photo_table.cellWidget(k, 0).objectName()
            x = 0
            for i in range(self.filtered_photo_table.rowCount()):
                for j in range(self.filtered_photo_table.columnCount()):
                    try:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                        if self.filtered_photo_table.cellWidget(i, j).objectName() == photo_path:
                            self.filtered_photo_table.cellWidget(i, j).setDisabled(False)
                            self.edit_photo_table.cellWidget(k, 0).deleteLater()
                            x = 1
                            break
                    except AttributeError:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                        pass
                if x:
                    break
            self.table_one_del(photo_path)

        self.edit_photo_table.setRowCount(0)

    # перенос одного фото в редактирование
    def transfer_one_to_edit(self) -> None:
        photo_path = self.sender().objectName()
        self.sender().setDisabled(True)
        item = QToolButton(self)
        item.setFixedSize(130, 130)
        item.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        item_iqon = QtGui.QIcon(self.photo_to_thumb_path([photo_path])[0])
        item_text = photo_path.split('/')[-1]
        item_objectname = photo_path

        item.setIcon(item_iqon)
        item.setIconSize(QtCore.QSize(100, 100))
        item.setText(item_text)
        item.setObjectName(item_objectname)

        self.edit_photo_table.setRowCount(self.edit_photo_table.rowCount() + 1)
        self.edit_photo_table.setCellWidget(self.edit_photo_table.rowCount() - 1, 0, item)

        self.table_one_add(photo_path)

        item.clicked.connect(self.transfer_one_to_filtered)

    # перенос одного фото из редактирования
    def transfer_one_to_filtered(self) -> None:
        photo_path = self.sender().objectName()
        x = 0
        for i in range(self.filtered_photo_table.rowCount()):
            for j in range(self.filtered_photo_table.columnCount()):
                try:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                    if self.filtered_photo_table.cellWidget(i, j).objectName() == photo_path:
                        self.filtered_photo_table.cellWidget(i, j).setDisabled(False)
                        x = 1
                        break
                except AttributeError:
                    pass
            if x:
                break

        for k in range(self.edit_photo_table.rowCount()):
            if self.edit_photo_table.cellWidget(k,0).objectName() == photo_path:
                self.edit_photo_table.cellWidget(k, 0).deleteLater()
                self.edit_photo_table.removeRow(k)
                break

        self.table_one_del(photo_path)

    # получить список всех файлов, выбранных для редактирования метаданных
    def get_edit_list(self) -> list[str]:
        photo_list = []
        for k in range(self.edit_photo_table.rowCount()):
            try:
                photo_list.append(self.edit_photo_table.cellWidget(k, 0).objectName())
            except AttributeError:
                pass
        return photo_list

    # очистка метаданных
    def func_clear(self) -> None:
        def accepted():
            self.empty1.hide()
            self.layout_btns.addWidget(self.loading_lbl, 0, 1, 1, 1)
            self.loading_lbl.show()
            QtCore.QCoreApplication.processEvents()

            for file in self.get_edit_list():
                name = file.split('/')[-1]
                directory = file[:(-1) * (len(name) + 1)]
                Metadata.clear_exif(name, directory)
                PhotoDataDB.clear_metadata(name, directory)

            self.empty1.show()
            self.layout_btns.addWidget(self.empty1, 0, 1, 1, 1)
            self.loading_lbl.hide()
            QtCore.QCoreApplication.processEvents()
            self.update_table()

        def rejected():
            win.close()

        win = ConfirmClear(self.parent())
        win.show()
        win.accept_signal.connect(accepted)
        win.reject_signal.connect(rejected)

    # считать все новые вводимые данные
    def get_all_new_data(self) -> dict[int, str]:
        modify_dict = dict()

        if self.new_make_check.checkState():
            if self.new_make_line.text():
                modify_dict[0] = self.new_make_line.text()
        if self.new_model_check.checkState():
            if self.new_model_line.text():
                modify_dict[1] = self.new_model_line.text()
        if self.new_lens_check.checkState():
            if self.new_lens_line.text():
                modify_dict[2] = self.new_lens_line.text()
        if self.new_bodynum_check.checkState():
            if self.new_bodynum_line.text():
                modify_dict[9] = self.new_bodynum_line.text()
        if self.new_lensnum_check.checkState():
            if self.new_lensnum_line.text():
                modify_dict[10] = self.new_lensnum_line.text()
        if self.new_datetime_check.checkState():
            modify_dict[11] = self.new_datetime_line.text().replace(".", ":")
        if self.new_offset_check.checkState():
            modify_dict[8] = self.new_offset_pm_line.currentText() + self.new_offset_line.text()
        if self.new_gps_check.checkState():
            if self.new_gps_lat_line.text() and self.new_gps_lon_line.text():
                modify_dict[7] = self.new_gps_lat_line.text() + ', ' + self.new_gps_lon_line.text()

        return modify_dict

    # запись новых метаданных
    def write_data(self) -> None:
        def finished():
            self.empty1.show()
            self.layout_btns.removeWidget(self.loading_lbl)
            self.layout_btns.addWidget(self.empty1, 0, 1, 1, 1)
            self.loading_lbl.hide()
            QtCore.QCoreApplication.processEvents()
            self.update_table()

        self.empty1.hide()
        self.layout_btns.addWidget(self.loading_lbl, 0, 1, 1, 1)
        self.loading_lbl.show()
        QtCore.QCoreApplication.processEvents()

        photo_list = self.get_edit_list()
        modify_dict = self.get_all_new_data()

        self.editing_process = DoEditing(photo_list, modify_dict)
        self.editing_process.finished.connect(finished)
        self.editing_process.start()

    # Создать таблицу сравнения
    def make_compare_table(self) -> None:
        self.table_compare.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_compare.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_compare.setFont(font14)
        self.table_compare.setRowCount(8)
        self.table_compare.setStyleSheet(stylesheet6)
        self.table_compare.horizontalHeader().setStyleSheet(stylesheet3)
        self.table_compare.verticalHeader().setStyleSheet(stylesheet3)
        self.table_compare.horizontalHeader().setFont(font10)
        self.table_compare.verticalHeader().setFont(font10)
        self.table_compare.setVerticalHeaderLabels(["Производитель", "Модель", "Объектив", "Серийный номер камеры",
                                                    "Серийный номер объектива", "Дата и Время", "Часовой пояс",
                                                    "Координаты"])
        # закрасить левый верхний угол, которые иначе - белый-белый
        self.table_compare.findChild(QAbstractButton).setStyleSheet(stylesheet2)

    # +1 фото в редактирование
    def table_one_add(self, photo: str) -> None:
        self.table_compare.setColumnCount(self.table_compare.columnCount() + 1)
        column = self.table_compare.columnCount() - 1
        self.table_positions[photo] = column
        self.table_compare.setHorizontalHeaderItem(column, QTableWidgetItem(photo.split('/')[-1]))
        current_data = Metadata.massive_table_data(photo)
        lbl_1 = QLabel(self)
        lbl_1.setText(str(current_data['Производитель']))
        lbl_1.setFont(font10)
        lbl_1.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(0, column, lbl_1)
        lbl_2 = QLabel(self)
        lbl_2.setText(str(current_data['Камера']))
        lbl_2.setFont(font10)
        lbl_2.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(1, column, lbl_2)
        lbl_3 = QLabel(self)
        lbl_3.setText(str(current_data['Объектив']))
        lbl_3.setFont(font10)
        lbl_3.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(2, column, lbl_3)
        lbl_4 = QLabel(self)
        lbl_4.setText(str(current_data['Серийный номер камеры']))
        lbl_4.setFont(font10)
        lbl_4.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(3, column, lbl_4)
        lbl_5 = QLabel(self)
        lbl_5.setText(str(current_data['Серийный номер объектива']))
        lbl_5.setFont(font10)
        lbl_5.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(4, column, lbl_5)
        lbl_6 = QLabel(self)
        lbl_6.setText(str(current_data['Время съёмки']))
        lbl_6.setFont(font10)
        lbl_6.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(5, column, lbl_6)
        lbl_7 = QLabel(self)
        lbl_7.setText(str(current_data['Часовой пояс']))
        lbl_7.setFont(font10)
        lbl_7.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(6, column, lbl_7)
        lbl_8 = QLabel(self)
        lbl_8.setText(str(current_data['Координаты']))
        lbl_8.setFont(font10)
        lbl_8.setStyleSheet(stylesheet2)
        self.table_compare.setCellWidget(7, column, lbl_8)

    # -1 фото из редактирования
    def table_one_del(self, photo: str) -> None:
        column = self.table_positions[photo]
        self.table_compare.removeColumn(column)
        for key in list(self.table_positions.keys()):
            if self.table_positions[key] > column:
                self.table_positions[key] = self.table_positions[key] - 1
        self.table_positions.pop(photo)

    # заново заполнить таблицу после очистки/редактирования
    def update_table(self) -> None:
        self.table_compare.setColumnCount(0)
        for photo in self.get_edit_list():
            self.table_one_add(photo)
            QtCore.QCoreApplication.processEvents()


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


# Процесс редактирования метаданных и записей в БД
# Пришлось сделать редактирование данных не всему списку разом, так как выполнение массового редактирования при 4+ фото
# длится больше 5 секунд и ломает поток. Поток выполняется, но не отправляет сигнал на изменение интерфейса (убрать
# загрузку и обновить таблицу).
class DoEditing(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, photo_list, modify_dict):
        QtCore.QThread.__init__(self)
        self.modify_dict = modify_dict
        self.photo_list = photo_list

        self._init = False

    def run(self):
        # Metadata.massive_exif_edit(self.photo_list, self.modify_dict)
        for file in self.photo_list:
            name = file.split('/')[-1]
            dir = file[:(-1)*(len(name)+1)]
            Metadata.exif_rewrite_edit(name, dir, self.modify_dict)
        PhotoDataDB.massive_edit_metadata(self.photo_list, self.modify_dict)

        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManyPhotoEdit()
    win.show()
    sys.exit(app.exec_())
