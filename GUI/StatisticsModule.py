# coding: utf-8
import os
import sys

import piexif
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
import exiftool
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QPushButton

from PyQt5 import QtWebEngineWidgets
import plotly.graph_objects as go

from Metadata import MetadataPhoto
from Database import PhotoDataDB
from GUI import Screenconfig, Settings


font14 = QtGui.QFont("Times", 14)

stylesheet1 = str()
stylesheet2 = str()
stylesheet5 = str()
stylesheet8 = str()
stylesheet9 = str()
text_color = str()
plot_back_color = str()
bar_color = str()
area_color = str()
bar_time_color = str()

system_scale = Screenconfig.monitor_info()[1]

mutex = QtCore.QMutex()


class StatisticsWin(QMainWindow):
    """
    Объект окна настроек
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle("Статистика основного каталога")
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1000, 300)

        widget = StatisticsWidget()
        self.setCentralWidget(widget)
        self.resize(widget.size())

    def stylesheet_color(self) -> None:
        """
        Задать стили для всего модуля в зависимости от выбранной темы
        """
        global stylesheet1
        global stylesheet2
        global stylesheet5
        global stylesheet8
        global stylesheet9
        global text_color
        global plot_back_color
        global bar_color
        global area_color
        global bar_time_color

        theme = Settings.get_theme_color()
        style = Screenconfig.style_dict
        stylesheet1 = style[f"{theme}"]["stylesheet1"]
        stylesheet2 = style[f"{theme}"]["stylesheet2"]
        stylesheet5 = style[f"{theme}"]["stylesheet5"]
        stylesheet8 = style[f"{theme}"]["stylesheet8"]
        stylesheet9 = style[f"{theme}"]["stylesheet9"]
        text_color = style[f"{theme}"]["statistics"]["text_color"]
        plot_back_color = style[f"{theme}"]["statistics"]["plot_back_color"]
        bar_color = style[f"{theme}"]["statistics"]["bar_color"]
        area_color = style[f"{theme}"]["statistics"]["area_color"]
        bar_time_color = style[f"{theme}"]["statistics"]["bar_time_color"]

        self.setStyleSheet(stylesheet2)


class StatisticsWidget(QWidget):
    """
    Сами настройки (виджет)
    """
    update_main_widget = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Статистика основного каталога")
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(1366, 720)
        self.setStyleSheet(stylesheet2)

        self.counter_hours = 0
        self.counter_camera = 0
        self.counter_lens = 0
        self.counter_iso = 0
        self.counter_fnumber = 0
        self.counter_fl = 0
        self.counter_expotime = 0

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
        self.start_btn.setText("Показать")
        self.layout.addWidget(self.start_btn, 2, 0, 1, 1)
        self.start_btn.setStyleSheet(stylesheet8)
        self.start_btn.setFont(font14)
        self.start_btn.clicked.connect(self.start_calculate)

        self.show_shortcut = QShortcut(QtGui.QKeySequence(Settings.get_hotkeys()["show_stat_map"]), self)
        self.show_shortcut.activated.connect(self.start_calculate)

        self.progress_group = QGroupBox(self)
        self.progress_layout = QGridLayout(self)
        self.progress_group.setLayout(self.progress_layout)
        self.progress_group.setFixedHeight(int(0))
        self.layout.addWidget(self.progress_group, 3, 0, 1, 2)

        self.layout_type = QGridLayout(self)
        self.layout_type.setAlignment(QtCore.Qt.AlignLeft)
        self.groupbox_sort = QGroupBox(self)
        self.groupbox_sort.setFixedHeight(int(60))
        self.groupbox_sort.setLayout(self.layout_type)
        self.layout.addWidget(self.groupbox_sort, 2, 1, 1, 2)

        self.fill_sort_groupbox()
        self.set_sort_layout()

        self.progressbar_hours = QProgressBar(self)
        self.progressbar_hours.setFont(font14)
        self.progressbar_hours.setValue(0)
        self.progressbar_hours.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_hours, 0, 0, 1, 1)

        self.progressbar_camera = QProgressBar(self)
        self.progressbar_camera.setFont(font14)
        self.progressbar_camera.setValue(0)
        self.progressbar_camera.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_camera, 0, 1, 1, 1)

        self.progressbar_lens = QProgressBar(self)
        self.progressbar_lens.setFont(font14)
        self.progressbar_lens.setValue(0)
        self.progressbar_lens.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_lens, 0, 2, 1, 1)

        self.progressbar_iso = QProgressBar(self)
        self.progressbar_iso.setFont(font14)
        self.progressbar_iso.setValue(0)
        self.progressbar_iso.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_iso, 0, 3, 1, 1)

        self.progressbar_fnumber = QProgressBar(self)
        self.progressbar_fnumber.setFont(font14)
        self.progressbar_fnumber.setValue(0)
        self.progressbar_fnumber.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_fnumber, 0, 4, 1, 1)

        self.progressbar_expotime = QProgressBar(self)
        self.progressbar_expotime.setFont(font14)
        self.progressbar_expotime.setValue(0)
        self.progressbar_expotime.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_expotime, 0, 5, 1, 1)

        self.progressbar_fl = QProgressBar(self)
        self.progressbar_fl.setFont(font14)
        self.progressbar_fl.setValue(0)
        self.progressbar_fl.setStyleSheet(stylesheet5)
        self.progress_layout.addWidget(self.progressbar_fl, 0, 6, 1, 1)

    def start_calculate(self):
        """
        Запуск всех вычислений
        """
        def start() -> None:
            self.progress_group.setFixedHeight(int(60))
            QtCore.QCoreApplication.processEvents()
            self.reset_counter()
            sort_type = self.group_type.currentText()
            arg1, arg2, arg3 = "", "", ""
            match sort_type:
                case "Дата":
                    arg1 = self.date_year.currentText()
                    arg2 = self.date_month.currentText()
                    arg3 = self.date_day.currentText()
                case "Оборудование":
                    arg1 = self.camera_choose.currentText()
                    arg2 = self.lens_choose.currentText()
                case _:
                    pass

            self.paths_process = FilesPaths(type_filter=sort_type, arg1=arg1, arg2=arg2, arg3=arg3)
            self.paths_process.files.connect(lambda fl: finish(fl))
            self.paths_process.start()

        def finish(files_list: list[str]) -> None:
            self.all_files = files_list
            self.number_of_operations = len(self.all_files)

            self.take_hour_dict()
            self.take_iso_dict()
            self.take_camera_dict()
            self.take_lens_dict()
            self.take_fnumber_dict()
            self.take_exposuretime_dict()
            self.take_fl_dict()

        start()

    def take_hour_dict(self) -> None:
        """
        Запустить сбор статистики времени съёмки
        """
        self.time_looter = HoursLooter(self.all_files)
        self.time_looter.changed.connect(self.change_progressbar_hours)
        self.time_looter.start()
        self.time_looter.finished.connect(lambda result: self.take_hour_ready(result))

    def take_hour_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики времени
        съёмки
        :param result: словарь, где ключи - временной интервал съёмки, значение - сколько фото с таких значением
        """
        self.progressbar_hours.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.time_looter = None
        self.result_hour = result
        self.make_hour_graphic(result)

    def make_hour_graphic(self, hd: dict) -> None:
        """
        Нарисовать график времени съёмки
        :param hd: словарь, где ключи - время съёмки, значение - сколько фото с таких значением
        """
        x_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = ["00:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00",
                      "7:00-8:00", "8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00", "13:00-14:00",
                      "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
                      "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-00:00"]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate="%{text} (%{y})<extra></extra>",
                                    text=hover_text, textposition="none", marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text="Время съёмки",
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)
        fig.update_traces(width=1)
        fig.update_xaxes(tickvals=[-0.5, 1.5, 3.5, 5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5, 21.5],
                         ticktext=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
        self.graphic_hours.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_camera_dict(self) -> None:
        """
        Запустить сбор статистики камер
        """
        self.camera_looter = CameraLooter(self.all_files)
        self.camera_looter.changed.connect(self.change_progressbar_camera)
        self.camera_looter.start()
        self.camera_looter.finished.connect(lambda result: self.take_camera_ready(result))

    def take_camera_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики камер
        :param result: словарь, где ключи - камеры, значение - сколько фото с таких значением
        """
        self.progressbar_camera.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.camera_looter = None
        self.result_camera = result
        self.make_camera_graphic(result)

    def make_camera_graphic(self, hd: dict) -> None:
        """
        Нарисовать график камер
        :param hd: словарь, где ключи - камеры, значение - сколько фото с таких значением
        """
        sizes = list(hd.values())
        names = list(hd.keys())
        fig = go.Figure(data=go.Pie(values=sizes, labels=names))
        fig.update_layout(autosize=True, title_text="Камеры", title_x=0.5, paper_bgcolor=area_color,
                          plot_bgcolor=plot_back_color, font_color=text_color, title_font_color=text_color)
        self.graphic_camera.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_lens_dict(self) -> None:
        """
        Запустить сбор статистики объективов
        """
        self.lens_looter = LensLooter(self.all_files)
        self.lens_looter.changed.connect(self.change_progressbar_lens)
        self.lens_looter.start()
        self.lens_looter.finished.connect(lambda result: self.take_lens_ready(result))

    def take_lens_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики объективов
        :param result: словарь, где ключи - объективы, значение - сколько фото с таких значением
        """
        self.progressbar_lens.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.lens_looter = None
        self.result_lens = result
        self.make_lens_graphic(result)

    def make_lens_graphic(self, hd: dict) -> None:
        """
        Нарисовать график объективов
        :param hd: словарь, где ключи - объективы, значение - сколько фото с таких значением
        """
        sizes = list(hd.values())
        names = list(hd.keys())
        fig = go.Figure(data=go.Pie(values=sizes, labels=names))
        fig.update_layout(autosize=True, title_text="Объективы", title_x=0.5, paper_bgcolor=area_color,
                          plot_bgcolor=plot_back_color, font_color=text_color, title_font_color=text_color)
        self.graphic_lens.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_iso_dict(self) -> None:
        """
        Запустить сбор статистики ISO
        """
        self.iso_looter = IsoLooter(self.all_files)
        self.iso_looter.changed.connect(self.change_progressbar_iso)
        self.iso_looter.start()
        self.iso_looter.finished.connect(lambda result: self.take_iso_ready(result))

    def take_iso_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики ISO
        :param result: словарь, где ключи - ISO, значение - сколько фото с таких значением
        """
        self.progressbar_iso.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.iso_looter = None
        self.result_iso = result
        self.make_iso_graphic(result)

    def make_iso_graphic(self, hd: dict) -> None:
        """
        Нарисовать график ISO
        :param hd: словарь, где ключи - ISO, значение - сколько фото с таких значением
        """
        iso_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = iso_values
        x_values = [i for i in range(0, len(iso_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate="%{text} (%{y})<extra></extra>",
                                    text=hover_text, textposition="none", marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text="ISO",
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}
        if len(iso_values) >= 11:
            for i in range(10):
                tick_dict[x_values[int(len(x_values) / 10) * i]] = iso_values[int(len(x_values) / 10) * i]
        else:
            for i in range(len(iso_values)):
                tick_dict[i] = iso_values[i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))

        self.graphic_iso.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_fnumber_dict(self) -> None:
        """
        Запустить сбор статистики диафрагмы
        """
        self.fnumber_looter = FnumberLooter(self.all_files)
        self.fnumber_looter.changed.connect(self.change_progressbar_fnumber)
        self.fnumber_looter.start()
        self.fnumber_looter.finished.connect(lambda result: self.take_fnumber_ready(result))

    def take_fnumber_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики диафрагмы
        :param result: словарь, где ключи - диафрагма, значение - сколько фото с таких значением
        """
        self.progressbar_fnumber.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.fnumber_looter = None
        self.result_fnumber = result
        self.make_fnumber_graphic(result)

    def make_fnumber_graphic(self, hd: dict) -> None:
        """
        Нарисовать график диафрагмы
        :param hd: словарь, где ключи - диафрагма, значение - сколько фото с таких значением
        """
        fnumber_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = fnumber_values
        x_values = [i for i in range(0, len(fnumber_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate="%{text} (%{y})<extra></extra>",
                                    text=hover_text, textposition="none", marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text="Диафрагма",
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}

        if len(fnumber_values) >= 11:
            for i in range(10):
                    tick_dict[x_values[int(len(x_values)/10)*i]] = fnumber_values[int(len(x_values)/10)*i]
        else:
            for i in range(len(fnumber_values)):
                    tick_dict[x_values[i]] = fnumber_values[i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))
        self.graphic_fnumber.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_exposuretime_dict(self) -> None:
        """
        Запустить сбор статистики выдержки
        """
        self.exposuretime_looter = ExposureTimeLooter(self.all_files)
        self.exposuretime_looter.changed.connect(self.change_progressbar_expotime)
        self.exposuretime_looter.start()
        self.exposuretime_looter.finished.connect(lambda result: self.take_exposuretime_ready(result))

    def take_exposuretime_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики выдержки
        :param result: словарь, где ключи - выдержка, значение - сколько фото с таких значением
        """
        self.progressbar_expotime.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.exposuretime_looter = None
        self.result_exposuretime = result
        self.make_exposuretime_graphic(result)

    def make_exposuretime_graphic(self, hd: dict) -> None:
        """
        Нарисовать график выдержки
        :param hd: словарь, где ключи - выдержка, значение - сколько фото с таких значением
        """
        def clear_labels(float_times_list, labels_enter):
            near_cleared = []
            labels = list(labels_enter)
            for i in range(len(float_times_list)):
                for j in range(len(float_times_list)):
                    if i == j:
                        pass
                    else:
                        if abs(float_times_list[i] - float_times_list[j]) < 2:
                            if float_times_list[j] in near_cleared:
                                labels[i] = ""
                            else:
                                if float_times_list[i] >= 0.1 and labels[i]:
                                    labels[i] = str(round(float(labels[i]), 2))
                                near_cleared.append(float_times_list[i])
                                labels[j] = ""
            return labels

        sizes = list(hd.values())
        times = list(hd.keys())
        float_times = []
        for t in times:
            if len(t.split("/")) == 2:
                float_value_buf = float(int(t.split("/")[0]) / int(t.split("/")[1]))
                float_value = float(((-1) * (1 / float_value_buf) / 50)+0.3)
            else:
                float_value = float(t)
            float_times.append(float_value)

        hover_text = []
        for time in times:
            hover_text.append(time[:7])
        fig = go.Figure(data=go.Bar(x=float_times, y=sizes, hovertemplate="%{text} (%{y})<extra></extra>",
                                    text=hover_text, textposition="none", marker_color=bar_time_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text="Выдержка",
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)
        fig.update_xaxes(tickvals=list(float_times),
                         ticktext=clear_labels(float_times, times))
        fig.update_traces(width=0.02)

        self.graphic_exposuretime.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def take_fl_dict(self) -> None:
        """
        Запустить сбор статистики фокусного расстояния
        """
        self.fl_looter = FocalLengthLooter(self.all_files)
        self.fl_looter.changed.connect(self.change_progressbar_fl)
        self.fl_looter.start()
        self.fl_looter.finished.connect(lambda result: self.take_fl_ready(result))

    def take_fl_ready(self, result: dict) -> None:
        """
        Убрать прогрессбары, если все прогрессбары скрыты (все данные собраны), отрисовать график статистики фокусного
        расстояния
        :param result: словарь, где ключи - фокусное расстояние, значение - сколько фото с таких значением
        """
        self.progressbar_fl.hide()
        if not self.progressbar_hours.isVisible() and not self.progressbar_fl.isVisible() and not self.progressbar_iso.isVisible() and not self.progressbar_camera.isVisible() and not self.progressbar_lens.isVisible() and not self.progressbar_fnumber.isVisible() and not self.progressbar_expotime.isVisible():
            self.progress_group.setFixedHeight(int(0))
        QtCore.QCoreApplication.processEvents()
        self.fl_looter = None
        self.result_fl = result
        self.make_fl_graphic(result)

    def make_fl_graphic(self, hd: dict) -> None:
        """
        Нарисовать график фокусного расстояния
        :param hd: словарь, где ключи - фокусное расстояние, значение - сколько фото с таких значением
        """
        fl_values = list(hd.keys())
        y_values = list(hd.values())
        hover_text = fl_values
        x_values = [i for i in range(0, len(fl_values))]
        fig = go.Figure(data=go.Bar(x=x_values, y=y_values, hovertemplate="%{text} (%{y})<extra></extra>",
                                    text=hover_text, textposition="none", marker_color=bar_color))
        fig.update_layout(modebar_remove=["lasso", "select", "select2d"], autosize=True, title_text="Фокусное расстояние",
                          title_x=0.5, paper_bgcolor=area_color, plot_bgcolor=plot_back_color,
                          font_color=text_color, title_font_color=text_color)

        tick_dict = {}
        if len(fl_values) >= 11:
            for i in range(10):
                    tick_dict[x_values[int(len(x_values)/10)*i]] = fl_values[int(len(x_values)/10)*i]
        else:
            for i in range(len(fl_values)):
                    tick_dict[i] = fl_values[i]

        fig.update_xaxes(tickvals=list(tick_dict.keys()),
                         ticktext=list(tick_dict.values()))
        self.graphic_fl.setHtml(fig.to_html(include_plotlyjs="cdn"))
        QtCore.QCoreApplication.processEvents()

    def update_colors(self) -> None:
        """
        Нарисовать графики по итогам сбора данных
        """
        self.parent().stylesheet_color()

        self.make_hour_graphic(self.result_hour)
        self.make_camera_graphic(self.result_camera)
        self.make_lens_graphic(self.result_lens)
        self.make_fl_graphic(self.result_fl)
        self.make_fnumber_graphic(self.result_fnumber)
        self.make_iso_graphic(self.result_iso)
        self.make_exposuretime_graphic(self.result_exposuretime)

        self.start_btn.setStyleSheet(stylesheet8)

    def reset_counter(self):
        """
        Сбросить все счётчики (для повторного отображения статистики)
        """
        self.counter_hours = 0
        self.counter_camera = 0
        self.counter_lens = 0
        self.counter_iso = 0
        self.counter_fnumber = 0
        self.counter_fl = 0
        self.counter_expotime = 0

    def change_progressbar_hours(self):
        """
        Обновление прогрессбара статистики времени съёмки
        """
        self.counter_hours += 1
        old_value = self.progressbar_hours.value()
        new_value = int((self.counter_hours/self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_hours.setValue(new_value)
            self.progressbar_hours.update()

    def change_progressbar_camera(self):
        """
        Обновление прогрессбара статистики камер
        """
        self.counter_camera += 1
        old_value = self.progressbar_camera.value()
        new_value = int((self.counter_camera / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_camera.setValue(new_value)
            self.progressbar_camera.update()

    def change_progressbar_lens(self):
        """
        Обновление прогрессбара статистики объективов
        """
        self.counter_lens += 1
        old_value = self.progressbar_lens.value()
        new_value = int((self.counter_lens / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_lens.setValue(new_value)
            self.progressbar_lens.update()

    def change_progressbar_iso(self):
        """
        Обновление прогрессбара статистики ISO
        """
        self.counter_iso += 1
        old_value = self.progressbar_iso.value()
        new_value = int((self.counter_iso / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_iso.setValue(new_value)
            self.progressbar_iso.update()

    def change_progressbar_fnumber(self):
        """
        Обновление прогрессбара статистики диафрагмы
        """
        self.counter_fnumber += 1
        old_value = self.progressbar_fnumber.value()
        new_value = int((self.counter_fnumber / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_fnumber.setValue(new_value)
            self.progressbar_fnumber.update()

    def change_progressbar_expotime(self):
        """
        Обновление прогрессбара статистики выдержки
        """
        self.counter_expotime += 1
        old_value = self.progressbar_expotime.value()
        new_value = int((self.counter_expotime / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_expotime.setValue(new_value)
            self.progressbar_expotime.update()

    def change_progressbar_fl(self):
        """
        Обновление прогрессбара статистики фокусного расстояния
        """
        self.counter_fl += 1
        old_value = self.progressbar_fl.value()
        new_value = int((self.counter_fl / self.number_of_operations)*100)
        if new_value != old_value:
            self.progressbar_fl.setValue(new_value)
            self.progressbar_fl.update()

    def fill_date(self, mode: str) -> None:
        """
        Заполнение полей сортировки по дате
        :param mode: режим заполнения (полная дата (год+месяц+день), месяц (+день) или день
        """
        # Получение годов
        def get_years() -> None:
            self.date_year.clear()
            j = 0
            k = 0
            dir_to_find_year = Settings.get_destination_media() + "/Media/Photo/const/"
            all_files_and_dirs = os.listdir(dir_to_find_year)
            dir_list = list()
            for name in all_files_and_dirs:
                if os.path.isdir(dir_to_find_year + name):
                    if len(os.listdir(dir_to_find_year + name)) >= 1:
                        for file in Path(dir_to_find_year + name).rglob("*"):
                            if os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG"):
                                k = 1
                        if k == 1:
                            k = 0
                            dir_list.append(name)

            dir_list.sort(reverse=True)
            i = 0
            for year in dir_list:
                if dir_list[i] != "No_Date_Info":
                    self.date_year.addItem(str(year))
                else:
                    j = 1
                i += 1
            if j == 1:
                self.date_year.addItem("No_Date_Info")
            else:
                pass
            self.date_year.addItem("All")

        def get_months() -> None:
            """
            Получение месяцев в году
            """
            self.date_month.clear()
            year = self.date_year.currentText()
            if year == "All":
                self.date_month.addItem("All")
            else:
                dir_to_find_month = Settings.get_destination_media() + "/Media/Photo/const/" + year + "/"
                all_files_and_dirs = os.listdir(dir_to_find_month)
                dir_list = list()
                k = 0
                for name in all_files_and_dirs:
                    if os.path.isdir(dir_to_find_month + name):
                        if len(os.listdir(dir_to_find_month + name)) >= 1:
                            for file in Path(dir_to_find_month + name).rglob("*"):
                                if os.path.isfile(file) and str(file).endswith(".jpg") or str(file).endswith(".JPG"):
                                    k = 1
                            if k == 1:
                                k = 0
                                dir_list.append(name)

                dir_list.sort(reverse=True)
                for month in dir_list:
                    self.date_month.addItem(str(month))
                self.date_month.addItem("All")

        def get_days() -> None:
            """
            Получение дней в месяце
            """
            self.date_day.clear()
            year = self.date_year.currentText()
            month = self.date_month.currentText()
            if year == "All" or month == "All":
                self.date_day.addItem("All")
            else:
                dir_to_find_day = Settings.get_destination_media() + "/Media/Photo/const/" + year + "/" + month + "/"
                all_files_and_dirs = os.listdir(dir_to_find_day)
                dir_list = list()
                for name in all_files_and_dirs:
                    if os.path.isdir(dir_to_find_day + name):
                        if len(os.listdir(dir_to_find_day + name)) >= 1:
                            dir_list.append(name)

                dir_list.sort(reverse=True)
                for day in dir_list:
                    self.date_day.addItem(str(day))
                self.date_day.addItem("All")

        match mode:
            case "date":
                get_years()
                get_months()
                get_days()
            case "year":
                get_years()
            case "month":
                get_months()
            case "day":
                get_days()
            case _:
                get_years()
                get_months()
                get_days()

    def fill_sort_groupbox(self) -> None:
        """
        Выбор способа группировки
        """
        self.group_type = QComboBox(self)
        self.group_type.addItem("")
        self.group_type.addItem("Дата")
        self.group_type.addItem("Оборудование")
        self.group_type.setObjectName("sort")
        self.group_type.currentTextChanged.connect(self.set_sort_layout)
        self.group_type.setFont(font14)
        self.group_type.setFixedWidth(int(152 * system_scale) + 1)
        self.group_type.setFixedHeight(int(30 * system_scale) + 1)
        self.group_type.setStyleSheet(stylesheet9)

        self.layout_type.addWidget(self.group_type, 0, 0, 1, 1)

    def set_sort_layout(self) -> None:
        """
        Заполнить нужное поле в зависимости от выбранного типа группировки
        """
        for i in reversed(range(self.layout_type.count())):
            if self.layout_type.itemAt(i).widget().objectName() != "sort":
                self.layout_type.itemAt(i).widget().hide()
                self.layout_type.itemAt(i).widget().deleteLater()
                QtCore.QCoreApplication.processEvents()

        match self.group_type.currentText():
            case "Дата":
                self.fill_sort_date()
            case "Оборудование":
                self.fill_sort_equipment()
            case _:
                self.fill_sort_nothing()

    def fill_sort_nothing(self):
        """
        Очистка полей группировки
        """
        for i in reversed(range(self.layout_type.count())):
            if self.layout_type.itemAt(i).widget().objectName() != "sort":
                self.layout_type.itemAt(i).widget().hide()
                self.layout_type.itemAt(i).widget().deleteLater()
                QtCore.QCoreApplication.processEvents()

    def fill_sort_date(self) -> None:
        """
        Заполнить поле группировки по дате
        """
        year_lbl = QLabel(self)
        year_lbl.setFont(font14)
        year_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(year_lbl, 0, 1, 1, 1)

        self.date_year = QComboBox(self)
        self.date_year.setStyleSheet(stylesheet9)
        self.date_year.setFont(font14)
        self.date_year.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_year.setFixedWidth(int(140 * system_scale) + 1)
        self.layout_type.addWidget(self.date_year, 0, 2, 1, 1)

        month_lbl = QLabel(self)
        month_lbl.setFont(font14)
        month_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(month_lbl, 0, 3, 1, 1)

        self.date_month = QComboBox(self)
        self.date_month.setFont(font14)
        self.date_month.setStyleSheet(stylesheet9)
        self.date_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_month.setFixedWidth(int(140 * system_scale) + 1)
        self.layout_type.addWidget(self.date_month, 0, 4, 1, 1)

        day_lbl = QLabel(self)
        day_lbl.setFont(font14)
        day_lbl.setStyleSheet(stylesheet2)
        self.layout_type.addWidget(day_lbl, 0, 5, 1, 1)

        self.date_day = QComboBox(self)
        self.date_day.setFont(font14)
        self.date_day.setStyleSheet(stylesheet9)
        self.date_day.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.date_day.setFixedWidth(int(140 * system_scale) + 1)
        self.layout_type.addWidget(self.date_day, 0, 6, 1, 1)

        self.fill_date("date")

        if not year_lbl.text():
            year_lbl.setText("Год:")
            month_lbl.setText("    Месяц:")
            day_lbl.setText("    День:")

        self.date_day.setFixedHeight(int(30 * system_scale) + 1)
        self.date_month.setFixedHeight(int(30 * system_scale) + 1)
        self.date_year.setFixedHeight(int(30 * system_scale) + 1)
        day_lbl.setFixedHeight(30)
        month_lbl.setFixedHeight(30)
        year_lbl.setFixedHeight(30)

        self.date_year.currentTextChanged.connect(lambda: self.fill_date("month"))
        self.date_month.currentTextChanged.connect(lambda: self.fill_date("day"))

    def fill_sort_equipment(self) -> None:
        """
        Заполнить поле группировки по оборудованию
        """
        self.camera_choose = QComboBox(self)
        self.camera_choose.setFont(font14)
        self.camera_choose.setFixedHeight(int(30 * system_scale) + 1)
        self.camera_choose.setStyleSheet(stylesheet9)
        self.lens_choose = QComboBox(self)
        self.lens_choose.setFont(font14)
        self.lens_choose.setFixedHeight(int(30 * system_scale) + 1)
        self.lens_choose.setStyleSheet(stylesheet9)
        self.layout_type.addWidget(self.camera_choose, 0, 1, 1, 1)
        self.layout_type.addWidget(self.lens_choose, 0, 2, 1, 1)

        cameras, lenses = PhotoDataDB.get_equipment()
        camera_max_len = 0
        lens_max_len = 0

        for camera in cameras:
            self.camera_choose.addItem(f"{camera}")
            if len(camera) > camera_max_len:
                camera_max_len = len(camera)
        self.camera_choose.addItem("All")

        for lens in lenses:
            self.lens_choose.addItem(f"{lens}")
            if len(lens) > lens_max_len:
                lens_max_len = len(lens)
        self.lens_choose.addItem("All")

        self.camera_choose.setFixedWidth(int((camera_max_len * 12) * system_scale) + 1)
        self.lens_choose.setFixedWidth(int((lens_max_len * 12) * system_scale) + 1)


class HoursLooter(QtCore.QThread):
    """
    Сбор статистики по времени съёмки (часовой интервал в сутках)
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.hours_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
                           14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0}

    def run(self):
        for file in self.all_files:
            try:
                hour = piexif.load(file)["Exif"][36867].decode("utf-8")[-8:-6]
                self.hours_dict[int(hour)] += 1
            except (ValueError, KeyError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            hour_exif = et.execute("-EXIF:DateTimeOriginal", file)
                            if hour_exif:
                                try:
                                    hour = int(hour_exif.split(":")[-2])
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
            self.changed.emit(1)

        self.finished.emit(self.hours_dict)


class CameraLooter(QtCore.QThread):
    """
    Сбор статистики по камерам
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.camera_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                camera = piexif.load(file)["0th"][272].decode("utf-8")
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
                                camera = camera_exif.split(":")[-1]
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
            self.changed.emit(1)

        result = {}
        for camera in list(self.camera_dict.keys()):
            if camera in list(result.keys()):
                pass
            else:
                mutex.lock()
                normname = MetadataPhoto.equip_solo_name_check(camera, "camera")
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
    """
    Сбор статистики по объективам
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.lens_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                lens = piexif.load(file)["Exif"][42036].decode("utf-8")
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
                                lens = lens_exif.split(":")[-1]
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
            self.changed.emit(1)

        result = {}
        for lens in list(self.lens_dict.keys()):
            if lens in list(result.keys()):
                pass
            else:
                mutex.lock()
                normname = MetadataPhoto.equip_solo_name_check(lens, "lens")
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
    """
    Сбор статистики по светочувтвительности ISO
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.iso_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                iso = piexif.load(file)["Exif"][34855]
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
                                    iso = int(iso_exif.split(":")[-1])
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
            self.changed.emit(1)

        result = dict(sorted(self.iso_dict.items()))

        self.finished.emit(result)


class FnumberLooter(QtCore.QThread):
    """
    Сбор статистики значения диафрагмы
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.fnumber_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                fnumber = piexif.load(file)["Exif"][33437][0]/piexif.load(file)["Exif"][33437][1]
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
                                    fnumber = float(fnumber_exif.split(":")[-1])
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
            self.changed.emit(1)

        result = dict(sorted(self.fnumber_dict.items()))

        self.finished.emit(result)
        

class ExposureTimeLooter(QtCore.QThread):
    """
    Сбор статистики выдержки
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.time_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                time = piexif.load(file)["Exif"][33434][0]/piexif.load(file)["Exif"][33434][1]
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
            except (KeyError, ValueError, ZeroDivisionError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            time_exif = et.execute("-EXIF:ExposureTime", file)
                            if time_exif:
                                try:
                                    time_raw = float(time_exif.split(":")[-1])
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
            self.changed.emit(1)

        result = dict(sorted(self.time_dict.items()))

        self.finished.emit(result)


class FocalLengthLooter(QtCore.QThread):
    """
    Сбор статистики фокусного расстояния
    """
    finished = QtCore.pyqtSignal(dict)
    changed = QtCore.pyqtSignal(int)

    def __init__(self, files):
        QThread.__init__(self)
        self.all_files = files
        self.fl_dict = {}

    def run(self):
        for file in self.all_files:
            try:
                fl = piexif.load(file)["Exif"][37386][0]/piexif.load(file)["Exif"][37386][1]
                if fl:
                    try:
                        self.fl_dict[fl] += 1
                    except KeyError:
                        self.fl_dict[fl] = 1
            except (KeyError, ValueError, ZeroDivisionError) as error:
                if type(error) == ValueError:
                    try:
                        with exiftool.ExifToolHelper() as et:
                            fl_exif = et.execute("-EXIF:FocalLength", file)
                            if fl_exif:
                                try:
                                    fl = int(fl_exif.split(":")[-1])
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
            self.changed.emit(1)

        result = dict(sorted(self.fl_dict.items()))

        self.finished.emit(result)


class FilesPaths(QtCore.QThread):
    """
    Сбор всех путей файлов, подходящих под выбранную группу
    """
    files = QtCore.pyqtSignal(list)

    def __init__(self, type_filter="", arg1="All", arg2="All", arg3="All"):
        QThread.__init__(self)
        self.type_filter = type_filter
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def run(self):
        if self.type_filter == "Дата":
            year = self.arg1
            month = self.arg2
            day = self.arg3
            photo_list = PhotoDataDB.get_date_photo_list(year, month, day, False, "")
            result = photo_list
        elif self.type_filter == "Оборудование":
            camera = self.arg1
            lens = self.arg2
            if camera == "All":
                camera_exif = "All"
            else:
                camera_exif = MetadataPhoto.equip_name_check_reverse(camera, "camera")

            if lens == "All":
                lens_exif = "All"
            else:
                lens_exif = MetadataPhoto.equip_name_check_reverse(lens, "lens")
            photo_list = PhotoDataDB.get_equip_photo_list(camera_exif, camera, lens_exif, lens, False, "")
            result = photo_list
        else:   # if not filter
            all_files = []
            main_catalog = Settings.get_destination_media() + r"/Media/Photo/const"
            for root, dirs, files in os.walk(main_catalog):
                for file in files:
                    if file.endswith(".jpg") or file.endswith(".JPG"):
                        root_name = str(root)
                        root_name = root_name.replace(r"\\", "/")
                        root_name = root_name.replace("\\", "/")
                        root_name = root_name.replace("//", "/")
                        name = root_name + "/" + file
                        all_files.append(name)
            result = all_files

        self.files.emit(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StatisticsWin()
    win.show()
    sys.exit(app.exec_())
