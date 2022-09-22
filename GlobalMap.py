import sys
import os
import folium

from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import json
import PhotoDataDB
import Metadata
import Settings
import Thumbnail


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()

font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


# объект окна настроек
class GlobalMapWin(QMainWindow):
    update_main_widget = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()

        # Создание окна
        self.setWindowTitle('Настройки')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.map_widget = GlobalMapWidget()

        self.setCentralWidget(self.map_widget)
        self.resize(self.map_widget.size())

    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global stylesheet9
        global loading_icon

        if Settings.get_theme_color() == 'light':
            stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0"
            stylesheet2 = "border: 0px; color: #000000; background-color: #F0F0F0"
            stylesheet8 = "QPushButton{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0}" \
                          "QPushButton::pressed{border: 2px; background-color: #C0C0C0; margin-top: -1px}"
            stylesheet9 = "QComboBox {border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;}" \
                          "QComboBox QAbstractItemView {selection-background-color: #C0C0C0;}"
            loading_icon = os.getcwd() + '/icons/loading_light.gif'
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C"
            stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #1C1C1C"
            stylesheet8 = "QPushButton{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C}" \
                          "QPushButton::pressed{border: 2px; background-color: #2F2F2F; margin-top: -1px}"
            stylesheet9 = "QComboBox {border: 1px; border-color: #696969; border-style: solid; background-color: #1C1C1C; color: #D3D3D3;}" \
                          "QComboBox QAbstractItemView {selection-background-color: #4F4F4F;}"
            loading_icon = os.getcwd() + '/icons/loading_dark.gif'
        try:
            self.map_widget.groupbox_sort.setStyleSheet(stylesheet2)
            self.setStyleSheet(stylesheet2)
            self.map_widget.setStyleSheet(stylesheet2)
            self.map_widget.set_sort_layout()
        except AttributeError:
            pass



class GlobalMapWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.soc_net_setting = int(settings["social_networks_status"])

        self.layout_outside = QGridLayout(self)
        self.setLayout(self.layout_outside)

        self.layout_type = QGridLayout(self)
        self.layout_type.setHorizontalSpacing(5)
        self.layout_type.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(50)
        self.groupbox_sort.setAlignment(QtCore.Qt.AlignVCenter)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.groupbox_sort.setLayout(self.layout_type)

        self.layout_outside.addWidget(self.groupbox_sort, 0, 1, 1, 1)

        self.fill_sort_groupbox()
        self.set_sort_layout()

        self.btn_show = QPushButton(self)
        self.btn_show.setText('Показать')
        self.btn_show.setFont(font14)
        self.btn_show.setStyleSheet(stylesheet8)
        self.btn_show.setFixedSize(100, 31)
        self.layout_outside.addWidget(self.btn_show, 0, 2, 1, 1,alignment=QtCore.Qt.AlignVCenter)
        self.btn_show.clicked.connect(self.make_show_map)

    # вывести карту
    def make_show_map(self):
        sort_type = self.group_type.currentText()
        if sort_type == 'Дата':
            year = self.date_year.currentText()
            month = self.date_month.currentText()
            day = self.date_day.currentText()
            full_paths = PhotoDataDB.get_date_photo_list(year, month, day)
        elif sort_type == 'Соцсети':
            socnet = self.socnet_choose.currentText()
            status = self.sn_status.currentText()
            full_paths = PhotoDataDB.get_sn_photo_list(socnet, status)
        elif sort_type == 'Оборудование':
            camera = self.camera_choose.currentText()
            lens = self.lens_choose.currentText()
            camera_exif = Metadata.equip_name_check_reverse(camera, 'camera')
            lens_exif = Metadata.equip_name_check_reverse(lens, 'lens')
            full_paths = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens)

        map_points_combo = PhotoDataDB.get_const_coordinates(full_paths)
        print(map_points_combo)
        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()
        if map_points_combo:
            self.map_gps = folium.Map(location=map_points_combo[0][1], zoom_start=14)
            for photo in map_points_combo:
                folium.Marker(photo[1], popup=photo[0], icon=folium.Icon(color='red')).add_to(self.map_gps)
        else:
            self.map_gps = folium.Map(location=(55.755833, 37.61777), zoom_start=14)
        self.map_gps_widget.setHtml(self.map_gps.get_root().render())

        self.layout_outside.addWidget(self.map_gps_widget, 1, 0, 1, 3)

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

    # выбор способа группировки
    def fill_sort_groupbox(self) -> None:
        self.group_type = QComboBox(self)
        self.group_type.addItem('Дата')
        if self.soc_net_setting:
            self.group_type.addItem('Соцсети')
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

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.get_days()
        self.date_day.setFixedWidth(140)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1, alignment=QtCore.Qt.AlignVCenter)

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

        self.date_year.currentTextChanged.connect(self.get_months)
        self.date_month.currentTextChanged.connect(self.get_days)

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

            self.socnet_choose.setFixedWidth(socnet_max_len * 12 + 30)

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

        self.camera_choose.setFixedWidth(camera_max_len * 12)
        self.lens_choose.setFixedWidth(lens_max_len * 12)

    # заполнить нужное поле в зависимости от выбранного типа группировки
    def set_sort_layout(self) -> None:
        sort_type = self.group_type.currentText()

        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().hide()
            self.layout_type.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        if sort_type == 'Дата':
            self.fill_sort_date()
        elif sort_type == 'Соцсети':
            self.fill_sort_socnets()
        elif sort_type == 'Оборудование':
            self.fill_sort_equipment()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GlobalMapWin()
    win.show()
    sys.exit(app.exec_())
