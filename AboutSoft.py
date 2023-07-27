from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
import sys

import Screenconfig
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()


font10 = QtGui.QFont("Times", 10)
font14 = QtGui.QFont("Times", 14)


def stylesheet_color():
    global stylesheet1
    global stylesheet2
    global stylesheet8

    theme = Settings.get_theme_color()
    style = Screenconfig.style_dict
    stylesheet1 = style[f"{theme}"]["stylesheet1"]
    stylesheet2 = style[f"{theme}"]["stylesheet2"]
    stylesheet8 = style[f"{theme}"]["stylesheet8"]


class AboutInfo(QDialog):
    """
    Добавляемое в основной каталог фото уже есть (совпали имя и папка по дате)
    """
    def __init__(self, parent):
        super(AboutInfo, self).__init__(parent)
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("О программе")
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)

        self.answer = None

        self.lbl = QLabel(self)

        self.btn_ok = QPushButton(self)

        self.make_gui()

    def make_gui(self) -> None:
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        str_to_show = """
                                    <p style="text-align:center">О программе</p>

                                    <p style="text-align:center">&quot;<strong>Мнемоменто</strong>&quot;</p>

                                    <p>Программа создана для удобного архивирования большого количества фотографий.</p>

                                    <p>В программе можно группировать фотографии по датам создания, используемому оборудованию и вести учёт публикаций в социальных сетях, просматривать и редактировать метаданные снимков.<br />
                                    <br />
                                    При разработке программы использовались следующие библиотеки, фреймворки и сторонние приложения:</p>

                                    <ul>
                                        <li><a href="https://www.riverbankcomputing.com/software/pyqt/">PyQt5</a></li>
                                        <li><a href="https://exiftool.org/">exiftool </a>by Phil Harvey</li>
                                        <li><a href="http://python-visualization.github.io/folium/">Folium</a></li>
                                        <li><a href="https://pillow.readthedocs.io/en/stable/">Pillow</a></li>
                                        <li><a href="https://piexif.readthedocs.io/en/latest/">piexif</a></li>
                                        <li><a href="https://plotly.com/python/">plotly</a></li>
                                    </ul>

                                    <p>Программа распространяется по лицензии GPLv3</p>
                             """
        self.lbl.setText(str_to_show)
        self.lbl.setFont(font10)
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)

        self.btn_ok.setText("Ок")
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)

        self.btn_ok.clicked.connect(self.close)

        self.resize(self.lbl.width()+20, self.lbl.height() + self.btn_ok.height() + 20)
