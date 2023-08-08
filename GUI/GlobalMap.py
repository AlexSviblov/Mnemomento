# coding: utf-8
import os
import folium
import base64
from Database import PhotoDataDB
from Metadata import MetadataPhoto
from GUI import Settings

from PyQt5 import QtWebEngineWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from pathlib import Path
from folium.plugins import MousePosition
from folium import IFrame
from PIL import Image, ImageFile

from GUI.FoliumRemastered import WebEnginePage, ClickForLatLng, LatLngPopup

from GUI.Screenconfig import *

ImageFile.LOAD_TRUNCATED_IMAGES = True


stylesheet1 = str()
stylesheet2 = str()
stylesheet5 = str()
stylesheet8 = str()
stylesheet9 = str()
map_tiles = str()
icon_explorer = str()
icon_view = str()


system_scale = monitor_info()[1]


class MapStartChooseWidget(QWidget):
    search_signal = QtCore.pyqtSignal()
    global_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout_main = QGridLayout(self)

        self.btn_search = QPushButton(self)
        self.btn_global = QPushButton(self)

        self.empty1 = QLabel(self)
        self.empty2 = QLabel(self)
        self.empty3 = QLabel(self)
        self.empty4 = QLabel(self)

        self.stylesheet_color()
        self.make_gui()

    def stylesheet_color(self) -> None:
        global stylesheet2
        global stylesheet5
        global stylesheet8
        global stylesheet9

        theme = Settings.get_theme_color()
        style = style_dict
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        stylesheet8 = style[f"{theme}"]["stylesheet8"]

        try:
            self.setStyleSheet(stylesheet2)
            self.btn_search.setStyleSheet(stylesheet8)
            self.btn_global.setStyleSheet(stylesheet8)
            self.empty1.setStyleSheet(stylesheet2)
            self.empty2.setStyleSheet(stylesheet2)
            self.empty3.setStyleSheet(stylesheet2)
            self.empty4.setStyleSheet(stylesheet2)
        except AttributeError:
            pass

    def make_gui(self) -> None:
        self.setLayout(self.layout_main)

        self.btn_search.setText("Поиск")
        self.btn_global.setText("Карта")

        self.btn_search.setFont(font16)
        self.btn_global.setFont(font16)

        self.btn_search.setFixedSize(200, 200)
        self.btn_global.setFixedSize(200, 200)

        self.empty1.setMinimumSize(5, 5)
        self.empty1.setMaximumSize(400, 400)

        self.empty2.setMinimumSize(5, 5)
        self.empty2.setMaximumSize(400, 400)

        self.empty3.setMinimumSize(5, 5)
        self.empty4.setMaximumSize(400, 400)

        self.empty4.setMinimumSize(5, 5)
        self.empty4.setMaximumSize(400, 400)

        self.layout_main.addWidget(self.btn_search, 1, 1, 1, 1)
        self.layout_main.addWidget(self.btn_global, 1, 2, 1, 1)
        self.layout_main.addWidget(self.empty1, 0, 0, 1, 1)
        self.layout_main.addWidget(self.empty2, 0, 3, 1, 1)
        self.layout_main.addWidget(self.empty3, 2, 0, 1, 1)
        self.layout_main.addWidget(self.empty4, 2, 3, 1, 1)

        self.btn_global.clicked.connect(self.global_signal.emit)
        self.btn_search.clicked.connect(self.search_signal.emit)


