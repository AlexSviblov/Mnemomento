from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
import sys
import Settings


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()


font10 = QtGui.QFont('Times', 10)
font14 = QtGui.QFont('Times', 14)


def stylesheet_color():
    global stylesheet1
    global stylesheet2
    global stylesheet8

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
    else:  # Settings.get_theme_color() == 'dark'
        stylesheet1 =   """
                            border: 1px;
                            border-color: #696969;
                            border-style: solid;
                            color: #D3D3D3;
                            background-color: #1C1C1C
                        """
        stylesheet2 = """
                            border: 0px;
                            color: #D3D3D3;
                            background-color: #1C1C1C
                        """
        stylesheet8 = """
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


# добавляемое в основной каталог фото уже есть (совпали имя и папка по дате)
class AboutInfo(QDialog):
    def __init__(self):
        super(AboutInfo, self).__init__()
        stylesheet_color()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Обнаружены совпадения')
        self.setStyleSheet(stylesheet2)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        self.answer = None

        self.lbl = QLabel(self)
        str_to_show =   """
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
                            </ul>
                            
                            <p>Программа распространяется по лицензии GPLv3</p>
                        """
        self.lbl.setText(str_to_show)
        self.lbl.setFont(font10)
        self.layout.addWidget(self.lbl, 0, 0, 1, 1)


        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('Ок')
        self.btn_ok.setStyleSheet(stylesheet8)
        self.btn_ok.setFont(font14)
        self.layout.addWidget(self.btn_ok, 1, 0, 1, 1)

        self.resize(self.lbl.width()+20, self.lbl.height() + self.btn_ok.height() + 20)

        self.btn_ok.clicked.connect(lambda: self.close())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AboutInfo()
    win.show()
    sys.exit(app.exec_())