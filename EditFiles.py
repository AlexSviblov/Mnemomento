import logging
import os
import folium
import math
import shutil

import ErrorsAndWarnings
import OnlyShowWidget
import PhotoDataDB
import Metadata
import Screenconfig
import Settings
import ShowConstWindowWidget
import Thumbnail

from PyQt5 import QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PIL import Image
from PIL import ImageFile
import exiftool

from FoliumRemastered import WebEnginePage, ClickForLatLng, LatLngPopup
from Screenconfig import font14, font12

ImageFile.LOAD_TRUNCATED_IMAGES = True


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()


system_scale = Screenconfig.monitor_info()[1]


# редактирование exif
class EditExifData(QDialog):

    edited_signal = QtCore.pyqtSignal()
    edited_signal_no_move = QtCore.pyqtSignal()
    movement_signal = QtCore.pyqtSignal(str, str, str)
    renamed_signal = QtCore.pyqtSignal(str)
    rotated_signal = QtCore.pyqtSignal()

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

        self.table = QTableWidget(self)
        self.btn_ok = QPushButton(self)
        self.btn_cancel = QPushButton(self)
        self.btn_clear = QPushButton(self)
        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

        self.tab_date_layout = QGridLayout(self)
        self.date_lbl = QLabel(self)
        self.date_choose = QDateTimeEdit(self)
        self.timezone_lbl = QLabel(self)
        self.timezone_pm_choose = QComboBox(self)
        self.timezone_num_choose = QTimeEdit(self)

        self.tab_tt_layout = QGridLayout(self)
        self.maker_lbl = QLabel(self)
        self.camera_lbl = QLabel(self)
        self.lens_lbl = QLabel(self)
        self.time_lbl = QLabel(self)
        self.iso_lbl = QLabel(self)
        self.fnumber_lbl = QLabel(self)
        self.flength_lbl = QLabel(self)
        self.serialbody_lbl = QLabel(self)
        self.seriallens_lbl = QLabel(self)
        self.maker_line = QLineEdit(self)
        self.camera_line = QLineEdit(self)
        self.lens_line = QLineEdit(self)
        self.time_line = QLineEdit(self)
        self.iso_line = QLineEdit(self)
        self.fnumber_line = QLineEdit(self)
        self.flength_line = QLineEdit(self)
        self.serialbody_line = QLineEdit(self)
        self.seriallens_line = QLineEdit(self)

        self.tab_layout_gps = QGridLayout(self)
        self.mode_check_dmc = QCheckBox(self)
        self.mode_check_fn = QCheckBox(self)
        self.latitude_fn_lbl = QLabel(self)  # широта
        self.longitude_fn_lbl = QLabel(self)  # долгота
        self.latitude_fn_line = QLineEdit(self)  # широта
        self.longitude_fn_line = QLineEdit(self)  # долгота
        self.latitude_dmc_lbl = QLabel(self)  # широта
        self.longitude_dmc_lbl = QLabel(self)  # долгота
        self.latitude_dmc_choose = QComboBox(self)
        self.longitude_dmc_choose = QComboBox(self)
        self.latitude_dmc_deg_lbl = QLabel(self)  # широта
        self.longitude_dmc_min_lbl = QLabel(self)  # долгота
        self.latitude_dmc_sec_lbl = QLabel(self)  # широта
        self.longitude_dmc_deg_lbl = QLabel(self)  # долгота
        self.latitude_dmc_min_lbl = QLabel(self)  # широта
        self.longitude_dmc_sec_lbl = QLabel(self)  # долгота
        self.latitude_dmc_deg_line = QLineEdit(self)  # широта
        self.latitude_dmc_min_line = QLineEdit(self)  # широта
        self.latitude_dmc_sec_line = QLineEdit(self)  # широта
        self.longitude_dmc_deg_line = QLineEdit(self)  # долгота
        self.longitude_dmc_min_line = QLineEdit(self)  # долгота
        self.longitude_dmc_sec_line = QLineEdit(self)  # долгота

        self.tab_file_layout = QGridLayout(self)
        self.filename_lbl = QLabel(self)
        self.filename_line = QLineEdit(self)
        self.file_size_lbl = QLabel(self)
        self.file_size_line = QLineEdit(self)

        self.tab_comment_layout = QGridLayout(self)
        self.usercomment_lbl = QLabel(self)
        self.usercomment_text = QLineEdit(self)

        self.tabs = QTabWidget(self)
        self.tab_date = QWidget(self)
        self.tab_technic_settings = QWidget(self)
        self.tab_GPS = QWidget(self)
        self.tab_file = QWidget(self)
        self.tab_comment = QWidget(self)

        self.make_gui()

        self.get_metadata(photoname, photodirectory)
        self.get_file_data(photoname, photodirectory)
        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet3
        global stylesheet6
        global stylesheet7
        global stylesheet8
        global stylesheet9

        theme = Settings.get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f'{theme}']['stylesheet1']
        stylesheet2 = style[f'{theme}']['stylesheet2']
        stylesheet3 = style[f'{theme}']['stylesheet3']
        stylesheet6 = style[f'{theme}']['stylesheet6']
        stylesheet7 = style[f'{theme}']['stylesheet7']
        stylesheet8 = style[f'{theme}']['stylesheet8']
        stylesheet9 = style[f'{theme}']['stylesheet9']

        try:
            self.setStyleSheet(stylesheet2)
        except AttributeError:
            pass

        try:
            self.table.setStyleSheet(stylesheet6)
        except AttributeError:
            pass

        try:
            self.make_buttons()
        except AttributeError:
            pass

        try:
            self.make_tabs_gui()
        except AttributeError:
            pass

        try:
            self.update_show_data()
        except AttributeError:
            pass

    # создание интерфейса
    def make_gui(self) -> None:
        """
        Создаёт графический интерфейс, состоящий из слоя, на котором всё находится, таблицы с метаданными (отображается
        в окне справа), переключаемыми панелями.
        """
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        self.table.setFont(font12)
        self.table.setDisabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet(stylesheet3)
        self.table.setStyleSheet(stylesheet6)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.table, 0, 1, 1, 2)

        self.make_buttons()

        self.make_tabs_gui()

        self.layout.addWidget(self.tabs, 0, 0, 1, 1)

    # создание кнопок
    def make_buttons(self):
        self.btn_ok.setText("Записать")
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)
        self.btn_ok.clicked.connect(self.pre_write_changes)

        self.btn_cancel.setText("Отмена")
        self.btn_cancel.setStyleSheet(stylesheet8)
        self.btn_cancel.setFont(font14)
        self.layout.addWidget(self.btn_cancel, 1, 1, 1, 1)
        self.btn_cancel.clicked.connect(self.close)

        self.btn_clear.setText("Очистить")
        self.btn_clear.setStyleSheet(stylesheet8)
        self.btn_clear.setFont(font14)
        self.layout.addWidget(self.btn_clear, 1, 2, 1, 1)
        self.btn_clear.clicked.connect(self.clear_exif_func)

    # создание карты и метки на ней
    def make_map(self, coordinates, filename):
        # удалить уже существующую карту, если она есть (просто скрытие hide и удаление виджета deleteWidget не работают,
        # надо прям удалять из памяти
        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass

        # карта - web на JS, для отображения нужен webview
        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

        # если координаты ненулевые - центруем карту по координатам фотографии
        if coordinates[0] != 0 and coordinates[1] != 0:
            self.map_gps = folium.Map(location=coordinates, zoom_start=14)
            folium.Marker(coordinates, popup=filename, icon=folium.Icon(color='red')).add_to(self.map_gps)
        else:
            self.map_gps = folium.Map(location=(0, 0), zoom_start=1)

        # если нажать на карту - появится окошко с координатами
        # в folium изменён текст внутри класса LatLngPopup для отображения русским языком
        self.popup = LatLngPopup()
        self.map_gps.add_child(self.popup)

        # добавить невидимую штуку, которая при нажатии на карту будет плевать в консоль JS (код folium изменён) координаты
        # координаты будут сигналом в переопределённом классе вызывать функцию write_coords_to_lines
        # self.map_gps.add_child(folium.features.ClickForLatLng(format_str='lat + "," + lng'))
        self.map_gps.add_child(ClickForLatLng(format_str='lat + "," + lng'))

        page = WebEnginePage(self.map_gps_widget)

        # записать выплюнутые в логи координаты в нужные поля
        def write_coords_to_lines(msg: str):
            self.latitude_fn_line.setText(msg.split(',')[0])
            self.longitude_fn_line.setText(msg.split(',')[1])

        page.coordinates_transfer.connect(lambda msg: write_coords_to_lines(msg))

        self.map_gps_widget.setPage(page)

        self.map_gps_widget.setHtml(self.map_gps.get_root().render())

        self.layout.addWidget(self.map_gps_widget, 0, 1, 1, 2)

    # отображение либо таблицы с данными, либо карты с GPS-меткой, в зависимости от выбранной вкладки
    def change_tab_gps(self):
        if self.tabs.currentIndex() in (0, 1, 3, 4):
            self.table.show()
            self.layout.addWidget(self.table, 0, 1, 1, 2)
            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass
        else:
            self.table.hide()
            self.make_map((float(self.latitude_fn_line.text()), float(self.longitude_fn_line.text())), self.photoname)
            self.map_gps_widget.show()

    # создание всего GUI в разделе, где можно редактировать метаданные
    def make_tabs_gui(self) -> None:
        def make_tab_date():
            self.date_lbl.setStyleSheet(stylesheet2)
            self.date_lbl.setText("Дата съёмки:")
            self.date_lbl.setFont(font14)
            self.date_lbl.setStyleSheet(stylesheet2)
            self.tab_date_layout.addWidget(self.date_lbl, 0, 0, 1, 1)

            self.date_choose.setDisplayFormat("yyyy.MM.dd HH:mm:ss")
            self.date_choose.setFont(font14)
            self.date_choose.setStyleSheet(stylesheet1)
            self.tab_date_layout.addWidget(self.date_choose, 0, 1, 1, 2)

            self.timezone_lbl.setStyleSheet(stylesheet2)
            self.timezone_lbl.setText("Часовой пояс:")
            self.timezone_lbl.setFont(font14)
            self.timezone_lbl.setStyleSheet(stylesheet2)
            self.tab_date_layout.addWidget(self.timezone_lbl, 1, 0, 1, 1)

            self.timezone_pm_choose.setFont(font14)
            self.timezone_pm_choose.setStyleSheet(stylesheet9)
            self.timezone_pm_choose.addItem("+")
            self.timezone_pm_choose.addItem("-")
            self.timezone_pm_choose.setFixedWidth(int(50*system_scale)+1)
            self.tab_date_layout.addWidget(self.timezone_pm_choose, 1, 1, 1, 1)

            self.timezone_num_choose.setFont(font14)
            self.timezone_num_choose.setStyleSheet(stylesheet1)
            self.timezone_num_choose.setDisplayFormat("HH:mm")
            self.tab_date_layout.addWidget(self.timezone_num_choose, 1, 2, 1, 1)

            self.tab_date.setLayout(self.tab_date_layout)

        def make_tab_tt():
            self.maker_lbl.setText("Производитель:")

            self.camera_lbl.setText("Камера:")

            self.lens_lbl.setText("Объектив:")

            self.time_lbl.setText("Выдержка:")

            self.iso_lbl.setText("ISO:")

            self.fnumber_lbl.setText("Диафрагма:")

            self.flength_lbl.setText("Фокусное расстояние:")

            self.serialbody_lbl.setText("Серийный номер камеры:")

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

            self.time_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d+[./]\d+')))

            self.iso_line.setValidator(QtGui.QIntValidator(1, 10000000))

            self.fnumber_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d+[.]\d+')))

            self.flength_line.setValidator(QtGui.QIntValidator(1, 10000))

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

        def make_tab_gps():
            self.mode_check_dmc.setText("ШД Г.м.с")
            self.mode_check_dmc.setFont(font12)
            self.mode_check_dmc.setStyleSheet(stylesheet2)
            self.mode_check_dmc.stateChanged.connect(self.block_check_gps)

            self.mode_check_fn.setText("Числом")
            self.mode_check_fn.setFont(font12)
            self.mode_check_fn.setStyleSheet(stylesheet2)
            self.mode_check_fn.stateChanged.connect(self.block_check_gps)

            self.latitude_fn_lbl.setText("Широта:")

            self.longitude_fn_lbl.setText("Долгота:")

            self.latitude_fn_line.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp('^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,4})?))$')))

            self.longitude_fn_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(
                '^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,4})?))$')))

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

            self.latitude_dmc_lbl.setText("Широта:")

            self.longitude_dmc_lbl.setText("Долгота:")

            self.latitude_dmc_choose.addItem("Север")
            self.latitude_dmc_choose.addItem("Юг")
            self.latitude_dmc_choose.setFixedWidth(int(80*system_scale)+1)

            self.longitude_dmc_choose.addItem("Восток")
            self.longitude_dmc_choose.addItem("Запад")
            self.longitude_dmc_choose.setFixedWidth(int(80*system_scale)+1)

            self.latitude_dmc_deg_lbl.setText("Градусы:")

            self.longitude_dmc_min_lbl.setText("Минуты:")

            self.latitude_dmc_sec_lbl.setText("Секунды:")

            self.longitude_dmc_deg_lbl.setText("Градусы:")

            self.latitude_dmc_min_lbl.setText("Минуты:")

            self.longitude_dmc_sec_lbl.setText("Секунды:")

            self.latitude_dmc_deg_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:90|[0-9]|[1-8][0-9])')))

            self.latitude_dmc_min_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:60|[0-9]|[1-5][0-9])')))

            self.latitude_dmc_sec_line.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp('^(?:60(?:(?:\.0{1,6})?)|(?:[0-9]|[1-5][0-9])(?:(?:\.[0-9]{1,2})?))$')))

            self.longitude_dmc_deg_line.setValidator(
                QtGui.QRegExpValidator(QtCore.QRegExp('(?:180|[0-9]|[1-9][0-9]|1[0-7][0-9])')))

            self.longitude_dmc_min_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('(?:60|[0-9]|[1-5][0-9])')))

            self.longitude_dmc_sec_line.setValidator(QtGui.QRegExpValidator(
                QtCore.QRegExp('^(?:60(?:(?:\.0{1,6})?)|(?:[0-9]|[1-5][0-9])(?:(?:\.[0-9]{1,2})?))$')))

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

            self.mode_check_fn.setFont(font12)
            self.mode_check_fn.setStyleSheet(stylesheet2)

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

        def make_tab_file():
            self.filename_lbl.setText("Имя файла:")
            self.filename_lbl.setFont(font14)
            self.filename_lbl.setStyleSheet(stylesheet2)

            self.filename_line.setFont(font14)
            self.filename_line.setStyleSheet(stylesheet1)
            if type(self.parent()) == OnlyShowWidget.WidgetWindow:
                self.filename_line.setDisabled(True)

            self.file_size_lbl.setText("Размер файла:")
            self.file_size_lbl.setFont(font14)
            self.file_size_lbl.setStyleSheet(stylesheet2)

            self.file_size_line.setFont(font14)
            self.file_size_line.setStyleSheet(stylesheet1)
            self.file_size_line.setDisabled(True)

            self.photo_rotate_right = QPushButton(self)
            self.photo_rotate_right.setText("Повернуть на 90° по часовой")
            self.photo_rotate_right.setFont(font14)
            self.photo_rotate_right.setStyleSheet(stylesheet1)

            self.photo_rotate_left = QPushButton(self)
            self.photo_rotate_left.setText("Повернуть на 90° против часовой")
            self.photo_rotate_left.setFont(font14)
            self.photo_rotate_left.setStyleSheet(stylesheet1)

            self.photo_flip_hor = QPushButton(self)
            self.photo_flip_hor.setText("Отразить по горизонтали")
            self.photo_flip_hor.setFont(font14)
            self.photo_flip_hor.setStyleSheet(stylesheet1)

            self.photo_flip_ver = QPushButton(self)
            self.photo_flip_ver.setText("Отразить по вертикали")
            self.photo_flip_ver.setFont(font14)
            self.photo_flip_ver.setStyleSheet(stylesheet1)

            self.thumbnail = QLabel(self)
            self.pixmap = QtGui.QPixmap(f"{self.photodirectory}/{self.photoname}").scaled(200, 300, QtCore.Qt.KeepAspectRatio)
            self.thumbnail.setPixmap(self.pixmap)

            self.tab_file_layout.addWidget(self.filename_lbl, 0, 0, 1, 1)
            self.tab_file_layout.addWidget(self.filename_line, 0, 1, 1, 2)
            self.tab_file_layout.addWidget(self.file_size_lbl, 1, 0, 1, 1)
            self.tab_file_layout.addWidget(self.file_size_line, 1, 1, 1, 2)
            self.tab_file_layout.addWidget(self.photo_rotate_right, 2, 2, 1, 1)
            self.tab_file_layout.addWidget(self.photo_rotate_left, 2, 0, 1, 1)
            self.tab_file_layout.addWidget(self.photo_flip_hor, 3, 0, 1, 1)
            self.tab_file_layout.addWidget(self.photo_flip_ver, 3, 2, 1, 1)
            self.tab_file_layout.addWidget(self.thumbnail, 2, 1, 2, 1)
            self.tab_file.setLayout(self.tab_file_layout)

            self.photo_flip_ver.setFixedWidth(300)
            self.photo_flip_hor.setFixedWidth(300)
            self.photo_rotate_left.setFixedWidth(300)
            self.photo_rotate_right.setFixedWidth(300)

        def make_tab_usercomment():
            self.usercomment_lbl.setText('Комментарий')
            self.usercomment_lbl.setFont(font14)
            self.usercomment_lbl.setStyleSheet(stylesheet2)
            self.usercomment_lbl.setAlignment(Qt.AlignCenter)
            
            self.usercomment_text.setFont(font12)
            self.usercomment_text.setStyleSheet(stylesheet1)

            self.tab_comment_layout.setAlignment(Qt.AlignTop)

            self.tab_comment_layout.addWidget(self.usercomment_lbl, 0, 0, 1, 1)
            self.tab_comment_layout.addWidget(self.usercomment_text, 1, 0, 1, 1)
            
            self.tab_comment.setLayout(self.tab_comment_layout)

        def make_connects():
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

            self.usercomment_text.textChanged.connect(lambda: self.changes_to_indicator(12))

            self.photo_flip_ver.clicked.connect(self.rotate_photo)
            self.photo_flip_hor.clicked.connect(self.rotate_photo)
            self.photo_rotate_left.clicked.connect(self.rotate_photo)
            self.photo_rotate_right.clicked.connect(self.rotate_photo)

        self.tabs.setStyleSheet(stylesheet7)
        self.tabs.currentChanged.connect(self.change_tab_gps)

        self.tabs.addTab(self.tab_date, 'Дата')
        self.tabs.addTab(self.tab_technic_settings, 'Оборудование и настройки')
        self.tabs.addTab(self.tab_GPS, 'GPS')
        self.tabs.addTab(self.tab_file, 'Файл')
        self.tabs.addTab(self.tab_comment, 'Комментарий')

        self.tabs.setFont(font12)

        make_tab_date()
        make_tab_tt()
        make_tab_gps()
        make_tab_file()
        make_tab_usercomment()
        make_connects()

    # Если поле было изменено, в списке "индикатор" меняется значение с индексом, соответствующем полю, с 0 на 1
    def changes_to_indicator(self, index: int) -> None:
        try:
            self.indicator[index] = 1
        except (IndexError, AttributeError):
            pass

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname: str, photodirectory: str) -> None:
        # все необходимые метаданные вместе
        data = Metadata.exif_show_edit(photodirectory + '/' + photoname)

        # преобразовать данные для отображения
        def date_convert(data):
            try:
                date_part = data['Время съёмки'].split(' ')[0]
                time_part = data['Время съёмки'].split(' ')[1]
            except IndexError:
                date_part = "0000:00:00"
                time_part = "00:00:00"

            try:
                year = int(date_part.split(":")[0])
            except ValueError:
                year = 0
            try:
                month = int(date_part.split(":")[1])
            except ValueError:
                month = 0
            try:
                day = int(date_part.split(":")[2])
            except ValueError:
                day = 0
            try:
                hour = int(time_part.split(":")[0])
            except ValueError:
                hour = 0
            try:
                minute = int(time_part.split(":")[1])
            except ValueError:
                minute = 0
            try:
                second = int(time_part.split(":")[2])
            except ValueError:
                second = 0

            try:
                zone_pm = data['Часовой пояс'][0]
                zone_hour = int(data['Часовой пояс'][1:].split(':')[0])
                zone_min = int(data['Часовой пояс'][1:].split(':')[1])
            except IndexError:
                zone_pm = "+"
                zone_hour = int("00")
                zone_min = int("00")

            return year, month, day, hour, minute, second, zone_pm, zone_hour, zone_min

        # изменение размеров таблицы и всего окна
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

        def fill_comment():
            self.usercomment_text.setText(str(data['Комментарий']))

        self.table.setColumnCount(2)
        self.table.setRowCount(len(data)-1)
        keys = list(data.keys())
        keys.remove('Комментарий')

        for parameter in range(len(data)-1):
            if keys[parameter] != 'Комментарий':
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
        fill_comment()

        func_resize()

    # считать и отобразить данные файла (имя и вес)
    def get_file_data(self, file_name: str, file_directory: str) -> None:
        file_name_splitted = file_name.split('.')
        self.picture_file_format = file_name_splitted[1]
        file_name_show = file_name_splitted[0]
        self.old_filename = file_name.split('.')[0]
        self.filename_line.setText(f"{file_name_show}")

        size = os.path.getsize(f"{file_directory}/{file_name}")

        if size < 1024:
            str_size = f'{round(size, 3)} байт\n'
        elif size < 1024**2:
            str_size = f'{round(size/1024, 3)} килобайт\n'
        elif size < 1024**3:
            str_size = f'{round(size/(1024**2), 3)} мегабайт\n'
        else:
            str_size = f'{round(size/(1024**3), 3)} гигабайт\n'

        self.file_size_line.setText(str_size)

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

            latitude = round((latitude_pm_coe*(latitude_deg + latitude_min/60 + latitude_sec/3600)), 4)
            longitude = round(longitude_pm_coe*(longitude_deg + longitude_min/60 + longitude_sec/3600), 4)

            self.latitude_fn_line.setText(str(latitude))
            self.longitude_fn_line.setText(str(longitude))
        else: # self.mode_check_fn.checkState() == 2
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
        usercomment = self.usercomment_text.text()

        timezone = self.timezone_pm_choose.currentText() + self.timezone_num_choose.text()
        datetime = self.date_choose.text().replace(".", ":")

        gps = self.latitude_fn_line.text() + ", " + self.longitude_fn_line.text()

        all_meta_entered = [maker, camera, lens, time, iso, fnumber, flenght, gps, timezone,
                            serialbody, seriallens, datetime, usercomment]

        return all_meta_entered

    # блокировать/разблокировать элементы ввода GPS при выборе разных вариантов ввода
    def block_check_gps(self) -> None:
        if self.sender().text() == "ШД Г.м.с":
            if self.mode_check_dmc.checkState() == 2:
                self.mode_check_fn.setCheckState(Qt.Unchecked)
            else:
                self.mode_check_fn.setCheckState(Qt.Checked)
        else: # self.sender().text() == "Числом":
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
        self.new_filename = self.filename_line.text()
        all_new_data = self.read_enter()
        changes_meta_dict = {}
        for i in range(len(all_new_data)):
            if self.indicator[i] == 1:
                changes_meta_dict[i] = all_new_data[i]
            else:
                pass

        self.write_changes(self.photoname, self.photodirectory, changes_meta_dict)

        if self.indicator[-2] == 0: # -1 - изменение даты (возможен перенос)
            self.update_show_data()
        else:
            if type(self.parent()) == ShowConstWindowWidget.ConstWidgetWindow:
                if self.filename_line.text() != self.old_filename and self.indicator[11] == 1:
                    win_warn = ErrorsAndWarnings.RenameTransferingPhoto(self)
                    win_warn.show()
                self.close()
                return
            else:
                self.update_show_data()

        self.indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if self.new_filename == self.old_filename:
            pass
        else:
            new_file_name = self.new_filename + '.' + self.picture_file_format
            if os.path.exists(f"{self.photodirectory}/{new_file_name}"):
                win_err = ErrorsAndWarnings.ExistFileRenameError2(self)
                win_err.show()
                return
            else:
                self.rename_file(self.photodirectory, self.photoname, new_file_name)
                self.renamed_signal.emit(new_file_name)
                self.close()

    # записать новые метаданные
    def write_changes(self, photoname: str, photodirectory: str, new_value_dict) -> None:
        # Перезаписать в exif и БД новые метаданные
        def rewriting(photoname: str, photodirectory: str, modify_dict) -> None:
            Metadata.exif_rewrite_edit(photoname, photodirectory, modify_dict)
            PhotoDataDB.edit_in_database(photoname, photodirectory, modify_dict)

        # проверка введённых пользователем метаданных
        def check_enter(editing_type: int, new_text: str) -> None:
            Metadata.exif_check_edit(editing_type, new_text)

        # проверка введённых пользователем метаданных
        for editing_type in list(new_value_dict.keys()):
            new_text = new_value_dict[editing_type]
            try:
                check_enter(editing_type, new_text)
            except ErrorsAndWarnings.EditExifError:
                win_err = ErrorsAndWarnings.EditExifErrorWin(self)
                win_err.show()
                return
            except ErrorsAndWarnings.EditCommentError as e:
                win_err = ErrorsAndWarnings.EditCommentErrorWin(self, e.symbol)
                win_err.show()
                return

        if 11 in list(new_value_dict.keys()) and type(self.parent()) == ShowConstWindowWidget.ConstWidgetWindow:
            date_dict = {}
            date_dict[11] = new_value_dict[11]
            new_value_dict.pop(11)
        # Если меняется дата -> проверка на перенос файла в новую папку
        # if editing_type == 11 and type(self.parent()) == ShowConstWindowWidget.ConstWidgetWindow:
            if photodirectory[-12:] == 'No_Date_Info':
                new_date = photodirectory[-38:]
            else:
                new_date = photodirectory[-10:]
            old_date = new_text[:10]
            new_date_splitted = new_date.split('/')
            old_date_splitted = old_date.split(':')
            if new_date_splitted == old_date_splitted:  # если дата та же, переноса не требуется
                rewriting(photoname, photodirectory, new_value_dict)
                rewriting(photoname, photodirectory, date_dict)
                self.edited_signal_no_move.emit()
            else:   # другая дата, требуется перенос файла
                destination = Settings.get_destination_media() + '/Media/Photo/const'
                year_new = new_date_splitted[0]
                month_new = new_date_splitted[1]
                day_new = new_date_splitted[2]

                year_old = old_date_splitted[0]
                month_old = old_date_splitted[1]
                day_old = old_date_splitted[2]

                new_file_fullname = destination + '/' + str(year_new) + '/' + str(month_new) + '/' + str(day_new) + '/' + photoname
                if not os.path.isdir(destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old)): # папки назначения нет -> сравнивать не надо
                    if not os.path.isdir(destination + '/' + str(year_old)):
                        os.mkdir(destination + '/' + str(year_old))
                    if not os.path.isdir(destination + '/' + str(year_old) + '/' + str(month_old)):
                        os.mkdir(destination + '/' + str(year_old) + '/' + str(month_old))
                    os.mkdir(destination + '/' + str(year_old) + '/' + str(month_old) + '/' + str(day_old))
                    rewriting(photoname, photodirectory, new_value_dict)
                    rewriting(photoname, photodirectory, date_dict)
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
                        rewriting(photoname, photodirectory, new_value_dict)
                        rewriting(photoname, photodirectory, date_dict)
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
            rewriting(photoname, photodirectory, new_value_dict)
            self.edited_signal.emit()

    # записать новые метаданные
    def clear_exif_func(self) -> None:
        def accepted():
            if 'No_Date_Info' in self.photodirectory:
                Metadata.clear_exif(self.photoname, self.photodirectory)
                PhotoDataDB.clear_metadata(self.photoname, self.photodirectory)
                self.get_metadata(self.photoname, self.photodirectory)
                self.close()
            else:
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
            self.edited_signal.emit()

        def rejected():
            win.close()

        win = ConfirmClear(self.parent())
        win.show()
        win.accept_signal.connect(accepted)
        win.reject_signal.connect(rejected)

    # переименование файла
    def rename_file(self, file_directory: str, file_name: str, new_name: str) -> None:
        PhotoDataDB.file_rename(file_directory, file_name, new_name)
        Thumbnail.file_rename(file_directory, file_name, new_name)
        shutil.move(f"{file_directory}/{file_name}", f"{file_directory}/{new_name}")

    # обновить данные в таблице/ на карте после записи метаданных
    def update_show_data(self):
        self.get_metadata(self.photoname, self.photodirectory)
        self.get_file_data(self.photoname, self.photodirectory)
        self.change_tab_gps()

    def rotate_photo(self):
        movement = self.sender().text()

        im = Image.open(f"{self.photodirectory}/{self.photoname}")
        file_exif = Metadata.read_exif(f"{self.photodirectory}/{self.photoname}")

        match movement:
            case "Повернуть на 90° по часовой":
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
            case "Повернуть на 90° против часовой":
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
            case "Отразить по горизонтали":
                im_flipped = im.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
            case "Отразить по вертикали":
                im_flipped = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            case _:
                im_flipped = im

        im_flipped.save(f"{self.photodirectory}/{self.photoname}", 'jpeg', quality=95, subsampling=0)
        im.close()
        im_flipped.close()

        for key in list(file_exif.keys()):
            if 'EXIF' in key or 'Composite' in key:
                pass
            else:
                file_exif.pop(key)

        with exiftool.ExifToolHelper() as et:
            et.set_tags(f"{self.photodirectory}/{self.photoname}",
                        tags=file_exif,
                        params=["-P", "-overwrite_original"])

        modify_dict = {}
        try:
            modify_dict['EXIF:GPSLatitudeRef'] = file_exif['EXIF:GPSLatitudeRef']
            modify_dict['EXIF:GPSLatitude'] = file_exif['EXIF:GPSLatitude']
            modify_dict['EXIF:GPSLongitudeRef'] = file_exif['EXIF:GPSLongitudeRef']
            modify_dict['EXIF:GPSLongitude'] = file_exif['EXIF:GPSLongitude']

            with exiftool.ExifToolHelper() as et:
                et.set_tags(f"{self.photodirectory}/{self.photoname}",
                            tags=modify_dict,
                            params=["-P", "-overwrite_original"])
        except KeyError:
            pass

        self.pixmap = QtGui.QPixmap(f"{self.photodirectory}/{self.photoname}").scaled(200, 300,
                                                                                      QtCore.Qt.KeepAspectRatio)
        self.thumbnail.setPixmap(self.pixmap)

        if 'const' in self.photodirectory.split('/'):
            Thumbnail.delete_thumbnail_const(self.photoname, self.photodirectory)
            Thumbnail.make_const_thumbnails(self.photodirectory, self.photoname)
        elif 'alone' in self.photodirectory.split('/'):
            Thumbnail.delete_thumbnail_alone(self.photoname, self.photodirectory)
            Thumbnail.make_alone_thumbnails(self.photodirectory.split('/')[-1], f"{self.photodirectory}/{self.photoname}", self.photoname)

        QtCore.QCoreApplication.processEvents()

        self.rotated_signal.emit()


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

        self.make_gui()

        self.show_photos()

    def make_gui(self):
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

        modify_dict = {11: self.full_exif_date}

        if self.new_checkbox.checkState():  # переименовывается переносимый файл
            new_new_name = self.new_name.text() + '.' + self.format

            if os.path.exists(self.old_photo_dir + new_new_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)
                err_win.show()
                return

            os.rename(self.new_photo_dir + self.file_full_name, self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg')
            shutil.move(self.new_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir)
            os.rename(self.old_photo_dir + 'aaabbbcccddddeeefffggghhh.jpg', self.old_photo_dir + new_new_name)

            PhotoDataDB.filename_after_transfer(self.file_full_name, new_new_name, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 0)
            Thumbnail.transfer_equal_date_thumbnail(self.file_full_name, self.file_full_name, self.old_date, self.new_date, new_new_name, 'new')
            Metadata.exif_rewrite_edit(new_new_name, self.old_photo_dir, modify_dict)
            PhotoDataDB.edit_in_database(new_new_name, self.old_photo_dir[:-1], modify_dict)
        else:       # переименовывается файл в папке назначения
            new_old_name = self.old_name.text() + '.' + self.format

            if os.path.exists(self.old_photo_dir + new_old_name):
                err_win = ErrorsAndWarnings.ExistFileRenameError2(self)
                err_win.show()
                return

            os.rename(self.old_photo_dir + self.file_full_name, self.old_photo_dir + new_old_name)
            shutil.move(self.new_photo_dir + self.file_full_name, self.old_photo_dir)

            PhotoDataDB.filename_after_transfer(self.file_full_name, new_old_name, self.new_photo_dir[:-1], self.old_photo_dir[:-1], 1)
            Thumbnail.transfer_equal_date_thumbnail(self.file_full_name, self.file_full_name, self.old_date, self.new_date, new_old_name, 'old')
            Metadata.exif_rewrite_edit(self.file_full_name, self.old_photo_dir[:-1], modify_dict)
            PhotoDataDB.edit_in_database(self.file_full_name, self.old_photo_dir[:-1], modify_dict)
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