class GlobalMapWidget(QWidget):
    """

    """
    update_main_widget = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.stylesheet_color()

        self.soc_net_setting = Settings.get_socnet_status()

        self.layout_outside = QGridLayout(self)
        self.layout_outside.setSpacing(10)
        self.setLayout(self.layout_outside)

        self.layout_type = QGridLayout(self)
        self.layout_type.setAlignment(QtCore.Qt.AlignLeft)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(int(60*system_scale)+1)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.groupbox_sort.setLayout(self.layout_type)
        self.layout_outside.addWidget(self.groupbox_sort, 0, 1, 1, 1)

        self.empty = QLabel(self)
        self.layout_outside.addWidget(self.empty, 1, 0, 1, 3)

        self.progressbar = QProgressBar()
        self.progressbar.setFixedWidth(int(self.width()/4))
        self.progressbar.setFont(font14)
        self.progressbar.setStyleSheet(stylesheet5)
        self.layout_outside.addWidget(self.progressbar, 0, 3, 1, 1)
        self.progressbar.hide()

        self.fill_sort_groupbox()
        self.set_sort_layout()

        self.btn_show = QPushButton(self)
        self.btn_show.setText("Показать")
        self.btn_show.setFont(font14)
        self.btn_show.setStyleSheet(stylesheet8)
        self.btn_show.setFixedWidth(int(100*system_scale)+1)
        self.btn_show.setFixedHeight(int(30*system_scale)+1)
        self.layout_outside.addWidget(self.btn_show, 0, 4, 1, 1)
        self.btn_show.clicked.connect(self.pre_make_show_map)

        self.show_shortcut = QShortcut(QtGui.QKeySequence(Settings.get_hotkeys()["show_stat_map"]), self)
        self.show_shortcut.activated.connect(self.pre_make_show_map)

    def stylesheet_color(self) -> None:
        global stylesheet2
        global stylesheet5
        global stylesheet8
        global stylesheet9
        global map_tiles

        theme = Settings.get_theme_color()
        style = style_dict
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        stylesheet8 = style[f"{theme}"]["stylesheet8"]
        stylesheet9 = style[f"{theme}"]["stylesheet9"]
        map_tiles = style[f"{theme}"]["map_tiles"]

        try:
            self.groupbox_sort.setStyleSheet(stylesheet2)
            self.setStyleSheet(stylesheet2)
            self.set_sort_layout()
            self.btn_show.setStyleSheet(stylesheet8)
            self.group_type.setStyleSheet(stylesheet9)
        except AttributeError:
            pass

    def pre_make_show_map(self) -> None:
        """
        Вывести карту
        """
        try:
            self.warning_number.deleteLater()
        except (AttributeError, RuntimeError):
            pass

        self.layout_outside.addWidget(self.progressbar, 0, 3, 1, 1)

        self.progressbar.show()
        self.progressbar.setMaximum(100)
        match self.group_type.currentText():
            case "Дата":
                year = self.date_year.currentText()
                month = self.date_month.currentText()
                day = self.date_day.currentText()
                if not year or not month or not day:
                    return
                else:
                    full_paths = PhotoDataDB.get_date_photo_list(year, month, day, False, "")
            case "Соцсети":
                socnet = self.socnet_choose.currentText()
                status = self.sn_status.currentText()
                full_paths = PhotoDataDB.get_sn_photo_list(socnet, status, False, "")
            case "Оборудование":
                camera = self.camera_choose.currentText()
                lens = self.lens_choose.currentText()

                if camera == "All":
                    camera_exif = "All"
                else:
                    camera_exif = MetadataPhoto.equip_name_check_reverse(camera, "camera")

                if lens == "All":
                    lens_exif = "All"
                else:
                    lens_exif = MetadataPhoto.equip_name_check_reverse(lens, "lens")

                full_paths = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens, False, "")
            case _:
                return

        self.progressbar.setValue(0)
        self.progressbar.update()

        self.get_files_paths = PathsLooter(full_paths)
        self.get_files_paths.finished.connect(lambda result: self.make_show_map(result))
        self.get_files_paths.start()

    def make_show_map(self, result: tuple[list[str, tuple[float, float], str, str, str, bool], int, tuple[float, float]]):
        """

        :param result:
        :return:
        """
        map_points_combo = result[0]
        zoom_level = result[1]
        map_center = result[2]
        self.progressbar.setValue(1)
        self.progressbar.update()

        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()
        self.map_gps_widget.page().setBackgroundColor(QtCore.Qt.transparent)
        progress = 0
        locations = []
        if map_points_combo:
            if len(map_points_combo) > 100:
                self.map_gps = folium.Map(location=map_center, zoom_start=zoom_level, tiles=map_tiles)
                for photo in map_points_combo:
                    QtCore.QCoreApplication.processEvents()
                    locations.append(photo[1])
                    self.progressbar.setValue(int((progress/len(map_points_combo))*99+1))
                    self.progressbar.update()
                    progress += 1

                callback = ('function (row) {'
                            'var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red"});'
                            'var icon = L.AwesomeMarkers.icon({'
                            "icon: 'glyphicon glyphicon-picture',"
                            "iconColor: 'white',"
                            "markerColor: 'red',"
                            "prefix: 'glyphicon',"
                            '});'
                            'marker.setIcon(icon);'
                            'return marker};')
                options_dict = {"spiderfyOnMaxZoom": False, "singleMarkerMode": True}

                folium.plugins.FastMarkerCluster(locations, callback=callback, options=options_dict).add_to(self.map_gps)
                QtCore.QCoreApplication.processEvents()
            else:
                self.map_gps = folium.Map(location=map_center, zoom_start=zoom_level, tiles=map_tiles)
                marker_cluster = folium.plugins.MarkerCluster().add_to(self.map_gps)
                for photo in map_points_combo:
                    iframe = self.popup_html(photo[0], photo[2], photo[3], photo[4])
                    popup = folium.Popup(iframe)
                    folium.Marker(location=photo[1], popup=popup, icon=folium.Icon(color="red", icon="glyphicon glyphicon-camera")).add_to(marker_cluster)

                    self.progressbar.setValue(int((progress / len(map_points_combo)) * 99 + 1))
                    self.progressbar.update()
                    progress += 1

                QtCore.QCoreApplication.processEvents()

        else:
            self.map_gps = folium.Map(location=(55.755833, 37.61777), zoom_start=14)

        formatter = "function(num) {return L.Util.formatNum(num, 4) + ' º ';};"

        MousePosition(position="topright", separator=", ", empty_string="NaN",  lng_first=True,
                      num_digits=20, prefix="Координаты:", lat_formatter=formatter, lng_formatter=formatter).add_to(self.map_gps)

        popup1 = LatLngPopup()

        self.map_gps.add_child(popup1)

        self.map_gps_widget.setHtml(self.map_gps.get_root().render())

        self.layout_outside.addWidget(self.map_gps_widget, 1, 0, 1, 5)
        QtCore.QCoreApplication.processEvents()
        self.progressbar.hide()
        if len(map_points_combo) > 100:
            self.warning_number = QLabel()
            self.warning_number.setStyleSheet(stylesheet2)
            self.warning_number.setFont(font14)
            self.warning_number.setText("Ограниченный показ")
            self.layout_outside.addWidget(self.warning_number, 0, 2, 1, 1)
        QtCore.QCoreApplication.processEvents()

    def fill_date(self, mode: str) -> None:
        """
        Заполнение полей сортировки по дате
        :param mode:
        """
        # Получение годов
        def get_years() -> None:
            self.date_year.clear()
            j = 0
            k = 0
            dir_to_find_year = Settings.get_destination_media() + "/Media/Photo/const/"
            all_files_and_dirs = os.listdir(dir_to_find_year)
            dir_list = list()
            for name in all_files_and_dirs:
                if os.path.isdir(dir_to_find_year + name):
                    if len(os.listdir(dir_to_find_year + name)) >= 1:
                        for file in Path(dir_to_find_year + name).rglob("*"):
                            if os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG"):
                                k = 1
                        if k == 1:
                            k = 0
                            dir_list.append(name)

            dir_list.sort(reverse=True)
            i = 0
            for year in dir_list:
                if dir_list[i] != "No_Date_Info":
                    self.date_year.addItem(str(year))
                else:
                    j = 1
                i += 1
            if j == 1:
                self.date_year.addItem("No_Date_Info")
            else:
                pass
            self.date_year.addItem("All")

        # Получение месяцев в году
        def get_months() -> None:
            self.date_month.clear()
            year = self.date_year.currentText()
            if year == "All":
                self.date_month.addItem("All")
            else:
                dir_to_find_month = Settings.get_destination_media() + "/Media/Photo/const/" + year + "/"
                all_files_and_dirs = os.listdir(dir_to_find_month)
                dir_list = list()
                k = 0
                for name in all_files_and_dirs:
                    if os.path.isdir(dir_to_find_month + name):
                        if len(os.listdir(dir_to_find_month + name)) >= 1:
                            for file in Path(dir_to_find_month + name).rglob("*"):
                                if os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG"):
                                    k = 1
                            if k == 1:
                                k = 0
                                dir_list.append(name)

                dir_list.sort(reverse=True)
                for month in dir_list:
                    self.date_month.addItem(str(month))
                self.date_month.addItem("All")

        # Получение дней в месяце
        def get_days() -> None:
            self.date_day.clear()
            year = self.date_year.currentText()
            month = self.date_month.currentText()
            if year == "All" or month == "All":
                self.date_day.addItem("All")
            else:
                dir_to_find_day = Settings.get_destination_media() + "/Media/Photo/const/" + year + "/" + month + "/"
                all_files_and_dirs = os.listdir(dir_to_find_day)
                dir_list = list()
                for name in all_files_and_dirs:
                    if os.path.isdir(dir_to_find_day + name):
                        if len(os.listdir(dir_to_find_day + name)) >= 1:
                            dir_list.append(name)

                dir_list.sort(reverse=True)
                for day in dir_list:
                    self.date_day.addItem(str(day))
                self.date_day.addItem("All")

        match mode:
            case "date":
                get_years()
                get_months()
                get_days()
            case "year":
                get_years()
            case "month":
                get_months()
            case "day":
                get_days()
            case _:
                get_years()
                get_months()
                get_days()

    def fill_sort_groupbox(self) -> None:
        """
        Выбор способа группировки
        """
        self.group_type = QComboBox(self)
        self.group_type.addItem("Дата")
        if self.soc_net_setting:
            self.group_type.addItem("Соцсети")
        self.group_type.addItem("Оборудование")
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(int(152*system_scale)+1)
        self.group_type.setFixedHeight(int(30*system_scale)+1)
        self.group_type.setStyleSheet(stylesheet9)

        self.layout_outside.addWidget(self.group_type, 0, 0, 1, 1)

    def fill_sort_date(self) -> None:
        """
        Заполнить поле группировки по дате
        """
        self.year_lbl = QLabel(self)
        self.year_lbl.setFont(font14)
        self.year_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.year_lbl, 0, 1, 1, 1)

        self.date_year = QComboBox(self)
        self.date_year.setStyleSheet(stylesheet9)
        self.date_year.setFont(font14)
        self.date_year.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_year.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_year, 0, 2, 1, 1)

        self.month_lbl = QLabel(self)
        self.month_lbl.setFont(font14)
        self.month_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.month_lbl, 0, 3, 1, 1)

        self.date_month = QComboBox(self)
        self.date_month.setFont(font14)
        self.date_month.setStyleSheet(stylesheet9)
        self.date_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_month.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1)

        self.day_lbl = QLabel(self)
        self.day_lbl.setFont(font14)
        self.day_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.day_lbl, 0, 5, 1, 1)

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_day.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1)

        self.fill_date("date")

        if not self.year_lbl.text():
            self.year_lbl.setText("Год:")
            self.month_lbl.setText("    Месяц:")
            self.day_lbl.setText("    День:")

        self.date_day.setFixedHeight(int(30*system_scale)+1)
        self.date_month.setFixedHeight(int(30*system_scale)+1)
        self.date_year.setFixedHeight(int(30*system_scale)+1)
        self.day_lbl.setFixedHeight(30)
        self.month_lbl.setFixedHeight(30)
        self.year_lbl.setFixedHeight(30)

        self.date_year.currentTextChanged.connect(lambda: self.fill_date("month"))
        self.date_month.currentTextChanged.connect(lambda: self.fill_date("day"))

    def fill_sort_socnets(self) -> None:
        """
        Заполнить поле группировки по соцсетям
        """
        self.socnet_choose = QComboBox(self)
        self.socnet_choose.setFont(font14)
        self.socnet_choose.setFixedHeight(int(30*system_scale)+1)
        self.socnet_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.socnet_choose, 0, 1, 1, 1)
        socnets = PhotoDataDB.get_socialnetworks()

        if not socnets:
            self.socnet_choose.addItem("Нет данных")
            self.socnet_choose.setFixedWidth(int(150*system_scale)+1)
        else:
            socnet_max_len = 0
            for net in socnets:
                if net[0:9] != "numnumnum":
                    self.socnet_choose.addItem(f"{net}")
                    if len(net) > socnet_max_len:
                        socnet_max_len = len(net)
                else:
                    self.socnet_choose.addItem(f"{net[9:]}")
                    if len(net) - 9 > socnet_max_len:
                        socnet_max_len = len(net) - 9

            self.socnet_choose.setFixedWidth(int((socnet_max_len * 12 + 30)*system_scale)+1)

            self.sn_status = QComboBox(self)
            self.sn_status.setFont(font14)
            self.sn_status.setFixedHeight(int(30*system_scale)+1)
            self.sn_status.setStyleSheet(stylesheet9)
            self.sn_status.addItem("Не выбрано")
            self.sn_status.addItem("Не публиковать")
            self.sn_status.addItem("Опубликовать")
            self.sn_status.addItem("Опубликовано")
            self.sn_status.setFixedWidth(int(164*system_scale)+1)
            self.layout_type.addWidget(self.sn_status, 0, 2, 1, 1)

    def fill_sort_equipment(self) -> None:
        """
        Заполнить поле группировки по оборудованию
        """
        self.camera_choose = QComboBox(self)
        self.camera_choose.setFont(font14)
        self.camera_choose.setFixedHeight(int(30*system_scale)+1)
        self.camera_choose.setStyleSheet(stylesheet9)
        self.lens_choose = QComboBox(self)
        self.lens_choose.setFont(font14)
        self.lens_choose.setFixedHeight(int(30*system_scale)+1)
        self.lens_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.camera_choose, 0, 1, 1, 1)
        self.layout_type.addWidget(self.lens_choose, 0, 2, 1, 1)

        cameras, lenses = PhotoDataDB.get_equipment()
        camera_max_len = 0
        lens_max_len = 0

        for camera in cameras:
            self.camera_choose.addItem(f"{camera}")
            if len(camera) > camera_max_len:
                camera_max_len = len(camera)
        self.camera_choose.addItem("All")

        for lens in lenses:
            self.lens_choose.addItem(f"{lens}")
            if len(lens) > lens_max_len:
                lens_max_len = len(lens)
        self.lens_choose.addItem("All")

        self.camera_choose.setFixedWidth(int((camera_max_len * 12)*system_scale)+1)
        self.lens_choose.setFixedWidth(int((lens_max_len * 12)*system_scale)+1)

    def set_sort_layout(self) -> None:
        """
        Заполнить нужное поле в зависимости от выбранного типа группировки
        """
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().hide()
            self.layout_type.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        match self.group_type.currentText():
            case "Дата":
                self.fill_sort_date()
            case "Соцсети":
                self.fill_sort_socnets()
            case "Оборудование":
                self.fill_sort_equipment()

    def popup_html(self, photo_name: str, shooting_date: str, camera: str, thumbnail_way: str) -> IFrame:
        """

        :param photo_name:
        :param shooting_date:
        :param camera:
        :param thumbnail_way:
        :return:
        """
        if shooting_date != "":
            date_splitted = shooting_date.split(".")
            date_show = f"{date_splitted[-1]}.{date_splitted[-2]}.{date_splitted[-3]}"
        else:
            date_show = ""

        encoded = base64.b64encode(open(f"{thumbnail_way}", "rb").read())
        html_img_str = '<center><img src="data:image/png;base64,{}"></center>'
        html = f"""
       <html>
           """ + html_img_str + f"""
           <center><h4 width="200px">{photo_name}</h4></center>
           <center> <table style="height: 80px; width: 305px; border: 1px solid black;">
               <tbody>
                   <tr>
                       <td style="background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;"><span style="color: #000000; ">Дата съёмки </span></td>
                       <td style="width: 150px;background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;">{date_show}</td>
                   </tr>
                   <tr>
                       <td style="background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;"><span style="color: #000000; ">Камера </span></td>
                       <td style="width: 150px;background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;">{camera}</td>
                   </tr>
               </tbody>
           </table></center>
       </html>
       """

        html_show = html.format

        im = Image.open(thumbnail_way)
        width, height = im.size

        if width > height:
            iframe = IFrame(html_show(encoded.decode("UTF-8")), width=380, height=380)
        else:
            iframe = IFrame(html_show(encoded.decode("UTF-8")), width=380, height=410)

        return iframe

    def popup_html_group(self, photo_data_list: list[list[str, str, str, str, bool]]) -> IFrame:
        """

        :param photo_data_list:
        :return:
        """
        html_result = f"""
               <html>
                   """
        i = 0
        for photo in photo_data_list:

            photo_name = photo[0]
            shooting_date = photo[2]
            camera = photo[3]
            thumbnail_way = photo[4]

            if shooting_date != "":
                date_splitted = shooting_date.split(".")
                date_show = f"{date_splitted[-1]}.{date_splitted[-2]}.{date_splitted[-3]}"
            else:
                date_show = ""

            encoded = base64.b64encode(open(f"{thumbnail_way}", "rb").read())
            if i == 0:
                html_img_str = '<center><img src="data:image/png;base64,{}"></center>'
            else:
                html_img_str = """
                                    <br>
                                    <br>
                                    <br>
                                    <br>
                                    <br>
                                <center><img src="data:image/png;base64,{}"></center>"""

            html = html_img_str + f"""
                       <center><h4 width="200px">{photo_name}</h4></center>
                       <center> <table style="height: 80px; width: 305px; border: 1px solid black;">
                           <tbody>
                               <tr>
                                   <td style="background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;"><span style="color: #000000; ">Дата съёмки </span></td>
                                   <td style="width: 150px;background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;">{date_show}</td>
                               </tr>
                               <tr>
                                   <td style="background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;"><span style="color: #000000; ">Камера </span></td>
                                   <td style="width: 150px;background-color: #F0F0F0; border: 1px solid black; text-align: center; font-size: 16px;">{camera}</td>
                               </tr>
                           </tbody>
                       </table></center>
                        """
            html_show = html.format
            html_result += html_show(encoded.decode("UTF-8"))
            i += 1

        html_result += """</html>
           """

        iframe = IFrame(html_result, width=380, height=410)

        return iframe


