# coding: utf-8
import json
import logging
import math
import os
from pathlib import Path

import folium
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import *

from Database import PhotoDataDB
from Explorer import Thumbnail
from GUI import Screenconfig, EditFiles, ErrorsAndWarnings, Settings
from GUI.Screenconfig import font14, font12
from Metadata import MetadataPhoto

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


system_scale = Screenconfig.monitor_info()[1]


class ConstWidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.stylesheet_color()

        self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()

        self.thumb_row = Settings.get_thumbs_row()
        self.soc_net_setting = Settings.get_socnet_status()

        self.setMaximumSize(Screenconfig.monitor_info()[0][0], Screenconfig.monitor_info()[0][1] - 63)

        self.layoutoutside = QGridLayout(self)

        self.layout_type = QGridLayout(self)
        # создание объекта большой картинки
        self.pic = QtWidgets.QLabel()
        # создание внутреннего слоя для подвижной области
        self.layout_inside_thumbs = QGridLayout(self)
        # создание группы объектов для помещения в него кнопок
        self.groupbox_thumbs = QGroupBox(self)
        # создание подвижной области
        self.scroll_area = QScrollArea(self)

        self.groupbox_sort = QGroupBox(self)

        self.metadata_show = QtWidgets.QTableWidget()

        self.metadata_header = self.metadata_show.horizontalHeader()

        self.last_clicked = ""

        self.resized_signal.connect(self.resize_func)
        self.oldsize = QtCore.QSize(0, 0)

        self.layout_btns = QGridLayout(self)

        self.groupbox_btns = QGroupBox(self)

        self.socnet_group = QTableWidget(self)

        self.layout_show = QGridLayout(self)

        self.photo_show = QGroupBox(self)

        self.group_type = QComboBox(self)

        self.make_gui()

        self.fill_sort_comment("Дата")
        self.fill_sort_groupbox()
        self.fill_sort_date()

        self.make_buttons()

        self.photo_path = str()
        self.photo_directory = str()
        self.last_clicked_name = str()
        self.last_clicked_dir = str()
        self.photo_rotation = str()
        self.gps_coordinates = str()

    def stylesheet_color(self) -> None:
        """
        Задать стили для всего модуля в зависимости от выбранной темы
        """
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
        stylesheet1 = style[f"{theme}"]["stylesheet1"]
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        stylesheet3 = style[f"{theme}"]["stylesheet3"]
        stylesheet6 = style[f"{theme}"]["stylesheet6"]
        stylesheet7 = style[f"{theme}"]["stylesheet7"]
        stylesheet8 = style[f"{theme}"]["stylesheet8"]
        stylesheet9 = style[f"{theme}"]["stylesheet9"]
        icon_explorer = style[f"{theme}"]["icon_explorer"]
        icon_view = style[f"{theme}"]["icon_view"]
        icon_edit = style[f"{theme}"]["icon_edit"]
        icon_delete = style[f"{theme}"]["icon_delete"]

        try:
            self.groupbox_thumbs.setStyleSheet(stylesheet1)
            self.scroll_area.setStyleSheet(stylesheet2)
            self.groupbox_sort.setStyleSheet(stylesheet2)
            self.groupbox_btns.setStyleSheet(stylesheet2)
            if self.soc_net_setting:
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

    def make_gui(self) -> None:
        self.layoutoutside.setSpacing(10)

        self.layout_type.setAlignment(Qt.AlignLeft)

        self.pic.hide()
        self.pic.setAlignment(Qt.AlignCenter)

        self.groupbox_thumbs.setStyleSheet(stylesheet1)
        self.groupbox_thumbs.setLayout(self.layout_inside_thumbs)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.groupbox_thumbs)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(stylesheet2)

        # помещение подвижной области на слой
        self.layoutoutside.addWidget(self.scroll_area, 1, 0, 2, 2)
        # задание размеров подвижной области и её внутренностей
        self.groupbox_thumbs.setFixedWidth(195*self.thumb_row)
        self.scroll_area.setFixedWidth(200*self.thumb_row)

        self.groupbox_sort.setFixedHeight(int(60*system_scale)+1)
        self.groupbox_sort.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.groupbox_sort, 0, 1, 1, 3)

        self.groupbox_sort.setLayout(self.layout_type)

        self.layoutoutside.addWidget(self.groupbox_btns, 0, 4, 3, 1)

        self.metadata_show.setColumnCount(2)
        self.metadata_show.setFont(font14)
        self.metadata_show.setStyleSheet(stylesheet6)

        self.metadata_show.horizontalHeader().setVisible(False)
        self.metadata_show.verticalHeader().setVisible(False)

        self.metadata_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.metadata_show.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.metadata_show.setDisabled(True)
        self.metadata_show.hide()

        self.layout_btns.setSpacing(0)
        self.layout_btns.setAlignment(Qt.AlignRight)

        self.groupbox_btns.setLayout(self.layout_btns)
        self.groupbox_btns.setStyleSheet(stylesheet2)
        self.groupbox_btns.setFixedSize(120, 220)
        self.groupbox_btns.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.socnet_group.setColumnCount(2)
        self.socnet_group.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.socnet_group.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.socnet_group.horizontalHeader().setVisible(False)
        self.socnet_group.verticalHeader().setVisible(False)
        self.socnet_group.setSelectionMode(QAbstractItemView.NoSelection)
        self.socnet_group.setFocusPolicy(Qt.NoFocus)
        self.socnet_group.setStyleSheet(stylesheet6)
        self.socnet_group.hide()

        self.photo_show.setAlignment(Qt.AlignCenter)
        self.layout_show.setAlignment(Qt.AlignCenter)
        self.layout_show.setHorizontalSpacing(10)
        self.photo_show.setLayout(self.layout_show)
        self.photo_show.setStyleSheet(stylesheet2)
        self.layoutoutside.addWidget(self.photo_show, 1, 2, 2, 2)

    def fill_date(self, mode: str) -> None:
        """
        Заполнение полей сортировки по дате
        :param mode:
        """
        def get_years() -> None:
            """
            Получение годов
            """
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

        def get_months() -> None:
            """
            Получение месяцев в году
            """
            self.date_month.clear()
            year = self.date_year.currentText()
            if year == "All":
                self.date_month.addItem("All")
            else:
                dir_to_find_month = Settings.get_destination_media() + "/Media/Photo/const/" + year + "/"
                all_files_and_dirs = os.listdir(dir_to_find_month)
                dir_list = list()
                for name in all_files_and_dirs:
                    if os.path.isdir(dir_to_find_month + name):
                        if len(os.listdir(dir_to_find_month + name)) >= 1:
                            for file in Path(dir_to_find_month + name).rglob("*"):
                                if os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG"):
                                    dir_list.append(name)
                                    break

                dir_list.sort(reverse=True)
                for month in dir_list:
                    self.date_month.addItem(str(month))
                self.date_month.addItem("All")

        def get_days() -> None:
            """
            Получение дней в месяце
            """
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
            case "year":
                get_years()
            case "month":
                get_months()
            case "day":
                get_days()
            case _:
                get_years()

    def photo_to_thumb_path(self, photo_list: list[str]) -> list[str]:
        """
        Преобразовать пути фотографий из БД в пути миниатюр для отображения
        :param photo_list:
        :return:
        """
        thumb_names = list()
        thumbnails_list = list()
        for photo in photo_list:
            photo_splitted = photo.split("/")
            thumb_dir = Settings.get_destination_thumb() + \
                        f"/thumbnail/const/{photo_splitted[-4]}/{photo_splitted[-3]}/{photo_splitted[-2]}/"
            thumb_names.append(photo_splitted[-1])

            if os.path.exists(thumb_dir + "thumbnail_" + photo_splitted[-1]):
                thumbnails_list.append(thumb_dir + "thumbnail_" + photo_splitted[-1])
            else:
                photo_dir = ""
                for i in range(len(photo_splitted) - 1):
                    photo_dir += photo_splitted[i] + "/"
                Thumbnail.make_or_del_thumbnails([f"{photo_splitted[-1]}"], [], photo_dir[:-1],
                                                 thumb_dir[:-1])
                thumbnails_list.append(thumb_dir + "thumbnail_" + photo_splitted[-1])

        return thumbnails_list

    def type_show_thumbnails(self) -> None:
        """
        Выбор функции показа миниатюр в зависимости от выбранной группировки
        """
        match self.group_type.currentText():
            case "Дата":
                if not self.date_day.currentText() or not self.date_month.currentText() or not self.date_year.currentText():
                    return
            case "Оборудование":
                pass
            case "Соцсети":
                if not self.socnet_choose.currentText() or not self.sn_status.currentText():
                    return

        def clear_and_lock_show() -> None:
            try:
                self.pic.clear()
                self.pic.hide()
            except AttributeError:
                pass

            try:
                self.metadata_show.clear()
                self.metadata_show.hide()
            except AttributeError:
                pass

            try:
                self.socnet_group.clear()
                self.socnet_group.hide()
            except AttributeError:
                pass

            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass

            try:
                self.group_type.setDisabled(True)
            except AttributeError:
                pass

            try:
                for i in reversed(range(self.layout_type.count())):
                    self.layout_type.itemAt(i).widget().setDisabled(True)
            except (RuntimeError, AttributeError):
                pass

            try:
                for i in reversed(range(self.layout_btns.count())):
                    self.layout_btns.itemAt(i).widget().setDisabled(True)
            except (RuntimeError, AttributeError):
                pass
            # иначе если будет загружаться много фото, а пользователь до окончания их загрузки, сменит тип, то фото
            # начнут прогружаться в уже несуществующую scroll_area и крашнут программу
            try:
                for i in reversed(range(self.layout_inside_thumbs.count())):
                    self.layout_inside_thumbs.itemAt(i).widget().deleteLater()
            except (RuntimeError, AttributeError):
                pass

        def unlock_show() -> None:
            try:
                for i in reversed(range(self.layout_type.count())):
                    self.layout_type.itemAt(i).widget().setDisabled(False)
            except (RuntimeError, AttributeError):
                pass

            try:
                for i in reversed(range(self.layout_btns.count())):
                    self.layout_btns.itemAt(i).widget().setDisabled(False)
            except (RuntimeError, AttributeError):
                pass

            try:
                self.group_type.setDisabled(False)
            except AttributeError:
                pass

        clear_and_lock_show()
        QtCore.QCoreApplication.processEvents()

        if self.comment_check.checkState():
            search_comment = True
            comment_text = self.comment_line.text()
        else:
            search_comment = False
            comment_text = ""

        match self.group_type.currentText():
            case "Дата":
                year = self.date_year.currentText()
                month = self.date_month.currentText()
                day = self.date_day.currentText()

                if not year or not month or not day:
                    return
                else:
                    photo_list = PhotoDataDB.get_date_photo_list(year, month, day, search_comment, comment_text)
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

                photo_list = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens, search_comment, comment_text)
            case "Соцсети":
                network = self.socnet_choose.currentText()
                if network == "Нет данных":
                    unlock_show()
                    return
                else:
                    pass

                photo_list = PhotoDataDB.get_sn_photo_list(network, self.sn_status.currentText(), search_comment, comment_text)
            case _:
                raise ValueError

        if not photo_list:
            self.groupbox_thumbs.setMinimumHeight(self.height() - 100)
        else:
            thumbnails_list = self.photo_to_thumb_path(photo_list)
            self.fill_scroll_thumbs(thumbnails_list, photo_list)

        unlock_show()
        QtCore.QCoreApplication.processEvents()

    def fill_scroll_thumbs(self, thumbnails_list: list[str], photo_list: list[str]) -> None:
        """
        Функция отображения кнопок с миниатюрами
        :param thumbnails_list:
        :param photo_list:
        """
        num_of_j = math.ceil(len(thumbnails_list) / self.thumb_row)  # количество строк кнопок
        self.groupbox_thumbs.setMinimumHeight(200 * num_of_j)

        for j in range(0, num_of_j):  # создание кнопок
            if j == num_of_j - 1:  # последний ряд (может быть неполным)
                for i in range(0, len(thumbnails_list) - self.thumb_row * (num_of_j - 1)):
                    button = QtWidgets.QToolButton(self)  # создание кнопки
                    button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # задание, что картинка над текстом
                    iqon = QtGui.QIcon(f"{thumbnails_list[j * self.thumb_row + i]}")  # создание объекта картинки
                    iqon.pixmap(150, 150)  # задание размера картинки
                    button.setMinimumHeight(180)
                    button.setFixedWidth(160)
                    button.setIcon(iqon)  # помещение картинки на кнопку
                    button.setIconSize(QtCore.QSize(150, 150))
                    filename_show = thumbnails_list[j * self.thumb_row + i].split("/")[-1][10:]
                    button.setText(f"{filename_show}")  # добавление названия фото
                    button.setObjectName(f"{photo_list[j * self.thumb_row + i]}")
                    self.layout_inside_thumbs.addWidget(button, j, i, 1, 1)
                    button.setStyleSheet(stylesheet1)
                    button.clicked.connect(self.showinfo)
                    QtCore.QCoreApplication.processEvents()
            else:
                for i in range(0, self.thumb_row):
                    button = QtWidgets.QToolButton(self)
                    button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    iqon = QtGui.QIcon(f"{thumbnails_list[j * self.thumb_row + i]}")
                    iqon.pixmap(150, 150)
                    button.setMinimumHeight(180)
                    button.setFixedWidth(160)
                    button.setIcon(iqon)
                    button.setIconSize(QtCore.QSize(150, 150))
                    filename_show = thumbnails_list[j * self.thumb_row + i].split("/")[-1][10:]
                    button.setText(f"{filename_show}")  # добавление названия фото
                    button.setObjectName(f"{photo_list[j * self.thumb_row + i]}")
                    self.layout_inside_thumbs.addWidget(button, j, i, 1, 1)
                    button.setStyleSheet(stylesheet1)
                    button.clicked.connect(self.showinfo)
                    QtCore.QCoreApplication.processEvents()

    def make_map(self) -> None:
        """
        Создание и отрисовка карты с GPS-меткой
        """
        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass

        if self.gps_coordinates:
            self.map_gps_widget = QtWebEngineWidgets.QWebEngineView()
            gps_dict = self.gps_coordinates
            gps_coords = [float(gps_dict.split(",")[0]), float(gps_dict.split(",")[1])]

            map_gps = folium.Map(location=gps_coords, zoom_start=14)
            folium.Marker(gps_coords, popup=self.last_clicked_name, icon=folium.Icon(color="red")).add_to(map_gps)
            self.map_gps_widget.setHtml(map_gps.get_root().render())
            if self.photo_rotation == "gor":
                self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
                if self.soc_net_setting:
                    self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - self.socnet_group.width() - 40)
                    self.map_gps_widget.setFixedHeight(self.metadata_show.height())
                else:
                    self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - 40)
                    self.map_gps_widget.setFixedHeight(self.metadata_show.height())
            else: # self.photo_rotation == "ver"
                self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
                if self.soc_net_setting:
                    self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                    self.map_gps_widget.setFixedHeight(self.height() - self.groupbox_sort.height() - self.metadata_show.height() - self.socnet_group.height() - 100)
                else:
                    self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                    self.map_gps_widget.setFixedHeight(self.height() - self.groupbox_sort.height() - self.metadata_show.height() - 100)
            self.map_gps_widget.show()
        else:
            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass

    def showinfo(self) -> None:
        """
        Функция показа большой картинки
        """
        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 120)

        self.photo_path = self.sender().objectName()

        if not self.photo_path:
            if type(self.sender()) is EditFiles.EditExifData:
                self.photo_path = self.last_clicked
            else:
                return

        self.socnet_group.clear()

        self.last_clicked = self.photo_path  # полный путь

        self.metadata_show.clear()
        self.metadata_show.hide()

        self.pic.clear()  # очистка от того, что показано сейчас

        photo_directory_parts = self.photo_path.split("/")
        self.photo_directory = ""
        for i in range(0, len(photo_directory_parts) - 1):
            self.photo_directory += photo_directory_parts[i] + "/"

        self.last_clicked_name = photo_directory_parts[-1]
        self.last_clicked_dir = self.photo_directory[:-1]
        # C:\Users\user\PycharmProjects\TestForPhotoPr/Media/Photo/const/2022/01/18/

        photo_file = self.photo_path  # получение информации о нажатой кнопке

        jsondata_wr = {"last_opened_photo": photo_file}
        with open("last_opened.json", "w") as json_file:
            json.dump(jsondata_wr, json_file)

        self.pixmap = QtGui.QPixmap(photo_file)  # размещение большой картинки

        try:
            metadata = MetadataPhoto.fast_filter_exif(MetadataPhoto.fast_read_exif(photo_file), self.last_clicked_name,
                                                 self.photo_directory)
        except (UnicodeDecodeError, UnicodeEncodeError, ValueError):
            metadata = MetadataPhoto.filter_exif(MetadataPhoto.read_exif(photo_file), self.last_clicked_name,
                                            self.photo_directory)
        except FileNotFoundError:
            win_err = ErrorsAndWarnings.ExistFileError(self)
            win_err.show()
            self.type_show_thumbnails()
            return

        self.photo_rotation = metadata["Rotation"]

        try:
            self.gps_coordinates = metadata["GPS"]
        except KeyError:
            self.gps_coordinates = ""
        params = list(metadata.keys())
        params.remove("Rotation")

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
                self.metadata_show.setItem(r, 1, QTableWidgetItem(str(metadata[params[i]])))
                r += 1
                if len(str(metadata[params[i]])) > max_len:
                    max_len = len(str(metadata[params[i]]))

        self.metadata_show.setColumnWidth(1, max_len*12)

        if self.metadata_show.columnWidth(1) < 164:
            self.metadata_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
            self.metadata_show.setColumnWidth(1, 164)

        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0))

        if self.soc_net_setting:
            if self.photo_rotation == "gor":
                self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)

                self.metadata_show.show()

                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 200,
                                                  self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 1, 3)

                self.pic.show()
                self.layout_show.addWidget(self.socnet_group, 1, 2, 1, 1)

                self.socnet_group.show()
                self.show_social_networks(self.last_clicked_name, self.last_clicked_dir)

                if self.pixmap2.width() > self.metadata_show.width() + self.socnet_group.width():
                    self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 200)
                else:
                    self.set_minimum_size.emit(self.scroll_area.width() + self.metadata_show.width() + self.socnet_group.width() + self.groupbox_btns.width() + 200)

            else:  # self.photo_rotation == "ver"
                self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
                self.metadata_show.show()
                self.layout_show.addWidget(self.socnet_group, 2, 1, 1, 1)
                self.socnet_group.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 50, self.size().height() - self.groupbox_sort.height() - 30,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
                self.pic.show()
                self.show_social_networks(self.last_clicked_name, self.last_clicked_dir)

                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 60)
        else:
            if self.photo_rotation == "gor":
                self.layout_show.addWidget(self.metadata_show, 1, 0, 1, 1)
                self.metadata_show.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 200, self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)
                self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
                self.pic.show()

                if self.pixmap2.width() > self.metadata_show.width():
                    self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.groupbox_btns.width() + 160)
                else:
                    self.set_minimum_size.emit(self.scroll_area.width() + self.metadata_show.width() + self.groupbox_btns.width() + 160)
            else:  # self.photo_rotation == "ver"
                self.layout_show.addWidget(self.metadata_show, 0, 1, 1, 1)
                self.metadata_show.show()
                self.pixmap2 = self.pixmap.scaled(self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 50, self.size().height() - self.groupbox_sort.height() - 30,
                                        QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
                self.pic.setPixmap(self.pixmap2)

                self.layout_show.addWidget(self.pic, 0, 0, 2, 1)
                self.pic.show()
                self.set_minimum_size.emit(self.scroll_area.width() + self.pixmap2.width() + self.metadata_show.width() + self.groupbox_btns.width() + 160)

        self.pic.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        QtCore.QCoreApplication.processEvents()
        self.make_map()
        self.oldsize = self.size()

    def clear_after_del(self) -> None:
        """
        Убрать с экрана фото и метаданные после удаления фотографии
        """
        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.socnet_group.clear()
        self.socnet_group.hide()
        QtCore.QCoreApplication.processEvents()

        self.type_show_thumbnails()
        match self.group_type.currentText():
            case "Дата":
                old_year = self.date_year.currentText()
                old_month = self.date_month.currentText()
                old_day = self.date_day.currentText()
                self.fill_sort_date()
                self.date_year.setCurrentText(old_year)
                self.date_month.setCurrentText(old_month)
                self.date_day.setCurrentText(old_day)
            case "Соцсети":
                old_network = self.socnet_choose.currentText()
                old_status = self.sn_status.currentText()
                self.fill_sort_socnets()
                self.socnet_choose.setCurrentText(old_network)
                self.sn_status.setCurrentText(old_status)
            case "Оборудование":
                old_camera = self.camera_choose.currentText()
                old_lens = self.lens_choose.currentText()
                self.fill_sort_equipment()
                self.camera_choose.setCurrentText(old_camera)
                self.lens_choose.setCurrentText(old_lens)

    def resizeEvent(self, QResizeEvent) -> None:
        """
        Действия при изменении размеров окна
        :param QResizeEvent:
        """
        self.resized_signal.emit()

    def resize_func(self) -> None:
        """
        Изменение размера фото и карты
        """
        self.resize_photo()
        self.resize_map()

    def resize_photo(self) -> None:
        """
        Изменение размера фото
        """
        if not self.pic.isVisible():
            return

        if self.photo_rotation == "gor":
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.groupbox_btns.width() - self.scroll_area.width() - 40,
                self.size().height() - self.groupbox_sort.height() - self.metadata_show.height() - 40,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
        else:
            self.pixmap2 = self.pixmap.scaled(
                self.size().width() - self.metadata_show.width() - self.groupbox_btns.width() - self.scroll_area.width() - 80,
                self.size().height() - self.groupbox_sort.height() - 10,
                QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(self.pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)

        self.photo_show.setFixedWidth(self.width() - self.scroll_area.width() - self.groupbox_btns.width() - 120)

    def resize_map(self):
        """
        Изменить размер карты
        """
        try:
            if not self.map_gps_widget.isVisible():
                return
            else:
                pass
        except (RuntimeError, AttributeError):
            return

        if self.photo_rotation == "gor":
            self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
            if self.soc_net_setting:
                self.map_gps_widget.setFixedWidth(
                    self.pic.width() - self.metadata_show.width() - self.socnet_group.width() - 40)
                self.map_gps_widget.setFixedHeight(self.metadata_show.height())
            else:
                self.map_gps_widget.setFixedWidth(self.pic.width() - self.metadata_show.width() - 40)
                self.map_gps_widget.setFixedHeight(self.metadata_show.height())
        else:  # self.photo_rotation == "ver"
            self.layout_show.addWidget(self.map_gps_widget, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)
            if self.soc_net_setting:
                self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                self.map_gps_widget.setFixedHeight(
                    self.height() - self.groupbox_sort.height() - self.metadata_show.height() - self.socnet_group.height() - 100)
            else:
                self.map_gps_widget.setFixedWidth(self.metadata_show.width())
                self.map_gps_widget.setFixedHeight(
                    self.height() - self.groupbox_sort.height() - self.metadata_show.height() - 100)
        self.map_gps_widget.show()

    def make_buttons(self) -> None:
        """
        Создание кнопок удаления и редактирования
        """
        try:
            for i in reversed(range(self.layout_btns.count())):
                self.layout_btns.itemAt(i).widget().deleteLater()
        except (RuntimeError, AttributeError):
            pass

        edit_btn = QToolButton(self)
        edit_btn.setStyleSheet(stylesheet1)
        edit_btn.setIcon(QtGui.QIcon(icon_edit))
        edit_btn.setIconSize(QtCore.QSize(50, 50))
        edit_btn.setToolTip("Редактирование метаданных")
        edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(edit_btn, 0, 0, 1, 1)
        edit_btn.clicked.connect(self.edit_exif_func)

        del_btn = QToolButton(self)
        del_btn.setStyleSheet(stylesheet1)
        del_btn.setIcon(QtGui.QIcon(icon_delete))
        del_btn.setIconSize(QtCore.QSize(50, 50))
        del_btn.setToolTip("Удалить")
        del_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(del_btn, 1, 0, 1, 1)
        del_btn.clicked.connect(self.del_photo_func)

        explorer_btn = QToolButton(self)
        explorer_btn.setStyleSheet(stylesheet1)
        explorer_btn.setIcon(QtGui.QIcon(icon_explorer))
        explorer_btn.setIconSize(QtCore.QSize(50, 50))
        explorer_btn.setToolTip("Показать в проводнике")
        explorer_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(explorer_btn, 2, 0, 1, 1)
        explorer_btn.clicked.connect(self.call_explorer)

        open_file_btn = QToolButton(self)
        open_file_btn.setStyleSheet(stylesheet1)
        open_file_btn.setIcon(QtGui.QIcon(icon_view))
        open_file_btn.setIconSize(QtCore.QSize(50, 50))
        open_file_btn.setToolTip("Открыть")
        open_file_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(open_file_btn, 3, 0, 1, 1)
        open_file_btn.clicked.connect(self.open_file_func)

        hotkeys = Settings.get_hotkeys()

        edit_shortcut = QShortcut(QKeySequence(hotkeys["edit_metadata"]), self)
        edit_shortcut.activated.connect(self.edit_exif_func)

        del_shortcut = QShortcut(QKeySequence(hotkeys["delete_file"]), self)
        del_shortcut.activated.connect(self.del_photo_func)

        explorer_shortcut = QShortcut(QKeySequence(hotkeys["open_explorer"]), self)
        explorer_shortcut.activated.connect(self.call_explorer)

        open_shortcut = QShortcut(QKeySequence(hotkeys["open_file"]), self)
        open_shortcut.activated.connect(self.open_file_func)

    def open_file_func(self) -> None:
        """
        Открыть фотографию в приложении просмотра
        """
        if not self.pic.isVisible() or not self.last_clicked:
            return

        path = self.last_clicked
        os.startfile(path)

    def call_explorer(self) -> None:
        """
        Показать фото в проводнике
        """
        if not self.pic.isVisible() or not self.last_clicked:
            return

        open_path = self.last_clicked
        path = open_path.replace("/", "\\")
        exp_str = f'explorer /select,\"{path}\"'
        os.system(exp_str)

    def del_photo_func(self) -> None:
        """
        Удаление фото по нажатию кнопки
        """
        if not self.pic.isVisible() or not self.last_clicked:
            return

        dialog_del = DelPhotoConfirm(self.last_clicked_name, self.last_clicked_dir)
        dialog_del.clear_info.connect(self.clear_after_del)
        if dialog_del.exec():
            self.last_clicked = ""

    def edit_exif_func(self) -> None:
        """
        Редактирование exif
        """
        if not self.pic.isVisible() or not self.last_clicked:
            return

        if not os.path.exists(f"{self.last_clicked_dir}/{self.last_clicked_name}"):
            return

        match self.group_type.currentText():
            case "Дата":
                old_year = self.date_year.currentText()
                old_month = self.date_month.currentText()
                old_day = self.date_day.currentText()
            case "Соцсети":
                old_network = self.socnet_choose.currentText()
                old_status = self.sn_status.currentText()
            case "Оборудование":
                old_camera = self.camera_choose.currentText()
                old_lens = self.lens_choose.currentText()

        def re_show() -> None:
            if self.group_type.currentText() == "Дата":
                pass
            else:
                self.pic.clear()
                self.metadata_show.clear()
                self.metadata_show.hide()
                if self.group_type.currentText() == "Соцсети":
                    self.socnet_choose.setCurrentText(old_network)
                    self.sn_status.setCurrentText(old_status)
                    self.type_show_thumbnails()
                elif self.group_type.currentText() == "Оборудование":
                    self.fill_sort_equipment()
                    self.camera_choose.setCurrentText(old_camera)
                    self.lens_choose.setCurrentText(old_lens)
                    self.type_show_thumbnails()
            self.showinfo()

        def renamed_re_show(new_name: str) -> None:
            self.pic.clear()
            self.metadata_show.clear()
            self.metadata_show.hide()
            try:
                self.map_gps_widget.deleteLater()
            except (RuntimeError, AttributeError):
                pass
            try:
                self.socnet_group.hide()
            except (RuntimeError, AttributeError):
                pass

            if self.group_type.currentText() == "Соцсети":
                self.socnet_choose.setCurrentText(old_network)
                self.sn_status.setCurrentText(old_status)
                self.type_show_thumbnails()
            elif self.group_type.currentText() == "Оборудование":
                self.fill_sort_equipment()
                self.camera_choose.setCurrentText(old_camera)
                self.lens_choose.setCurrentText(old_lens)
                self.type_show_thumbnails()
            else:
                self.date_year.setCurrentText(old_year)
                self.date_month.setCurrentText(old_month)
                self.date_day.setCurrentText(old_day)
                self.type_show_thumbnails()

            last_splitted = self.last_clicked.split("/")
            button_text = ""
            for k in range(len(last_splitted) - 1):
                button_text += last_splitted[k] + "/"
            button_text += new_name

            for i in reversed(range(self.layout_inside_thumbs.count())):
                if self.layout_inside_thumbs.itemAt(i).widget().objectName() == button_text:
                    self.layout_inside_thumbs.itemAt(i).widget().click()
                    break

        dialog_edit = EditFiles.EditExifData(parent=self, photoname=self.last_clicked_name,
                                             photodirectory=self.last_clicked_dir,
                                             chosen_group_type=self.group_type.currentText())
        dialog_edit.show()

        if self.group_type.currentText() == "Дата":
            dialog_edit.movement_signal.connect(lambda y, m, d: self.get_date(y, m, d))

        if self.pic.isVisible():
            dialog_edit.edited_signal.connect(re_show)

        dialog_edit.edited_signal_no_move.connect(self.showinfo)
        dialog_edit.renamed_signal.connect(lambda n: renamed_re_show(n))
        dialog_edit.rotated_signal.connect(self.func_rotate_show)

    def get_date(self, year: str, month: str, day: str) -> None:
        """
        При редактировании метаданных могут создаваться новые папки (по датам), а фото будут переноситься -
        надо обновлять отображение
        :param year:
        :param month:
        :param day:
        :return:
        """
        self.socnet_group.clear()
        self.socnet_group.hide()
        self.group_type.setCurrentText("Дата")
        self.fill_date("date")
        self.pic.clear()
        self.pic.hide()
        self.metadata_show.clear()
        self.metadata_show.hide()
        self.type_show_thumbnails()
        self.date_year.setCurrentText(year)
        self.date_month.setCurrentText(month)
        self.date_day.setCurrentText(day)

        last_splitted = self.last_clicked.split("/")
        button_text = ""
        for k in range(len(last_splitted)-4):
            button_text += last_splitted[k] + "/"
        button_text += f"{year}/{month}/{day}/{last_splitted[-1]}"

        for i in reversed(range(self.layout_inside_thumbs.count())):
            if self.layout_inside_thumbs.itemAt(i).widget().objectName() == button_text:
                self.layout_inside_thumbs.itemAt(i).widget().click()
                break

    def show_social_networks(self, photoname: str, photodirectory: str) -> None:
        """
        Отображения статуса фото в соцсетях
        :param photoname:
        :param photodirectory:
        :return:
        """
        def fill_sn_widgets(sn_names: list[str], sn_tags: dict) -> None:
            i = 0
            self.socnet_group.setRowCount(len(sn_names))
            if not sn_names:
                self.socnet_group.setStyleSheet(stylesheet2)
                self.socnet_group.setFixedSize(0, 0)
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

                if name[:9] != "numnumnum":
                    self.sn_lbl.setText(f"{name}")
                else:
                    self.sn_lbl.setText(f"{name[9:]}")

                self.sn_lbl.setFixedWidth(int((len(name)*12)*system_scale)+1)
                self.socnet_group.setCellWidget(i, 0, self.sn_lbl)

                self.sn_tag_choose = QComboBox(self)
                self.sn_tag_choose.setFont(font14)
                self.sn_tag_choose.setStyleSheet(stylesheet9)
                self.sn_tag_choose.setObjectName(name)
                self.sn_tag_choose.addItem("Не выбрано")
                self.sn_tag_choose.addItem("Не публиковать")
                self.sn_tag_choose.addItem("Опубликовать")
                self.sn_tag_choose.addItem("Опубликовано")

                match sn_tags[f"{name}"]:
                    case "No value":
                        self.sn_tag_choose.setCurrentText("Не выбрано")
                    case "No publicate":
                        self.sn_tag_choose.setCurrentText("Не публиковать")
                    case "Will publicate":
                        self.sn_tag_choose.setCurrentText("Опубликовать")
                    case "Publicated":
                        self.sn_tag_choose.setCurrentText("Опубликовано")

                self.sn_tag_choose.currentTextChanged.connect(edit_tags)
                self.sn_tag_choose.currentTextChanged.connect(refresh_thumbs)

                self.socnet_group.setCellWidget(i, 1, self.sn_tag_choose)
                i += 1

                if self.sn_lbl.width() > self.metadata_show.columnWidth(0):
                    self.metadata_show.setColumnWidth(0, self.sn_lbl.width())

            if not sn_names:
                self.socnet_group.setStyleSheet(stylesheet2)
            else:
                self.socnet_group.setStyleSheet(stylesheet6)

            self.socnet_group_header = self.socnet_group.horizontalHeader()

            if self.photo_rotation == "gor":
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

            self.socnet_group.setFixedWidth(self.socnet_group.columnWidth(0) + self.socnet_group.columnWidth(1)+2)
            self.socnet_group.setFixedHeight(self.socnet_group.rowCount() * self.socnet_group.rowHeight(0) + 2)

        def edit_tags() -> None:
            match self.sender().currentText():
                case "Не выбрано":
                    new_status_bd = "No value"
                case "Не публиковать":
                    new_status_bd = "No publicate"
                case "Опубликовать":
                    new_status_bd = "Will publicate"
                case "Опубликовано":
                    new_status_bd = "Publicated"
                case _:
                    raise ValueError

            network = self.sender().objectName()
            PhotoDataDB.edit_sn_tags(photoname, photodirectory, new_status_bd, network)

        def refresh_thumbs() -> None:
            if self.group_type.currentText() == "Соцсети":
                if self.socnet_choose.currentText() == self.sender().objectName() or self.socnet_choose.currentText() == self.sender().objectName()[
                                                                                                                         9:]:
                    self.type_show_thumbnails()
                else:
                    pass
            else:
                pass

        fill_sn_widgets(PhotoDataDB.get_social_tags(photoname, photodirectory))

    def fill_sort_groupbox(self) -> None:
        """
        Выбор способа группировки
        """
        self.group_type.addItem("Дата")
        if self.soc_net_setting:
            self.group_type.addItem("Соцсети")
        self.group_type.addItem("Оборудование")
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(int(152*system_scale)+1)
        self.group_type.setFixedHeight(int(30*system_scale)+1)
        self.group_type.setStyleSheet(stylesheet9)

        self.layoutoutside.addWidget(self.group_type, 0, 0, 1, 1)

    def fill_sort_comment(self, group_type: str) -> None:
        """

        :param group_type:
        """
        def comment_line_block():
            if self.comment_check.checkState():
                self.comment_line.setDisabled(False)
            else:
                self.comment_line.clear()
                self.comment_line.setDisabled(True)
                self.type_show_thumbnails()

        self.empty_sort = QLabel(self)
        self.empty_sort.setFixedHeight(int(30 * system_scale) + 1)
        self.empty_sort.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.comment_check = QCheckBox(self)
        self.comment_check.setFont(font14)
        self.comment_check.setStyleSheet(stylesheet2)
        self.comment_check.setFixedHeight(int(30 * system_scale) + 1)

        self.comment_check.stateChanged.connect(comment_line_block)

        self.comment_line = QLineEdit(self)
        self.comment_line.setFont(font14)
        self.comment_line.setStyleSheet(stylesheet1)
        self.comment_line.setFixedHeight(int(30*system_scale)+1)
        self.comment_line.setFixedWidth(int(150*system_scale)+1)
        self.comment_line.setDisabled(True)
        self.comment_line.editingFinished.connect(self.type_show_thumbnails)

        if group_type == "Дата":
            self.layout_type.addWidget(self.empty_sort, 0, 7, 1, 1)
            self.layout_type.addWidget(self.comment_check, 0, 8, 1, 1, alignment=Qt.AlignRight)
            self.layout_type.addWidget(self.comment_line, 0, 9, 1, 1, alignment=Qt.AlignRight)
        else:
            self.layout_type.addWidget(self.empty_sort, 0, 3, 1, 1)
            self.layout_type.addWidget(self.comment_check, 0, 4, 1, 1, alignment=Qt.AlignRight)
            self.layout_type.addWidget(self.comment_line, 0, 5, 1, 1, alignment=Qt.AlignRight)

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
        self.date_day.currentTextChanged.connect(self.type_show_thumbnails)

        self.fill_date("date")

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

            self.socnet_choose.setFixedWidth(int((socnet_max_len*12+30)*system_scale)+1)

            self.socnet_choose.currentTextChanged.connect(self.type_show_thumbnails)

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

            self.sn_status.currentTextChanged.connect(self.type_show_thumbnails)
            self.type_show_thumbnails()

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

        self.camera_choose.setFixedWidth(int((camera_max_len*12)*system_scale)+1)
        self.lens_choose.setFixedWidth(int((lens_max_len*12)*system_scale)+1)

        self.camera_choose.currentTextChanged.connect(self.type_show_thumbnails)
        self.lens_choose.currentTextChanged.connect(self.type_show_thumbnails)

        self.type_show_thumbnails()

    def set_sort_layout(self) -> None:
        """
        Заполнить нужное поле в зависимости от выбранного типа группировки
        """
        for i in reversed(range(self.layout_type.count())):
            self.layout_type.itemAt(i).widget().hide()
            self.layout_type.itemAt(i).widget().deleteLater()
            QtCore.QCoreApplication.processEvents()

        try:
            self.map_gps_widget.deleteLater()
        except (RuntimeError, AttributeError):
            pass
        QtCore.QCoreApplication.processEvents()

        match self.group_type.currentText():
            case "Дата":
                self.fill_sort_date()
                self.fill_sort_comment("Дата")
            case "Соцсети":
                self.fill_sort_socnets()
                self.fill_sort_comment("Соцсети")
            case "Оборудование":
                self.fill_sort_equipment()
                self.fill_sort_comment("Оборудование")

        self.make_buttons()

    def after_change_settings(self) -> None:
        """
        Обновить дизайн при изменении настроек
        """
        self.thumb_row = Settings.get_thumbs_row()

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll_area.setFixedWidth(200 * self.thumb_row)

        self.type_show_thumbnails()

    def func_rotate_show(self) -> None:
        """
        Фото повернули, переназначить иконку на повёрнутую
        """
        destination_thumbs = Settings.get_destination_thumb()
        photo_way_splitted = self.last_clicked.split("/")
        year = photo_way_splitted[-4]
        month = photo_way_splitted[-3]
        day = photo_way_splitted[-2]
        name = photo_way_splitted[-1]

        thumbnail_way = f"{destination_thumbs}/thumbnail/const/{year}/{month}/{day}/thumbnail_{name}"
        iqon = QtGui.QIcon(thumbnail_way)
        iqon.pixmap(150, 150)

        for i in reversed(range(self.layout_inside_thumbs.count())):
            if self.layout_inside_thumbs.itemAt(i).widget().objectName() == self.last_clicked:
                self.layout_inside_thumbs.itemAt(i).widget().setIcon(iqon)
                break

        QtCore.QCoreApplication.processEvents()

        self.showinfo()

        QtCore.QCoreApplication.processEvents()


class DelPhotoConfirm(QDialog):
    """
    Подтвердить удаление фото
    """
    clear_info = QtCore.pyqtSignal()

    def __init__(self, photoname: str, photodirectory: str):
        super(DelPhotoConfirm, self).__init__()
        self.photoname = photoname
        self.photodirectory = photodirectory

        self.setStyleSheet(stylesheet2)

        self.setWindowTitle("Подтверждение удаления")
        self.resize(400, 100)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.lbl = QLabel()
        self.lbl.setText(f"Вы точно хотите удалить {self.photoname}?")
        self.lbl.setFont(font12)
        self.lbl.setStyleSheet(stylesheet2)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl, 0, 0, 1, 2)

        btn_ok = QPushButton(self)
        btn_ok.setText("Подтверждение")
        btn_ok.setFont(font12)
        btn_ok.setStyleSheet(stylesheet8)
        btn_cancel = QPushButton(self)
        btn_cancel.setText("Отмена")
        btn_cancel.setFont(font12)
        btn_cancel.setStyleSheet(stylesheet8)

        self.layout.addWidget(btn_ok, 1, 0, 1, 1)
        self.layout.addWidget(btn_cancel, 1, 1, 1, 1)

        btn_ok.clicked.connect(lambda: self.do_del(photoname, photodirectory))
        btn_cancel.clicked.connect(self.reject)

    def do_del(self, photoname: str, photodirectory: str) -> None:
        """
        При подтверждении - удалить фото, его миниатюру и записи в БД
        :param photoname:
        :param photodirectory:
        :return:
        """
        logging.info(f"Removing file {photodirectory + '/' + photoname}")
        os.remove(photodirectory + "/" + photoname)
        Thumbnail.delete_thumbnail_const(photoname, photodirectory)
        PhotoDataDB.del_from_database(photoname, photodirectory)
        self.clear_info.emit()
        self.accept()
