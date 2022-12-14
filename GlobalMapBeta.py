import os
import folium
import json
import base64
from PyQt5 import QtWebEngineWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from pathlib import Path
from folium.plugins import MousePosition
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from folium import IFrame

import PhotoDataDB
import Metadata
import Screenconfig
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet5 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()
map_tiles = str()

font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


system_scale = Screenconfig.monitor_info()[1]


class GlobalMapWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.stylesheet_color()

        self.soc_net_setting = Settings.get_socnet_status()

        self.layout_outside = QGridLayout(self)
        self.setLayout(self.layout_outside)

        self.layout_type = QGridLayout(self)
        self.layout_type.setHorizontalSpacing(5)
        self.layout_type.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(int(60*system_scale)+1)
        self.groupbox_sort.setAlignment(QtCore.Qt.AlignVCenter)
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
        self.btn_show.setText('Показать')
        self.btn_show.setFont(font14)
        self.btn_show.setStyleSheet(stylesheet8)
        self.btn_show.setFixedSize(int(100*system_scale)+1, int(30*system_scale)+1)
        self.layout_outside.addWidget(self.btn_show, 0, 2, 1, 1)
        self.btn_show.clicked.connect(self.make_show_map)

    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet5
        global stylesheet8
        global stylesheet9
        global loading_icon
        global map_tiles

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
            stylesheet5 =   """
                                QProgressBar
                                {
                                    border: 1px;
                                    border-color: #000000;
                                    border-style: solid;
                                    background-color: #FFFFFF;
                                    color: #000000
                                }
                                QProgressBar::chunk
                                {
                                    background-color: #00FF7F;  
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
            map_tiles = "OpenStreetMap"
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
            stylesheet5 =   """
                                QProgressBar
                                {
                                    border: 1px;
                                    border-color: #000000;
                                    border-style: solid;
                                    background-color: #CCCCCC;
                                    color: #000000
                                }
                                QProgressBar::chunk
                                {
                                    background-color: #1F7515;
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
            loading_icon = os.getcwd() + '/icons/loading_dark.gif'
            map_tiles = "OpenStreetMap"

        try:
            self.groupbox_sort.setStyleSheet(stylesheet2)
            self.setStyleSheet(stylesheet2)
            self.set_sort_layout()
            self.btn_show.setStyleSheet(stylesheet8)
            self.group_type.setStyleSheet(stylesheet9)
        except AttributeError:
            pass

    # вывести карту
    def make_show_map(self) -> None:
        self.progressbar.show()
        self.progressbar.setMaximum(100)
        match self.group_type.currentText():
            case 'Дата':
                year = self.date_year.currentText()
                month = self.date_month.currentText()
                day = self.date_day.currentText()
                full_paths = PhotoDataDB.get_date_photo_list(year, month, day)
            case 'Соцсети':
                socnet = self.socnet_choose.currentText()
                status = self.sn_status.currentText()
                full_paths = PhotoDataDB.get_sn_photo_list(socnet, status)
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

                full_paths = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens)

        self.progressbar.setValue(1)
        QtCore.QCoreApplication.processEvents()
        map_points_combo, zoom_level, map_center = PhotoDataDB.get_global_map_info(full_paths)

        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()
        progress = 0
        print(len(map_points_combo))
        if map_points_combo:
            self.map_gps = folium.Map(location=map_center, zoom_start=zoom_level, tiles=map_tiles)
            photo_grouped_shown = list()
            for photo in map_points_combo:

                QtCore.QCoreApplication.processEvents()
                if not photo[5]:
                    iframe = self.popup_html(photo[0], photo[2], photo[3], photo[4])
                    popup = folium.Popup(iframe)
                    folium.Marker(location=photo[1], popup=popup,
                                  icon=folium.Icon(color='red', icon='glyphicon glyphicon-picture')).add_to(self.map_gps)
                    photo_grouped_shown.append(photo)
                else: # несколько фото с 1 меткой GPS
                    if photo not in photo_grouped_shown:
                        group_photo_list = list()
                        for photo_compare in map_points_combo:
                            if photo_compare[1] == photo[1] and not photo_compare[4] == photo[4]:
                                group_photo_list.append(photo_compare)
                                photo_grouped_shown.append(photo_compare)
                            else: # совпадение координат
                                pass
                        if len(group_photo_list) > 0:
                            group_photo_list.append(photo)
                            photo_grouped_shown.append(photo)
                            iframe = self.popup_html_group(group_photo_list)
                            popup = folium.Popup(iframe)
                            folium.Marker(location=photo[1], popup=popup,
                                          icon=folium.Icon(color='red', icon='glyphicon glyphicon-camera')).add_to(
                                self.map_gps)
                        else:
                            pass
                QtCore.QCoreApplication.processEvents()
                progress += 1
                self.progressbar.setValue(int((progress/len(map_points_combo))*99+1))
                QtCore.QCoreApplication.processEvents()

        else:
            self.map_gps = folium.Map(location=(55.755833, 37.61777), zoom_start=14)

        formatter = "function(num) {return L.Util.formatNum(num, 4) + ' º ';};"

        MousePosition(position="topright", separator=", ", empty_string="NaN",  lng_first=True,
            num_digits=20, prefix="Координаты:", lat_formatter=formatter, lng_formatter=formatter).add_to(self.map_gps)

        popup1 = folium.LatLngPopup()

        self.map_gps.add_child(popup1)

        self.map_gps_widget.setHtml(self.map_gps.get_root().render())

        self.layout_outside.addWidget(self.map_gps_widget, 1, 0, 1, 4)
        QtCore.QCoreApplication.processEvents()
        self.progressbar.hide()
        QtCore.QCoreApplication.processEvents()

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

    # выбор способа группировки
    def fill_sort_groupbox(self) -> None:
        self.group_type = QComboBox(self)
        self.group_type.addItem('Дата')
        if self.soc_net_setting:
            self.group_type.addItem('Соцсети')
        self.group_type.addItem('Оборудование')
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(int(152*system_scale)+1)
        self.group_type.setFixedHeight(int(30*system_scale)+1)
        self.group_type.setStyleSheet(stylesheet9)

        self.layout_outside.addWidget(self.group_type, 0, 0, 1, 1)

    # заполнить поле группировки по дате
    def fill_sort_date(self) -> None:
        self.year_lbl = QLabel(self)
        self.year_lbl.setFont(font14)
        self.year_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.year_lbl, 0, 1, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.date_year = QComboBox(self)
        self.date_year.setStyleSheet(stylesheet9)
        self.date_year.setFont(font14)
        self.date_year.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_year.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_year, 0, 2, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.month_lbl = QLabel(self)
        self.month_lbl.setFont(font14)
        self.month_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.month_lbl, 0, 3, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.date_month = QComboBox(self)
        self.date_month.setFont(font14)
        self.date_month.setStyleSheet(stylesheet9)
        self.date_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_month.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.day_lbl = QLabel(self)
        self.day_lbl.setFont(font14)
        self.day_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(self.day_lbl, 0, 5, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_day.setFixedWidth(int(140*system_scale)+1)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1, alignment=QtCore.Qt.AlignVCenter)

        self.fill_date('date')

        if not self.year_lbl.text():
            self.year_lbl.setText('Год:')
            self.month_lbl.setText('    Месяц:')
            self.day_lbl.setText('    День:')

        self.date_day.setFixedHeight(int(30*system_scale)+1)
        self.date_month.setFixedHeight(int(30*system_scale)+1)
        self.date_year.setFixedHeight(int(30*system_scale)+1)
        self.day_lbl.setFixedHeight(30)
        self.month_lbl.setFixedHeight(30)
        self.year_lbl.setFixedHeight(30)

        self.date_year.currentTextChanged.connect(lambda: self.fill_date('month'))
        self.date_month.currentTextChanged.connect(lambda: self.fill_date('day'))

    # заполнить поле группировки по соцсетям
    def fill_sort_socnets(self) -> None:
        self.socnet_choose = QComboBox(self)
        self.socnet_choose.setFont(font14)
        self.socnet_choose.setFixedHeight(int(30*system_scale)+1)
        self.socnet_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.socnet_choose, 0, 1, 1, 1)
        socnets = PhotoDataDB.get_socialnetworks()

        if not socnets:
            self.socnet_choose.addItem('Нет данных')
            self.socnet_choose.setFixedWidth(int(150*system_scale)+1)
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

            self.socnet_choose.setFixedWidth(int((socnet_max_len * 12 + 30)*system_scale)+1)

            self.sn_status = QComboBox(self)
            self.sn_status.setFont(font14)
            self.sn_status.setFixedHeight(int(30*system_scale)+1)
            self.sn_status.setStyleSheet(stylesheet9)
            self.sn_status.addItem('Не выбрано')
            self.sn_status.addItem('Не публиковать')
            self.sn_status.addItem('Опубликовать')
            self.sn_status.addItem('Опубликовано')
            self.sn_status.setFixedWidth(int(164*system_scale)+1)
            self.layout_type.addWidget(self.sn_status, 0, 2, 1, 1)

    # заполнить поле группировки по оборудованию
    def fill_sort_equipment(self) -> None:
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
            self.camera_choose.addItem(f'{camera}')
            if len(camera) > camera_max_len:
                camera_max_len = len(camera)
        self.camera_choose.addItem('All')

        for lens in lenses:
            self.lens_choose.addItem(f'{lens}')
            if len(lens) > lens_max_len:
                lens_max_len = len(lens)
        self.lens_choose.addItem('All')

        self.camera_choose.setFixedWidth(int((camera_max_len * 12)*system_scale)+1)
        self.lens_choose.setFixedWidth(int((lens_max_len * 12)*system_scale)+1)

    # заполнить нужное поле в зависимости от выбранного типа группировки
    def set_sort_layout(self) -> None:
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().hide()
            self.layout_type.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        match self.group_type.currentText():
            case 'Дата':
                self.fill_sort_date()
            case 'Соцсети':
                self.fill_sort_socnets()
            case 'Оборудование':
                self.fill_sort_equipment()

    def popup_html(self, photo_name: str, shooting_date: str, camera: str, thumbnail_way: str) -> IFrame:
        if shooting_date != "":
            date_splitted = shooting_date.split('.')
            date_show = f"{date_splitted[-1]}.{date_splitted[-2]}.{date_splitted[-3]}"
        else:
            date_show = ""

        encoded = base64.b64encode(open(f'{thumbnail_way}', 'rb').read())
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
            iframe = IFrame(html_show(encoded.decode('UTF-8')), width=380, height=380)
        else:
            iframe = IFrame(html_show(encoded.decode('UTF-8')), width=380, height=410)

        return iframe

    def popup_html_group(self, photo_data_list: list[list[str, str, str, str, bool]]) -> IFrame:
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
                date_splitted = shooting_date.split('.')
                date_show = f"{date_splitted[-1]}.{date_splitted[-2]}.{date_splitted[-3]}"
            else:
                date_show = ""

            encoded = base64.b64encode(open(f'{thumbnail_way}', 'rb').read())
            if i == 0:
                html_img_str = '<center><img src="data:image/png;base64,{}"></center>'
            else:
                html_img_str =  """
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
            html_result += html_show(encoded.decode('UTF-8'))
            i += 1

        html_result += """</html>
           """

        iframe = IFrame(html_result, width=380, height=410)

        return iframe