class PathsLooter(QtCore.QThread):
    """

    """
    finished = QtCore.pyqtSignal(tuple)

    def __init__(self, full_paths: list[str]):
        QtCore.QThread.__init__(self)
        self.full_paths = full_paths

    def run(self):
        try:
            map_points_combo, zoom_level, map_center = PhotoDataDB.get_global_map_info(self.full_paths)
        except IndexError:
            map_points_combo, zoom_level, map_center = "", "", ""
        self.finished.emit((map_points_combo, zoom_level, map_center))


class LocationSearcherWidget(QWidget):
    open_main_catalog_by_map = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout_main = QGridLayout(self)

        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

        self.groupbox_photos = QGroupBox(self)
        self.scroll_area = QScrollArea(self)
        self.layout_group = QGridLayout(self)

        self.top_box_group = QGroupBox(self)
        self.layout_top_box = QGridLayout(self)

        self.distance_lbl = QLabel(self)
        self.distance_edit = QLineEdit(self)

        self.stylesheet_color()
        self.make_gui()

    def stylesheet_color(self) -> None:
        global stylesheet1
        global stylesheet2
        global icon_explorer
        global icon_view

        theme = Settings.get_theme_color()
        style = style_dict
        stylesheet1 = style[f"{theme}"]["stylesheet1"]
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        icon_explorer = style[f"{theme}"]["icon_explorer"]
        icon_view = style[f"{theme}"]["icon_view"]

        try:
            self.setStyleSheet(stylesheet2)
            self.groupbox_photos.setStyleSheet(stylesheet1)
            self.top_box_group.setStyleSheet(stylesheet1)
            self.scroll_area.setStyleSheet(stylesheet2)
        except AttributeError:
            pass

    def make_gui(self) -> None:
        def make_map() -> None:
            self.map_gps_widget.page().setBackgroundColor(QtCore.Qt.transparent)

            map_gps = folium.Map(location=(55.755833, 37.61777), zoom_start=14)
            map_gps.add_child(ClickForLatLng(format_str='lat + "," + lng'))

            popup = LatLngPopup()
            map_gps.add_child(popup)

            page = WebEnginePage(self.map_gps_widget)
            page.coordinates_transfer.connect(self.get_photo_for_place)
            self.map_gps_widget.setPage(page)

            self.map_gps_widget.setHtml(map_gps.get_root().render())
            self.map_gps_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout_main.addWidget(self.map_gps_widget, 1, 0, 1, 1)

        def make_scroll_area() -> None:
            self.groupbox_photos.setLayout(self.layout_group)

            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setWidget(self.groupbox_photos)

            self.layout_main.addWidget(self.scroll_area, 1, 1, 1, 1)

        def make_top_box() -> None:
            self.top_box_group.setLayout(self.layout_top_box)
            self.layout_main.addWidget(self.top_box_group, 0, 0, 1, 2)

            self.distance_lbl.setText("Расстояние поиска [м]:")
            self.distance_lbl.setFont(font10)
            self.distance_lbl.setStyleSheet(stylesheet2)

            self.distance_edit.setValidator(QtGui.QIntValidator(1, 1000000))
            self.distance_edit.setText("1000")
            self.distance_edit.setFont(font10)
            self.distance_edit.setStyleSheet(stylesheet1)

            self.layout_top_box.addWidget(self.distance_lbl, 0, 0, 1, 1)
            self.layout_top_box.addWidget(self.distance_edit, 0, 1, 1, 1)

        self.setLayout(self.layout_main)
        make_map()
        make_scroll_area()
        make_top_box()

    def get_photo_for_place(self, js_msg: str):
        for i in reversed(range(self.layout_group.count())):
            self.layout_group.itemAt(i).widget().hide()
            self.layout_group.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        coordinates = [float(js_msg.split(",")[0]), float(js_msg.split(",")[1])]
        nearly_photos_list = PhotoDataDB.search_nearly_photos(coordinates, distance=int(self.distance_edit.text()))
        for photo in nearly_photos_list:
            catalog_splitted = photo[1].split("/")
            day = catalog_splitted[-1]
            month = catalog_splitted[-2]
            year = catalog_splitted[-3]
            thumbnail_way = f"{Settings.get_destination_thumb()}/thumbnail/const/{year}/{month}/{day}/thumbnail_{photo[0]}"
            photo.append(thumbnail_way)

        self.fill_scroll_thumbs(nearly_photos_list)

    def fill_scroll_thumbs(self, photo_data_list: list[str]):
        i = 0
        for photo in photo_data_list:
            photo_group = QGroupBox()
            photo_layout = QGridLayout()
            photo_group.setLayout(photo_layout)
            photo_group.setMaximumHeight(300)

            button = QToolButton()
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            iqon = QtGui.QIcon(photo[6])
            iqon.pixmap(250, 250)
            button.setMinimumHeight(280)
            button.setFixedWidth(260)
            button.setIcon(iqon)
            button.setIconSize(QtCore.QSize(250, 250))
            button.setText(photo[0])
            button.setObjectName(f"{photo[1]}/{photo[0]}")
            button.setFont(font10)
            button.setStyleSheet(stylesheet1)
            button.clicked.connect(self.open_main_catalog)

            photo_layout.addWidget(button, 0, 0, 3, 1, alignment=QtCore.Qt.AlignVCenter)

            description_lbl = QLabel()
            description_lbl.setText(f"Камера: {photo[3]}\n\n"
                                    f"Объектив: {photo[4]}\n\n"
                                    f"{photo[5][8:]}.{photo[5][5:7]}.{photo[5][:4]}")
            description_lbl.setFont(font10)
            description_lbl.setStyleSheet(stylesheet2)
            photo_layout.addWidget(description_lbl, 0, 1, 3, 1)

            explorer_btn = QToolButton()
            explorer_btn.setStyleSheet(stylesheet1)
            explorer_btn.setIcon(QtGui.QIcon(icon_explorer))
            explorer_btn.setIconSize(QtCore.QSize(30, 30))
            explorer_btn.setToolTip("Показать в проводнике")
            explorer_btn.setFixedSize(30, 30)
            explorer_btn.setObjectName(f"{photo[1]}/{photo[0]}")
            explorer_btn.clicked.connect(self.call_explorer)

            open_file_btn = QToolButton(self)
            open_file_btn.setStyleSheet(stylesheet1)
            open_file_btn.setIcon(QtGui.QIcon(icon_view))
            open_file_btn.setIconSize(QtCore.QSize(30, 30))
            open_file_btn.setToolTip("Открыть")
            open_file_btn.setFixedSize(30, 30)
            open_file_btn.setObjectName(f"{photo[1]}/{photo[0]}")
            open_file_btn.clicked.connect(self.open_file_func)

            photo_layout.addWidget(explorer_btn, 0, 2, 1, 1)
            photo_layout.addWidget(open_file_btn, 2, 2, 1, 1)

            self.layout_group.addWidget(photo_group, i, 0, 1, 1)
            i += 1
            QtCore.QCoreApplication.processEvents()

            # TODO: функциональные кнопки: открыть в осн.каталоге, открыть сам файл, открыть в проводнике
            # TODO: метки на карте
            # TODO: поиск по координатам

    def call_explorer(self):
        open_path = self.sender().objectName().replace("/", "\\")
        os.system(f'explorer /select,\"{open_path}\"')

    def open_file_func(self):
        open_path = self.sender().objectName().replace("/", "\\")
        os.startfile(open_path)

    def open_main_catalog(self):
        photo_path = self.sender().objectName()
        self.open_main_catalog_by_map.emit(photo_path)
