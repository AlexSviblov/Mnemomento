# coding: utf-8
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from GUI import Screenconfig, Settings

stylesheet2 = str()
stylesheet8 = str()


font14 = Screenconfig.font14


def stylesheet_color():
    global stylesheet2
    global stylesheet8

    theme = Settings.get_theme_color()
    style = Screenconfig.style_dict
    stylesheet2 = style[f"{theme}"]["stylesheet2"]
    stylesheet8 = style[f"{theme}"]["stylesheet8"]


class PhotoExists(QDialog):
    """
    Добавляемое в основной каталог фото уже есть (совпали имя и папка по дате)
    """
    def __init__(self, parent, photo_list: list[str], catalog_type: str):
        super(PhotoExists, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Обнаружены совпадения")
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        self.answer = None

        self.lbl = QLabel(self)
        str_to_show = ""
        str_to_show += "Данные файлы уже находились в основном каталоге:\n\n"
        for photo in photo_list:
            str_to_show += str(photo) + "\n"

        if catalog_type == "const":
            str_to_show += "\nЕсли вы хотите их перезаписать - удалите уже добавленные.\n\nУ данных файлов совпала дата " \
                           "съёмки(при её наличии) и название."
        else:   # type == "alone"
            str_to_show += "\nЕсли вы хотите их перезаписать - удалите уже добавленные.\n\nВ папке уже есть файлы с такими именами."
        self.lbl.setText(str_to_show)
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText("Ок")
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)

        self.resize(self.lbl.width()+20, self.lbl.height() + self.btn_ok.height() + 20)

        self.btn_ok.clicked.connect(self.close)


class EditExifErrorWin(QDialog):
    """
    При вводе метаданных в режиме редактирования введён недопустимый формат
    """
    def __init__(self, parent):
        super(EditExifErrorWin, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Ошибка ввода данных")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Ошибка ввода метаданных")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class ExistFileRenameError1(QDialog):
    """
    При редактировании даты exif надо переносить файл в другую папку, там уже есть файл с таким
    именем, и пользователь не переименовал ни один из двух
    """
    def __init__(self, parent):
        super(ExistFileRenameError1, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Файл не был переименован")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Имена файлов всё ещё совпадают")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class ExistFileRenameError2(QDialog):
    """

    """
    def __init__(self, parent):
        super(ExistFileRenameError2, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Файл с таким именем уже существует")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Файл с таким именем уже существует")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class ErNamesDBWarn(QDialog):
    """

    """
    def __init__(self, parent, code: int = 0):
        super(ErNamesDBWarn, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.answer = None
        self.resize(100, 100)
        self.setWindowTitle("ОШИБКА")
        match code:
            case 1:
                self.text = "Не введено, некорректное наименование, подлежащее исправлению"
            case 2:
                self.text = "Не введено корректное именование"
            case 3:
                self.text = "Ошибка доступа к базе пользовательских поправок"
            case _:
                self.text = ""

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText(self.text)
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class ExistAloneDir(QDialog):
    """

    """
    def __init__(self, parent=None):
        super(ExistAloneDir, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Директория уже существует")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Папка с таким именем уже есть в программе")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class ErNamesDBErrorWin(QDialog):
    """

    """
    def __init__(self, parent=None):
        super(ErNamesDBErrorWin, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("ОШИБКА")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)

        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Ошибка доступа к базе данных ErrorNames.db")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class RenameTransferingPhoto(QDialog):
    """

    """
    def __init__(self, parent=None):
        super(RenameTransferingPhoto, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Предупреждение")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("При смене даты съёмки фотографии основного каталога, она переносится.\n"
                    "Переносимые фотографии не переименовываются (возможно, когда-то появится такая функция).\n"
                    "Если вам всё ещё необходимо переименовать файл - сделайте это заново.")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class SettingsReadError(QDialog):
    """

    """
    def __init__(self, parent=None):
        super(SettingsReadError, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("ОШИБКА")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Не удалось считать файл с настройками.")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class FilesReadErrorWin(QDialog):
    """

    """
    def __init__(self, parent, files: list[str]):
        super(FilesReadErrorWin, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("ОШИБКА доступа к файлам")

        self.str_show = "Данные файлы не удалось перенести, возможно они открыты в другой программе или повреждены:"
        for file in files:
            self.str_show += f"\n{file}"
        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText(self.str_show)
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class EditCommentErrorWin(QDialog):
    """
    При вводе метаданных в режиме редактирования введён недопустимый формат
    """
    def __init__(self, parent, symbol: str):
        super(EditCommentErrorWin, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Комментарий плохого формата")
        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.str_show = f"К сожалению, комментарии к JPEG могут содержать только английские буквы,\n" \
                        f"цифры и специальные символы.\n" \
                        f"Недопустимый символ - {symbol}"
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self):
        self.setLayout(self.layout)

        self.lbl.setText(self.str_show)
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)


class EditCommentError(Exception):
    """

    """
    def __init__(self, symbol: str):
        self.symbol = symbol


class EditExifError(Exception):
    """
    При любой ошибки в процессе modify_exif вызывается ошибка
    """
    pass


class PhotoDBConnectionError(Exception):
    """

    """
    pass


class ErnamesDBConnectionError(Exception):
    """

    """
    pass


class FileReadError(Exception):
    """

    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print(f"FileReadError")
        if self.message:
            return f"FileReadError - {self.message}"
        else:
            return "FileReadError"


class ExistFileError(QDialog):
    """

    """
    def __init__(self, parent):
        super(ExistFileError, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Файл не найден")

        self.layout = QGridLayout(self)
        self.lbl = QLabel(self)
        self.btn = QPushButton(self)
        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)

        self.lbl.setText("Файл не найден")
        self.lbl.setFont(font14)
        self.lbl.setStyleSheet(stylesheet2)

        self.btn.setText("Ок")
        self.btn.setFont(font14)
        self.btn.setStyleSheet(stylesheet8)
        self.btn.clicked.connect(self.close)

        self.layout.addWidget(self.lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.btn, 1, 0, 1, 1)
