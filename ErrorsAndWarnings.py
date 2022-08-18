from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *


font14 = QtGui.QFont('Times', 14)

stylesheet1 = "border: 0px; background-color: #F0F0F0; color: black"
stylesheet2 = "border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #F0F0F0; color: black"
stylesheet4 = "border: 1px; border-color: #A9A9A9; border-style: solid; background-color: #FFFFFF; color: black;"


# добавляемое в основной каталог фото уже есть (совпали имя и папка по дате)
class PhotoExists(QDialog):
    def __init__(self, parent, photo_list):
        super(PhotoExists, self).__init__(parent)

        self.setWindowTitle('Обнаружены совпадения')

        self.answer = None
        self.resize(1000, 500)

        self.lbl = QLabel(self)
        str_to_show = ''
        str_to_show += 'Данные файлы уже находились в основном каталоге:\n\n'
        for photo in photo_list:
            str_to_show += str(photo) + '\n'

        str_to_show += '\nЕсли вы хотите их перезаписать - удалите уже добавленные.\n\nУ данных файлов совпала дата ' \
                       'съёмки(при её наличии) и название.'
        self.lbl.setText(str_to_show)
        self.lbl.setFont(QtGui.QFont('Times', 14))
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('ok')
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)

        self.btn_ok.clicked.connect(lambda: self.close())


# при вводе метаданных в режиме редактирования введён недопустимый формат
class EditExifError(QDialog):
    def __init__(self, parent):
        super(EditExifError, self).__init__(parent)
        self.setWindowTitle('Ошибка ввода данных')
        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Недопустимый формат ввода')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet1)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet2)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


# при редактировании даты exif надо переносить файл в другую папку, там уже есть файл с таким
# именем, и пользователь не переименовал ни один из двух
class ExistFileRenameError1(QDialog):
    def __init__(self, parent):
        super(ExistFileRenameError1, self).__init__(parent)
        self.setWindowTitle('Файл не был переименован')

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Имена файлов всё ещё совпадают')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet1)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet2)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


class ExistFileRenameError2(QDialog):
    def __init__(self, parent):
        super(ExistFileRenameError2, self).__init__(parent)
        self.setWindowTitle('Файл с таким именем уже существует')

        layout = QGridLayout(self)
        self.setLayout(layout)
        lbl = QLabel(self)
        lbl.setText('Файл с таким именем уже существует')
        lbl.setFont(font14)
        lbl.setStyleSheet(stylesheet1)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet2)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)


class ErNamesDBWarn(QDialog):
    def __init__(self, parent, code=0):
        super(ErNamesDBWarn, self).__init__(parent)
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
        lbl.setStyleSheet(stylesheet1)

        btn = QPushButton(self)
        btn.setText('Ок')
        btn.setFont(font14)
        btn.setStyleSheet(stylesheet2)
        btn.clicked.connect(lambda: self.close())

        layout.addWidget(lbl, 0, 0, 1, 1)
        layout.addWidget(btn, 1, 0, 1, 1)
