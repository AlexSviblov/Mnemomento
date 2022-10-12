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
icon_explorer = str()
icon_view = str()
icon_edit = str()
icon_delete = str()


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


class ManyPhotoEdit(QWidget):

    def __init__(self):
        super().__init__()

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
        self.layout_outside.addWidget(self.groupbox_choose, 1, 0, 1, 2)
        self.make_move_buttons()

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

        self.layout_choose.addWidget(self.scroll_filtered_area, 0, 0, 6, 1)

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

        self.layout_choose.addWidget(self.scroll_edit_area, 0, 2, 6, 1)

        self.empty = QLabel()
        self.layout_outside.addWidget(self.empty, 1, 3, 1, 1)

        self.fill_sort_groupbox()
        self.fill_sort_date()

        self.show_filtered_thumbs()

    def make_move_buttons(self):
        self.btn_move_all_right = QPushButton(self)
        self.btn_move_all_right.setText(">>")
        self.btn_move_all_right.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_all_right, 1, 1, 1, 1)
        self.btn_move_all_right.clicked.connect(self.transfer_all_to_edit)

        self.btn_move_one_right = QPushButton(self)
        self.btn_move_one_right.setText(">")
        self.btn_move_one_right.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_one_right, 2, 1, 1, 1)
        self.btn_move_one_right.clicked.connect(self.transfer_one_to_edit)

        self.btn_move_one_left = QPushButton(self)
        self.btn_move_one_left.setText("<")
        self.btn_move_one_left.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_one_left, 3, 1, 1, 1)

        self.btn_move_all_left = QPushButton(self)
        self.btn_move_all_left.setText("<<")
        self.btn_move_all_left.setFixedSize(40, 20)
        self.layout_choose.addWidget(self.btn_move_all_left, 4, 1, 1, 1)
        self.btn_move_all_left.clicked.connect(self.transfer_all_to_filtered)

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
    def photo_to_thumb_path(self, photo_list):
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

    def show_filtered_thumbs(self):
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

    def transfer_all_to_edit(self):
        for i in range(self.filtered_photo_table.rowCount()):
            for j in range(self.filtered_photo_table.columnCount()):
                try:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
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

                    item.clicked.connect(self.transfer_one_to_filtered)
                except AttributeError:  # в последнем слоте может ничего не быть - всегда если количество фоток нечётное
                    pass

    def transfer_all_to_filtered(self):
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

        self.edit_photo_table.setRowCount(0)

    def transfer_one_to_edit(self):
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

        item.clicked.connect(self.transfer_one_to_filtered)

    def transfer_one_to_filtered(self):
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





if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManyPhotoEdit()
    win.show()
    sys.exit(app.exec_())