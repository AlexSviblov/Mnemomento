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


# редактирование exif
class EditExifData(QDialog):

    edited_signal = QtCore.pyqtSignal()
    edited_signal_no_move = QtCore.pyqtSignal()
    movement_signal = QtCore.pyqtSignal(str, str, str)

    def __init__(self, parent, photoname, photodirectory, chosen_group_type):
        super().__init__(parent)
        self.stylesheet_color()

        self.setStyleSheet(stylesheet2)

        self.setWindowTitle('Редактирование метаданных')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.photoname = photoname
        self.photodirectory = photodirectory
        self.chosen_group_type = chosen_group_type

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

    # создание всего GUI в разделе, где можно редактировать метаданные
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

        self.latitude_fn_lbl = QLabel(self)     # широта
        self.latitude_fn_lbl.setText("Широта:")

        self.longitude_fn_lbl = QLabel(self)    # долгота
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

        self.latitude_dmc_lbl = QLabel(self)     # широта
        self.latitude_dmc_lbl.setText("Широта:")

        self.longitude_dmc_lbl = QLabel(self)    # долгота
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
        data = Metadata.exif_show_edit(photodirectory + '/' + photoname)

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
                                self.table.rowCount() * self.table.rowHeight(0) + self.btn_ok.height() + 60)

        def fill_equip_set():
            self.maker_line.setText(str(data['Производитель']))
            self.camera_line.setText(str(data['Камера']))
            self.lens_line.setText(str(data['Объектив']))
            self.time_line.setText(str(data['Выдержка']))
            self.iso_line.setText(str(data['ISO']))
            self.fnumber_line.setText(str(data['Диафрагма']))
            self.flength_line.setText(str(data['Фокусное расстояние']))
            self.serialbody_line.setText(str(data['Серийный номер камеры']))
            self.seriallens_line.setText(str(data['Серийный номер объектива']))

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

            latitude_min = math.trunc((abs(latitude_part) - latitude_deg)*60)
            longitude_min = math.trunc((abs(longitude_part) - longitude_deg)*60)

            latitude_sec = round((((abs(latitude_part) - latitude_deg)*60) - latitude_min) * 60, 3)
            longitude_sec = round((((abs(longitude_part) - longitude_deg)*60) - longitude_min) * 60, 3)

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
            try:
                latitude_deg = float(self.latitude_dmc_deg_line.text())
            except ValueError:
                latitude_deg = 0
            try:
                longitude_deg = float(self.longitude_dmc_deg_line.text())
            except ValueError:
                longitude_deg = 0
            try:
                latitude_min = float(self.latitude_dmc_min_line.text())
            except ValueError:
                latitude_min = 0
            try:
                longitude_min = float(self.longitude_dmc_min_line.text())
            except ValueError:
                longitude_min = 0
            try:
                latitude_sec = float(self.latitude_dmc_sec_line.text())
            except ValueError:
                latitude_sec = 0
            try:
                longitude_sec = float(self.longitude_dmc_sec_line.text())
            except ValueError:
                longitude_sec = 0

            if latitude_ref == "Юг":
                latitude_pm_coe = -1
            else: # latitude_ref == "Север"
                latitude_pm_coe = 1

            if longitude_ref == "Восток":
                longitude_pm_coe = 1
            else: # latitude_ref == "Запад"
                longitude_pm_coe = -1

            latitude = round((latitude_pm_coe*(latitude_deg + latitude_min/60 + latitude_sec/3600)), 6)
            longitude = round(longitude_pm_coe*(longitude_deg + longitude_min/60 + longitude_sec/3600), 6)

            self.latitude_fn_line.setText(str(latitude))
            self.longitude_fn_line.setText(str(longitude))
        else: #self.mode_check_fn.checkState() == 2
            try:
                latitude = float(self.latitude_fn_line.text())
            except ValueError:
                latitude = 0

            try:
                longitude = float(self.longitude_fn_line.text())
            except ValueError:
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
        if self.sender().text() == "ШД Г.м.с":    # type: ignore[attr-defined]
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
            PhotoDataDB.edit_in_database(photoname, photodirectory, editing_type, new_text)

        # проверка введённых пользователем метаданных
        def check_enter(editing_type: int, new_text: str) -> None:
            Metadata.exif_check_edit(editing_type, new_text)

        # проверка введённых пользователем метаданных
        try:
            check_enter(editing_type, new_text)
        except ErrorsAndWarnings.EditExifError:
            logging.error(f"Invalid try to rewrite metadata {photoname}, {photodirectory}, {editing_type}, {new_text}")
            win_err = ErrorsAndWarnings.EditExifError_win(self)
            win_err.show()
            return

        # Если меняется дата -> проверка на перенос файла в новую папку
        if editing_type == 11 and type(self.parent()) == ShowConstWindowWidget.ConstWidgetWindow:
            if photodirectory[-12:] == 'No_Date_Info':
                new_date = photodirectory[-38:]
            else:
                new_date = photodirectory[-10:]
            old_date = new_text[:10]
            new_date_splitted = new_date.split('/')
            old_date_splitted = old_date.split(':')
            if new_date_splitted == old_date_splitted:  # если дата та же, переноса не требуется
                rewriting(photoname, photodirectory, editing_type, new_text)
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
                    rewriting(photoname, photodirectory, editing_type, new_text)
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
                        rewriting(photoname, photodirectory, editing_type, new_text)
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
        else:
            rewriting(photoname, photodirectory, editing_type, new_text)
            self.edited_signal.emit()

    # записать новые метаданные
    def clear_exif_func(self) -> None:
        def accepted():
            if not os.path.exists(Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info/'):
                os.mkdir(Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/')
                os.mkdir(Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/')
                os.mkdir(Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info/')

            photodirectory_splitted = self.photodirectory.split('/')
            new_date_splitted = [photodirectory_splitted[-3], photodirectory_splitted[-2], photodirectory_splitted[-1]]
            old_date_splitted = ['No_Date_Info', 'No_Date_Info', 'No_Date_Info']

            # self.photodirectory = 'C:/Users/user/PycharmProjects/PhotoProgramm/Media/Photo/const/2021/10/30'
            # self.photoname = 'IMG_0866.jpg'
            if not os.path.exists(Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info/' + self.photoname):
                Metadata.clear_exif(self.photoname, self.photodirectory)
                PhotoDataDB.clear_metadata(self.photoname, self.photodirectory)
                shutil.move(self.photodirectory + '/' + self.photoname, Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info/' + self.photoname)
                PhotoDataDB.catalog_after_transfer(self.photoname, Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info', self.photodirectory)
                Thumbnail.transfer_diff_date_thumbnail(self.photoname, new_date_splitted, old_date_splitted)
                self.movement_signal.emit('No_Date_Info', 'No_Date_Info', 'No_Date_Info')
            else:
                window_equal = EqualNames(self, self.photoname, old_date_splitted, new_date_splitted, "No_Date_Info:No_Date_Info:No_Date_Info")
                window_equal.show()
                if self.chosen_group_type == 'Дата':
                    window_equal.file_rename_transfer_signal.connect(lambda: self.movement_signal.emit('No_Date_Info', 'No_Date_Info', 'No_Date_Info'))
                else:
                    pass

                window_equal.file_rename_transfer_signal.connect(lambda: self.close())
                window_equal.file_rename_transfer_signal.connect(lambda: self.movement_signal.emit('No_Date_Info', 'No_Date_Info', 'No_Date_Info'))

            self.get_metadata(self.photoname, Settings.get_destination_media() + '/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info')
            self.close()

        def rejected():
            win.close()

        win = ConfirmClear(self.parent())
        win.show()
        win.accept_signal.connect(accepted)
        win.reject_signal.connect(rejected)