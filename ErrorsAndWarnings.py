from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *


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
class EditExifError(QMessageBox):
    def __init__(self, parent):
        super(EditExifError, self).__init__(parent)
        self.setWindowTitle('Ошибка ввода данных')
        self.setText('Недопустимый формат ввода')
        self.setDefaultButton(QMessageBox.Ok)


# при редактировании даты exif надо переносить файл в другую папку, там уже есть файл с таким
# именем, и пользователь не переименовал ни один из двух
class ExistFileRenameError1(QMessageBox):
    def __init__(self, parent):
        super(ExistFileRenameError1, self).__init__(parent)
        self.setWindowTitle('Файл не был переименован')
        self.setText('Имена файлов всё ещё совпадают')
        self.setDefaultButton(QMessageBox.Ok)


class ExistFileRenameError2(QMessageBox):
    def __init__(self, parent):
        super(ExistFileRenameError2, self).__init__(parent)
        self.setWindowTitle('Файл с таким именем уже существует')
        self.setText('Файл с таким именем уже существует')
        self.setDefaultButton(QMessageBox.Ok)


class ErNamesDBWarn(QMessageBox):
    def __init__(self, code=0):
        super(ErNamesDBWarn, self).__init__()
        self.answer = None
        self.resize(100, 100)

        match code:
            case 1:
                self.setWindowTitle('ОШИБКА')
                self.setText("Не введено, некорректное наименование, подлежащее исправлению")
            case 2:
                self.setWindowTitle('ОШИБКА')
                self.setText("Не введено корректное именование")
            case 3:
                self.setWindowTitle('ОШИБКА')
                self.setText("Ошибка доступа к базе пользовательских поправок")

        self.setDefaultButton(QMessageBox.Ok)
