import logging
import os
import sys

import piexif
import matplotlib
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import ErrorsAndWarnings
import Metadata
import PhotoDataDB
import Screenconfig
import Settings

font14 = QtGui.QFont('Times', 14)

stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()
stylesheet9 = str()
loading_icon = str()

system_scale = Screenconfig.monitor_info()[1]


# объект окна настроек
class StatisticsWin(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle('Настройки')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1000, 300)

        widget = StatisticsWidget()
        self.setCentralWidget(widget)
        self.resize(widget.size())

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self):
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global stylesheet9
        global loading_icon

        if Settings.get_theme_color() == 'light':
            stylesheet1 = """
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            """
            stylesheet2 = """
                                border: 0px;
                                color: #000000;
                                background-color: #F0F0F0
                            """
            stylesheet8 = """
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
            stylesheet9 = """
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
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 = """
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
            stylesheet9 = """
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


# сами настройки (виджет)
class StatisticsWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1200, 700)

        self.all_files = self.get_all_main_catalog_files()

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(5)
        
        self.hours_lbl = QLabel(self)
        self.hours_lbl.setText("Время суток:")
        self.layout.addWidget(self.hours_lbl, 0, 0, 1, 1)

        self.figure_hours = matplotlib.pyplot.figure(figsize=(9, 3), dpi=80)
        self.canvas_hours = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(self.figure_hours)
        self.layout.addWidget(self.canvas_hours, 1, 0, 1, 1)

        self.iso_lbl = QLabel(self)
        self.iso_lbl.setText("ISO:")
        self.layout.addWidget(self.iso_lbl, 0, 1, 1, 1)

        self.figure_iso = matplotlib.pyplot.figure(figsize=(7, 7), dpi=80)
        self.canvas_iso = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(self.figure_iso)
        self.layout.addWidget(self.canvas_iso, 1, 1, 1, 1)

        self.camera_lbl = QLabel(self)
        self.camera_lbl.setText("Камеры:")
        self.layout.addWidget(self.camera_lbl, 0, 2, 1, 1)

        self.figure_camera = matplotlib.pyplot.figure(figsize=(7, 7), dpi=80)
        self.canvas_camera = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(self.figure_camera)
        self.layout.addWidget(self.canvas_camera, 1, 2, 1, 1)

        self.start_btn = QPushButton(self)
        self.start_btn.setText('Start')
        self.layout.addWidget(self.start_btn, 2, 0, 1, 1)
        self.start_btn.clicked.connect(self.take_hour_dict)
        self.start_btn.clicked.connect(self.take_iso_dict)
        self.start_btn.clicked.connect(self.take_camera_dict)

    def get_all_main_catalog_files(self):
        all_files = []
        main_catalog = Settings.get_destination_media() + r'\\Media\\Photo\\const'
        for root, dirs, files in os.walk(main_catalog):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".JPG"):
                    name = root.replace('\\', '/') + '/' + file
                    all_files.append(name)
        return all_files

    def take_hour_dict(self):
        self.time_looter = TimeLooter(self.all_files)
        self.time_looter.start()
        self.time_looter.finished.connect(lambda result: self.take_hour_ready(result))

    def take_hour_ready(self, result):
        self.time_looter = None
        self.make_time_graphic(result)

    def make_time_graphic(self, hd):
        self.figure_hours.clear()
        ax = self.figure_hours.add_subplot(111)
        ax.grid(True)
        ax.bar([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
               [hd[0], hd[1], hd[2], hd[3], hd[4], hd[5], hd[6], hd[7], hd[8], hd[9],
                hd[10], hd[11], hd[12], hd[13], hd[14], hd[15], hd[16], hd[17], hd[18], hd[19],
                hd[20], hd[21], hd[22], hd[23]], width=1, align='edge', color='blue')
        ax.set_xlim(0, 24)
        ax.set_ylim(0, hd[max(hd, key=hd.get)])
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])

        ax.set_yticks([i for i in range(0, hd[max(hd, key=hd.get)]+1)])
        self.canvas_hours.draw()

    def take_iso_dict(self):
        self.iso_looter = IsoLooter(self.all_files)
        self.iso_looter.start()
        self.iso_looter.finished.connect(lambda result: self.take_iso_ready(result))

    def take_iso_ready(self, result):
        self.iso_looter = None
        self.make_iso_graphic(result)

    def make_iso_graphic(self, hd):
        self.figure_iso.clear()
        bx = self.figure_iso.add_subplot(111)
        sizes = list(hd.values())
        hd_keys = list(hd.keys())
        labels = []
        for i in range(len(sizes)):
            labels.append(f"{hd_keys[i]} ({sizes[i]})")
        bx.pie(sizes, labels=labels)
        self.canvas_iso.draw()

    def take_camera_dict(self):
        self.camera_looter = CameraLooter(self.all_files)
        self.camera_looter.start()
        self.camera_looter.finished.connect(lambda result: self.take_camera_ready(result))

    def take_camera_ready(self, result):
        self.camera_looter = None
        self.make_camera_graphic(result)

    def make_camera_graphic(self, hd):
        self.figure_camera.clear()
        bx = self.figure_camera.add_subplot(111)
        sizes = list(hd.values())
        hd_keys = list(hd.keys())
        labels = []
        for i in range(len(sizes)):
            labels.append(f"{hd_keys[i]} ({sizes[i]})")
        bx.pie(sizes, labels=labels)
        self.canvas_camera.draw()



class TimeLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.hours_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
                           14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0}

        self._init = False

    def run(self):
        for file in self.all_files:
            try:
                hour = piexif.load(file)['Exif'][36867].decode('utf-8')[-8:-6]
                self.hours_dict[int(hour)] += 1
            except KeyError:
                pass

        self.finished.emit(self.hours_dict)


class IsoLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.iso_dict = {}

        self._init = False

    def run(self):
        for file in self.all_files:
            try:
                iso = piexif.load(file)['Exif'][34855]
                try:
                    self.iso_dict[int(iso)] += 1
                except KeyError:
                    self.iso_dict[int(iso)] = 1
            except KeyError:
                pass

        result = dict(sorted(self.iso_dict.items()))

        self.finished.emit(result)


class CameraLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.camera_dict = {}

        self._init = False

    def run(self):
        for file in self.all_files:
            try:
                camera = piexif.load(file)['0th'][272].decode('utf-8')
                try:
                    self.camera_dict[camera] += 1
                except KeyError:
                    self.camera_dict[camera] = 1
            except KeyError:
                pass

        result ={}
        for camera in list(self.camera_dict.keys()):
            if camera in list(result.keys()):
                pass
            else:
                normname = Metadata.equip_solo_name_check(camera, 'camera')
                if normname == camera:
                    result[camera] = self.camera_dict[camera]
                else:
                    try:
                        norm_value = self.camera_dict.pop(normname)
                    except KeyError:
                        norm_value = 0
                    exif_value = self.camera_dict[camera]
                    result[normname] = norm_value + exif_value

        self.finished.emit(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StatisticsWin()
    win.show()
    sys.exit(app.exec_())

# ISO +
# Время суток съёмки +
# фокусное расстояние
# выдержка
# Диафрагма
# на какую камеру
# на какой объектив
