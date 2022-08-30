from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
import Settings


font14 = QtGui.QFont('Times', 14)


def stylesheet_color():
    global stylesheet1
    global stylesheet2
    global stylesheet3
    global stylesheet4
    global stylesheet5
    global stylesheet6
    global stylesheet7
    global stylesheet8
    global stylesheet9

    if Settings.get_theme_color() == 'light':
        stylesheet1 = "border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0"
        stylesheet2 = "border: 0px; color: #000000; background-color: #F0F0F0"
        stylesheet3 = "QHeaderView::section{border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}"
        stylesheet4 = "QMenuBar {border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0}" \
                      "QMenuBar::item::selected {color: #000000; background-color: #C0C0C0}"

        stylesheet5 = "QProgressBar{border: 1px; border-color: #000000; border-style: solid; background-color: #FFFFFF; color: #000000} QProgressBar::chunk {background-color: #00FF7F; }"
        stylesheet6 = "QTableView{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;gridline-color: #A9A9A9;}"
        stylesheet7 = "QTabWidget::pane {border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: #000000;}" \
                      "QTabBar::tab {border: 1px; border-color: #A9A9A9; border-style: solid; padding: 5px; color: #000000; min-width: 12em;} " \
                      "QTabBar::tab:selected {border: 2px; border-color: #A9A9A9; border-style: solid; margin-top: -1px; background-color: #C0C0C0; color: #000000;}"
        stylesheet8 = "QPushButton{border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0}" \
                      "QPushButton::pressed{border: 2px; background-color: #C0C0C0; margin-top: -1px}"
        stylesheet9 = "QComboBox {border: 1px; border-color: #A9A9A9; border-style: solid; color: #000000; background-color: #F0F0F0;}" \
                      "QComboBox QAbstractItemView {selection-background-color: #C0C0C0;}"

    else:  # Settings.get_theme_color() == 'dark'
        stylesheet1 = "border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C"
        stylesheet2 = "border: 0px; color: #D3D3D3; background-color: #1C1C1C"
        stylesheet3 = "QHeaderView::section{border: 1px; border-color: #696969; border-style: solid; background-color: #1C1C1C; color: #D3D3D3;}"
        stylesheet4 = "QMenuBar {border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C}" \
                      "QMenuBar::item::selected {color: #D3D3D3; background-color: #3F3F3F}"

        stylesheet5 = "QProgressBar{border: 1px; border-color: #000000; border-style: solid; background-color: #CCCCCC; color: #000000} QProgressBar::chunk {background-color: #1F7515; }"
        stylesheet6 = "QTableView{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1c1c1c; gridline-color: #696969;}"
        stylesheet7 = "QTabWidget::pane {border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C;  color: #D3D3D3}" \
                      "QTabBar::tab {border: 1px; border-color: #696969; border-style: solid; padding: 5px; color: #D3D3D3; min-width: 12em;} " \
                      "QTabBar::tab:selected {border: 2px; border-color: #6A6A6A; border-style: solid; margin-top: -1px; background-color: #1F1F1F; color: #D3D3D3}"
        stylesheet8 = "QPushButton{border: 1px; border-color: #696969; border-style: solid; color: #D3D3D3; background-color: #1C1C1C}" \
                      "QPushButton::pressed{border: 2px; background-color: #2F2F2F; margin-top: -1px}"
        stylesheet9 = "QComboBox {border: 1px; border-color: #696969; border-style: solid; background-color: #1C1C1C; color: #D3D3D3;}" \
                      "QComboBox QAbstractItemView {selection-background-color: #4F4F4F;}"


# добавляемое в основной каталог фото уже есть (совпали имя и папка по дате)
class PhotoExists(QDialog):
    def __init__(self, parent, photo_list, type):
        super(PhotoExists, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Обнаружены совпадения')
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        self.answer = None

        self.lbl = QLabel(self)
        str_to_show = ''
        str_to_show += 'Данные файлы уже находились в основном каталоге:\n\n'
        for photo in photo_list:
            str_to_show += str(photo) + '\n'

        if type == "const":
            str_to_show += '\nЕсли вы хотите их перезаписать - удалите уже добавленные.\n\nУ данных файлов совпала дата ' \
                           'съёмки(при её наличии) и название.'
        else:   # type == "alone"
            str_to_show += '\nЕсли вы хотите их перезаписать - удалите уже добавленные.\n\nВ папке уже есть файлы с такими именами.'
        self.lbl.setText(str_to_show)
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ок')
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)

        self.resize(self.lbl.width()+20, self.lbl.height() + self.btn_ok.height() + 20)

        self.btn_ok.clicked.connect(lambda: self.close())


# при вводе метаданных в режиме редактирования введён недопустимый формат
class EditExifError_win(QDialog):
    def __init__(self, parent):
        super(EditExifError_win, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Ошибка ввода данных')
        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Недопустимый формат ввода')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


# при редактировании даты exif надо переносить файл в другую папку, там уже есть файл с таким
# именем, и пользователь не переименовал ни один из двух
class ExistFileRenameError1(QDialog):
    def __init__(self, parent):
        super(ExistFileRenameError1, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Файл не был переименован')

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Имена файлов всё ещё совпадают')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


class ExistFileRenameError2(QDialog):
    def __init__(self, parent):
        super(ExistFileRenameError2, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Файл с таким именем уже существует')

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Файл с таким именем уже существует')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


class ErNamesDBWarn(QDialog):
    def __init__(self, parent, code=0):
        super(ErNamesDBWarn, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.answer = None
        self.resize(100, 100)
        self.setWindowTitle('ОШИБКА')
        match code:
            case 1:
                text = "Не введено, некорректное наименование, подлежащее исправлению"
            case 2:
                text = "Не введено корректное именование"
            case 3:
                text = "Ошибка доступа к базе пользовательских поправок"

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText(text)
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


class ExistAloneDir(QDialog):
    def __init__(self, parent=None):
        super(ExistAloneDir, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Директория уже существует')

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Папка с таким именем уже есть в программе')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet2)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet8)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


# при любой ошибки в процессе modify_exif вызывается ошибка
class EditExifError(Exception):
    pass


class PhotoDBConnectionError(Exception):
    pass


class ErnamesDBConnectionError(Exception):
    pass
