import sys, os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from math import ceil
from PyQt5.QtCore import Qt
import pyexiv2
from PIL import Image
import Screenconfig
import Metadata
import Settings
import Thumbnail
import ErrorsAndWarnings
import json


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


class WidgetWindow(QWidget):
    resized_signal = QtCore.pyqtSignal()
    set_minimum_size = QtCore.pyqtSignal(int)

    def __init__(self, photo_list: list[str, ...]):
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

        self.scroll = QScrollArea(self)  # создание подвижной области
        self.layoutoutside.addWidget(self.scroll, 0, 0, 2, 1)  # помещение подвижной области на слой
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

        self.make_edit_btn()

        self.groupbox_btns = QGroupBox(self)
        self.groupbox_btns.setLayout(self.layout_btns)
        self.groupbox_btns.setStyleSheet(stylesheet2)
        self.groupbox_btns.setFixedSize(70, 220)
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
            self.groupbox_btns.setStyleSheet(stylesheet2)
            self.photo_show.setStyleSheet(stylesheet2)
            self.metadata_show.setStyleSheet(stylesheet6)
            self.edit_btn.setStyleSheet(stylesheet1)
            self.setStyleSheet(stylesheet2)
            self.show_thumbnails()
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
            self.button_text = self.sender().text()
        except AttributeError:
            if self.last_clicked == '':
                return
            else:
                self.button_text = self.last_clicked

        self.last_clicked = self.button_text

        self.pic.clear()  # очистка от того, что показано сейчас

        self.photo_file = self.photo_directory + self.button_text  # получение информации о нажатой кнопке


        pixmap = QtGui.QPixmap(self.photo_file)  # размещение большой картинки

        metadata = Metadata.filter_exif(Metadata.read_exif(self.button_text, self.photo_directory, self.own_dir),
                                             self.button_text, self.photo_directory)

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


        self.metadata_show.setFixedWidth(self.metadata_show.columnWidth(0) + self.metadata_show.columnWidth(1))

        self.metadata_show.setFixedHeight(self.metadata_show.rowCount() * self.metadata_show.rowHeight(0) + 1)


        if self.photo_rotation == 'gor':
            self.layout_show.addWidget(self.metadata_show, 1, 1, 1, 1)
            self.metadata_show.show()

            pixmap2 = pixmap.scaled(self.size().width() - self.scroll.width() - self.groupbox_btns.width(),
                                    self.size().height() - self.metadata_show.height(),
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 1, 3)
            self.pic.show()
        else: # self.photo_rotation == 'ver'
            self.layout_show.addWidget(self.metadata_show, 1, 1, 1, 1)
            self.metadata_show.show()
            pixmap2 = pixmap.scaled(self.size().width() - - self.scroll.width() - self.groupbox_btns.width() -
                                    self.metadata_show.width(), self.size().height() - 50,
                                    QtCore.Qt.KeepAspectRatio)  # масштабируем большое фото под размер окна
            self.pic.setPixmap(pixmap2)
            self.layout_show.addWidget(self.pic, 0, 0, 3, 1)
            self.pic.show()

        self.set_minimum_size.emit(self.scroll.width() + self.metadata_show.width() + self.groupbox_btns.width() + 120)
        self.oldsize = self.size()

    # в класс передаётся список файлов, надо получить их директорию
    def make_photo_dir(self, photo_list: list[str, ...]) -> str:
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
    def make_edit_btn(self) -> None:
        self.edit_btn = QToolButton(self)
        # self.edit_btn.setIcon()
        self.edit_btn.setText('RED')
        self.edit_btn.setStyleSheet(stylesheet1)
        self.edit_btn.setFixedSize(50, 50)
        self.layout_btns.addWidget(self.edit_btn, 0, 0, 1, 1)
        self.edit_btn.clicked.connect(self.edit_photo_func)

    # функция редактирования
    def edit_photo_func(self) -> None:
        if not self.pic.isVisible() or not self.last_clicked:
            return

        photoname = self.button_text
        photodirectory = self.photo_directory[:-1]
        dialog_edit = EditExifData(parent=self, photoname=photoname, photodirectory=photodirectory)
        dialog_edit.show()
        dialog_edit.edited_signal.connect(self.showinfo)

    def after_change_settings(self):
        with open('settings.json', 'r') as json_file:
            settings = json.load(json_file)
        self.thumb_row = int(settings["thumbs_row"])

        self.groupbox_thumbs.setFixedWidth(195 * self.thumb_row)
        self.scroll.setFixedWidth(200 * self.thumb_row)

        self.show_thumbnails()


# редактирование exif
class EditExifData(QDialog):

    edited_signal = QtCore.pyqtSignal()

    def __init__(self, parent, photoname, photodirectory):
        super().__init__(parent)
        self.setWindowTitle('Редактирование метаданных')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.photoname = photoname
        self.photodirectory = photodirectory

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.layout.addWidget(self.table, 0, 0, 1, 1)

        self.indicator = 0
        self.get_metadata(photoname, photodirectory)

        self.table.itemDoubleClicked.connect(self.pre_edit)
        self.table.itemChanged.connect(lambda: self.write_changes(photoname, photodirectory))

    # редактировать только после двойного нажатия (иначе обновление данных вызовет вечную рекурсию)
    def pre_edit(self):
        self.indicator = 1

    # считать и отобразить актуальные метаданные
    def get_metadata(self, photoname, photodirectory):

        own_dir = os.getcwd()
        data = Metadata.exif_show_edit(photoname, photodirectory, own_dir)

        self.table.setColumnCount(2)
        self.table.setRowCount(len(data))
        keys = list(data.keys())
        self.table.setFont(QtGui.QFont('Times', 10))

        for parameter in range(len(data)):
            self.table.setItem(parameter, 0, QTableWidgetItem(keys[parameter]))
            self.table.item(parameter, 0).setFlags(Qt.ItemIsEditable)
            self.table.setItem(parameter, 1, QTableWidgetItem(data[keys[parameter]]))

        self.table.setStyleSheet('color: black')
        self.table.resizeColumnsToContents()
        self.resize(self.table.columnWidth(0) + self.table.columnWidth(1) + 80, 500)

    # записать новые метаданные
    def write_changes(self, photoname: str, photodirectory: str) -> None:
        # Перезаписать в exif и БД новые метаданные
        def rewriting(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_rewrite_edit(photoname, photodirectory, editing_type, new_text, own_dir)

        # проверка введённых пользователем метаданных
        def check_enter(photoname: str, photodirectory: str, editing_type: int, new_text: str, own_dir: str) -> None:
            Metadata.exif_check_edit(photoname, photodirectory, editing_type, new_text, own_dir)

        # Если изменение метаданных в таблице - дело рук программы, а не пользователя (не было предшествующего двойного нажатия)
        if self.indicator == 0:
            pass
        else:
            own_dir = os.getcwd()
            editing_type = self.table.currentRow()
            new_text = self.table.currentItem().text()

            # проверка введённых пользователем метаданных
            try:
                check_enter(photoname, photodirectory, editing_type, new_text, own_dir)
            except Metadata.EditExifError:
                win_err = ErrorsAndWarnings.EditExifError(self)
                win_err.show()
                # self.get_metadata(photoname, photodirectory)
                return

            rewriting(photoname, photodirectory, editing_type, new_text, own_dir)
            self.edited_signal.emit()

            # Если меняется дата -> проверка на перенос файла в новую папку
            self.indicator = 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WidgetWindow()
    form.show()
    app.exec_()
