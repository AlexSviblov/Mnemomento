import logging
import os
import sys

import piexif
import matplotlib
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
import exiftool


from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

from PyQt5 import QtWebEngineWidgets
import plotly.express as px
import plotly.graph_objects as go

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
text_color = str()
plot_back_color = str()
bar_color = str()
area_color = str()
bar_time_color = str()

system_scale = Screenconfig.monitor_info()[1]

mutex = QtCore.QMutex()


# объект окна настроек
class StatisticsWin(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle('Статистика основного каталога')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1000, 300)

        widget = StatisticsWidget()
        self.setCentralWidget(widget)
        self.resize(widget.size())

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self) -> None:
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global stylesheet9
        global text_color
        global plot_back_color
        global bar_color
        global area_color
        global bar_time_color

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
            text_color = "black"
            plot_back_color = "white"
            bar_time_color = "black"
            bar_color = 'blue'
            area_color = "#F4F4F4"
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
            text_color = "white"
            plot_back_color = "#585858"
            bar_color = "yellow"
            bar_time_color = "#fff100"
            area_color = "#181818"

        self.setStyleSheet(stylesheet2)


# сами настройки (виджет)
class StatisticsWidget(QWidget):
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Статистика основного каталога')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1366, 720)
        self.setStyleSheet(stylesheet2)

        self.all_files = self.get_all_main_catalog_files()

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(5)

        self.graphic_hours = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_hours.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_hours, 0, 0, 1, 1)

        self.graphic_camera = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_camera.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_camera, 0, 1, 1, 1)

        self.graphic_lens = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_lens.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_lens, 0, 2, 1, 1)

        self.graphic_iso = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_iso.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_iso, 1, 0, 1, 1)

        self.graphic_fnumber = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_fnumber.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_fnumber, 1, 1, 1, 1)

        self.graphic_exposuretime = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_exposuretime.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_exposuretime, 1, 2, 1, 2)

        self.graphic_fl = QtWebEngineWidgets.QWebEngineView(self)
        self.graphic_fl.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.graphic_fl, 0, 3, 1, 1)

        self.start_btn = QPushButton(self)
        self.start_btn.setText('Пересчитать')
        self.layout.addWidget(self.start_btn, 2, 0, 1, 1)
        self.start_btn.setStyleSheet(stylesheet8)
        self.start_btn.setFont(font14)
        self.start_btn.clicked.connect(self.take_hour_dict)
        self.start_btn.clicked.connect(self.take_iso_dict)
        self.start_btn.clicked.connect(self.take_camera_dict)
        self.start_btn.clicked.connect(self.take_lens_dict)
        self.start_btn.clicked.connect(self.take_fnumber_dict)
        self.start_btn.clicked.connect(self.take_exposuretime_dict)
        self.start_btn.clicked.connect(self.take_fl_dict)

        self.start_btn.click()

    def get_all_main_catalog_files(self) -> list[str]:
        all_files = []
        main_catalog = Settings.get_destination_media() + r'/Media/Photo/const'
        for root, dirs, files in os.walk(main_catalog):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".JPG"):
                    root_name = str(root)
                    root_name = root_name.replace(r'\\', '/')
                    root_name = root_name.replace('\\', '/')
                    root_name = root_name.replace('//', '/')
                    name = root_name + '/' + file
                    all_files.append(name)
        return all_files

    def take_hour_dict(self) -> None:
        self.time_looter = HoursLooter(self.all_files)
        self.time_looter.start()
        self.time_looter.finished.connect(lambda result: self.take_hour_ready(result))

    def take_hour_ready(self, result: dict) -> None:
        self.time_looter = None
        self.result_hour = result
        self.make_hour_graphic(result)

    def make_hour_graphic(self, hd: dict) -> None:
        x_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = ["00:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00",
                      "7:00-8:00", "8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00",
                      "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
                      "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-00:00"]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate='%{text} (%{y})<extra></extra>',
                                    text=hover_text, textposition='none', marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text='Время съёмки',
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)
        fig.update_traces(width=1)
        fig.update_xaxes(tickvals=[-0.5, 1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5, 21.5],
                         ticktext=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
        self.graphic_hours.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_camera_dict(self) -> None:
        self.camera_looter = CameraLooter(self.all_files)
        self.camera_looter.start()
        self.camera_looter.finished.connect(lambda result: self.take_camera_ready(result))

    def take_camera_ready(self, result: dict) -> None:
        self.camera_looter = None
        self.result_camera = result
        self.make_camera_graphic(result)

    def make_camera_graphic(self, hd: dict) -> None:
        sizes = list(hd.values())
        names = list(hd.keys())
        fig = go.Figure(data=go.Pie(values=sizes, labels=names))
        fig.update_layout(autosize=True, title_text='Камеры', title_x=0.5, paper_bgcolor=area_color,
                          plot_bgcolor=plot_back_color, font_color=text_color, title_font_color=text_color)
        self.graphic_camera.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_lens_dict(self) -> None:
        self.lens_looter = LensLooter(self.all_files)
        self.lens_looter.start()
        self.lens_looter.finished.connect(lambda result: self.take_lens_ready(result))

    def take_lens_ready(self, result: dict) -> None:
        self.lens_looter = None
        self.result_lens = result
        self.make_lens_graphic(result)

    def make_lens_graphic(self, hd: dict) -> None:
        sizes = list(hd.values())
        names = list(hd.keys())
        fig = go.Figure(data=go.Pie(values=sizes, labels=names))
        fig.update_layout(autosize=True, title_text='Объективы', title_x=0.5, paper_bgcolor=area_color,
                          plot_bgcolor=plot_back_color, font_color=text_color, title_font_color=text_color)
        self.graphic_lens.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_iso_dict(self) -> None:
        self.iso_looter = IsoLooter(self.all_files)
        self.iso_looter.start()
        self.iso_looter.finished.connect(lambda result: self.take_iso_ready(result))

    def take_iso_ready(self, result: dict) -> None:
        self.iso_looter = None
        self.result_iso = result
        self.make_iso_graphic(result)

    def make_iso_graphic(self, hd: dict) -> None:
        iso_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = iso_values
        x_values = [i for i in range(0, len(iso_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate='%{text} (%{y})<extra></extra>',
                                    text=hover_text, textposition='none', marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text='ISO',
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}
        for i in range(11):
            tick_dict[x_values[int(len(x_values) / 10) * i]] = iso_values[int(len(x_values) / 10) * i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))

        self.graphic_iso.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_fnumber_dict(self) -> None:
        self.fnumber_looter = FnumberLooter(self.all_files)
        self.fnumber_looter.start()
        self.fnumber_looter.finished.connect(lambda result: self.take_fnumber_ready(result))

    def take_fnumber_ready(self, result: dict) -> None:
        self.fnumber_looter = None
        self.result_fnumber = result
        self.make_fnumber_graphic(result)

    def make_fnumber_graphic(self, hd: dict) -> None:
        fnumber_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = fnumber_values
        x_values = [i for i in range(0, len(fnumber_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate='%{text} (%{y})<extra></extra>',
                                    text=hover_text, textposition='none', marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text='Диафрагма',
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}
        # for i in range(len(x_values)):
        #     if 20 >= len(x_values) > 10:
        #         if i%2 == 0:
        #             tick_dict[x_values[i]] = fnumber_values[i]
        #     elif 40 >= len(x_values) > 20:
        #         if i%5 == 0:
        #             tick_dict[x_values[i]] = fnumber_values[i]
        #     elif len(x_values) > 40:
        #         if i%10 == 0:
        #             tick_dict[x_values[i]] = fnumber_values[i]
        #     else:
        #         tick_dict[x_values[i]] = fnumber_values[i]

        for i in range(11):
                tick_dict[x_values[int(len(x_values)/10)*i]] = fnumber_values[int(len(x_values)/10)*i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))
        self.graphic_fnumber.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_exposuretime_dict(self) -> None:
        self.exposuretime_looter = ExposureTimeLooter(self.all_files)
        self.exposuretime_looter.start()
        self.exposuretime_looter.finished.connect(lambda result: self.take_exposuretime_ready(result))

    def take_exposuretime_ready(self, result: dict) -> None:
        self.exposuretime_looter = None
        self.result_exposuretime = result
        self.make_exposuretime_graphic(result)

    def make_exposuretime_graphic(self, hd: dict) -> None:
        def clear_labels(float_times, labels_enter):
            near_cleared = []
            labels = list(labels_enter)
            for i in range(len(float_times)):
                for j in range(len(float_times)):
                    if i == j:
                        pass
                    else:
                        if abs(float_times[i] - float_times[j]) < 2:
                            if float_times[j] in near_cleared:
                                labels[i] = ''
                            else:
                                if float_times[i] >= 0.1 and labels[i]:
                                    labels[i] = str(round(float(labels[i]), 2))
                                near_cleared.append(float_times[i])
                                labels[j] = ''
            return labels

        sizes = list(hd.values())
        times = list(hd.keys())
        float_times = []
        for t in times:
            if len(t.split('/')) == 2:
                float_value_buf = float(int(t.split('/')[0]) / int(t.split('/')[1]))
                float_value = float(((-1) * (1 / float_value_buf) / 50)+0.3)
            else:
                float_value = float(t)
            float_times.append(float_value)

        hover_text = []
        for time in times:
            hover_text.append(time[:7])
        fig = go.Figure(data=go.Bar(x=float_times, y=sizes, hovertemplate='%{text} (%{y})<extra></extra>',
                                    text=hover_text, textposition='none', marker_color=bar_time_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text='Выдержка',
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)
        fig.update_xaxes(tickvals=list(float_times),
                         ticktext=clear_labels(float_times, times))
        fig.update_traces(width=0.02)

        self.graphic_exposuretime.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def take_fl_dict(self) -> None:
        self.fl_looter = FocalLengthLooter(self.all_files)
        self.fl_looter.start()
        self.fl_looter.finished.connect(lambda result: self.take_fl_ready(result))

    def take_fl_ready(self, result: dict) -> None:
        self.fl_looter = None
        self.result_fl = result
        self.make_fl_graphic(result)

    def make_fl_graphic(self, hd: dict) -> None:
        fl_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = fl_values
        x_values = [i for i in range(0, len(fl_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate='%{text} (%{y})<extra></extra>',
                                    text=hover_text, textposition='none', marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text='Фокусное расстояние',
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}
        for i in range(11):
                tick_dict[x_values[int(len(x_values)/10)*i]] = fl_values[int(len(x_values)/10)*i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))
        self.graphic_fl.setHtml(fig.to_html(include_plotlyjs='cdn'))
        QtCore.QCoreApplication.processEvents()

    def update_colors(self) -> None:
        self.parent().stylesheet_color()

        self.make_hour_graphic(self.result_hour)
        self.make_camera_graphic(self.result_camera)
        self.make_lens_graphic(self.result_lens)
        self.make_fl_graphic(self.result_fl)
        self.make_fnumber_graphic(self.result_fnumber)
        self.make_iso_graphic(self.result_iso)
        self.make_exposuretime_graphic(self.result_exposuretime)

        self.start_btn.setStyleSheet(stylesheet8)


class HoursLooter(QtCore.QThread):
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
            except (ValueError, KeyError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            hour_exif = et.execute("-EXIF:DateTimeOriginal", file)
                            if hour_exif:
                                try:
                                    hour = int(hour_exif.split(':')[-2])
                                    try:
                                        self.hours_dict[hour] += 1
                                    except KeyError:
                                        self.hours_dict[hour] = 1
                                except ValueError:
                                    pass
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        self.finished.emit(self.hours_dict)


class CameraLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.camera_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                camera = piexif.load(file)['0th'][272].decode('utf-8')
                if camera:
                    try:
                        self.camera_dict[camera] += 1
                    except KeyError:
                        self.camera_dict[camera] = 1
            except (ValueError, KeyError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            camera_exif = et.execute("-EXIF:Model", file)
                            if camera_exif:
                                camera = camera_exif.split(':')[-1]
                                try:
                                    self.camera_dict[camera] += 1
                                except KeyError:
                                    self.camera_dict[camera] = 1
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result ={}
        for camera in list(self.camera_dict.keys()):
            if camera in list(result.keys()):
                pass
            else:
                mutex.lock()
                normname = Metadata.equip_solo_name_check(camera, 'camera')
                mutex.unlock()
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


class LensLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.lens_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                lens = piexif.load(file)['Exif'][42036].decode('utf-8')
                if lens:
                    try:
                        self.lens_dict[lens] += 1
                    except KeyError:
                        self.lens_dict[lens] = 1
            except (ValueError, KeyError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            lens_exif = et.execute("-EXIF:LensModel", file)
                            if lens_exif:
                                lens = lens_exif.split(':')[-1]
                                try:
                                    self.lens_dict[lens] += 1
                                except KeyError:
                                    self.lens_dict[lens] = 1
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result ={}
        for lens in list(self.lens_dict.keys()):
            if lens in list(result.keys()):
                pass
            else:
                mutex.lock()
                normname = Metadata.equip_solo_name_check(lens, 'lens')
                mutex.unlock()
                if normname == lens:
                    result[lens] = self.lens_dict[lens]
                else:
                    try:
                        norm_value = self.lens_dict.pop(normname)
                    except KeyError:
                        norm_value = 0
                    exif_value = self.lens_dict[lens]
                    result[normname] = norm_value + exif_value

        self.finished.emit(result)


class IsoLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.iso_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                iso = piexif.load(file)['Exif'][34855]
                if iso:
                    try:
                        self.iso_dict[int(iso)] += 1
                    except KeyError:
                        self.iso_dict[int(iso)] = 1
            except (KeyError, ValueError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            iso_exif = et.execute("-EXIF:ISO", file)
                            if iso_exif:
                                try:
                                    iso = int(iso_exif.split(':')[-1])
                                    try:
                                        self.iso_dict[iso] += 1
                                    except KeyError:
                                        self.iso_dict[iso] = 1
                                except ValueError:
                                    pass
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result = dict(sorted(self.iso_dict.items()))

        self.finished.emit(result)


class FnumberLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.fnumber_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                fnumber = piexif.load(file)['Exif'][33437][0]/piexif.load(file)['Exif'][33437][1]
                if fnumber:
                    try:
                        self.fnumber_dict[fnumber] += 1
                    except KeyError:
                        self.fnumber_dict[fnumber] = 1
            except (ValueError, KeyError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            fnumber_exif = et.execute("-EXIF:FNumber", file)
                            if fnumber_exif:
                                try:
                                    fnumber = float(fnumber_exif.split(':')[-1])
                                    try:
                                        self.fnumber_dict[fnumber] += 1
                                    except KeyError:
                                        self.fnumber_dict[fnumber] = 1
                                except ValueError:
                                    pass
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result = dict(sorted(self.fnumber_dict.items()))

        self.finished.emit(result)
        

class ExposureTimeLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.time_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                time = piexif.load(file)['Exif'][33434][0]/piexif.load(file)['Exif'][33434][1]
                if time:
                    if time >= 0.1:
                        expo_time = str(time)
                    else:
                        try:
                            denominator = 1 / time
                            expo_time = f"1/{int(denominator)}"
                        except ZeroDivisionError:
                            expo_time = 0
                    try:
                        self.time_dict[expo_time] += 1
                    except KeyError:
                        self.time_dict[expo_time] = 1
            except (KeyError, ValueError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            time_exif = et.execute("-EXIF:ExposureTime", file)
                            if time_exif:
                                try:
                                    time_raw = float(time_exif.split(':')[-1])
                                    if time_raw > 0.1:
                                        time = str(time_raw)
                                    else:
                                        time = f"1/{int(1/time_raw)}"
                                    try:
                                        self.time_dict[time] += 1
                                    except KeyError:
                                        self.time_dict[time] = 1
                                except ValueError:
                                    pass
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result = dict(sorted(self.time_dict.items()))

        self.finished.emit(result)


class FocalLengthLooter(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.fl_dict = {}

        # self._init = False

    def run(self):
        for file in self.all_files:
            try:
                fl = piexif.load(file)['Exif'][37386][0]/piexif.load(file)['Exif'][37386][1]
                if fl:
                    try:
                        self.fl_dict[fl] += 1
                    except KeyError:
                        self.fl_dict[fl] = 1
            except (KeyError, ValueError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            fl_exif = et.execute("-EXIF:FocalLength", file)
                            if fl_exif:
                                try:
                                    fl = int(fl_exif.split(':')[-1])
                                    try:
                                        self.fl_dict[fl] += 1
                                    except KeyError:
                                        self.fl_dict[fl] = 1
                                except ValueError:
                                    pass
                            else:
                                pass
                    except exiftool.exceptions.ExifToolExecuteError:
                        pass
                else:
                    pass

        result = dict(sorted(self.fl_dict.items()))

        self.finished.emit(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StatisticsWin()
    win.show()
    sys.exit(app.exec_())
