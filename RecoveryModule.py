import os
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread, pyqtSignal

import Settings
import SynhronizeDBMedia


stylesheet1 = str()
stylesheet2 = str()
stylesheet8 = str()
loading_icon = str()


font14 = QtGui.QFont('Times', 14)


# объект окна настроек
class RecoveryWin(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheet_color()
        # Создание окна
        self.setWindowTitle('Восстановление')
        self.setStyleSheet(stylesheet2)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        recovery = RecoveryWidget(self)
        self.setCentralWidget(recovery)
        self.resize(recovery.size())

    # задать стили для всего модуля в зависимости от выбранной темы
    def stylesheet_color(self) -> None:
        global stylesheet1
        global stylesheet2
        global stylesheet8
        global loading_icon

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
            loading_icon = os.getcwd() + '/icons/loading_light.gif'
        else:  # Settings.get_theme_color() == 'dark'
            stylesheet1 =   """
                                border: 1px;
                                border-color: #696969;
                                border-style: solid;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            """
            stylesheet2 =   """
                                border: 0px;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            """
            stylesheet8 =   """
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
            loading_icon = os.getcwd() + '/icons/loading_dark.gif'

        try:
            self.setStyleSheet(stylesheet2)
            self.centralWidget().make_gui()
        except AttributeError:
            pass


# сам виджет со всем GUI
class RecoveryWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(stylesheet2)
        self.setWindowTitle('Восстановление')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.make_gui()

        self.resize(800, 220)

    def make_gui(self):
        self.lbl_len_photos = QLabel(self)
        self.lbl_len_photos.setText("Записей в таблице данных о фотографиях:")
        self.lbl_len_photos.setFont(font14)
        self.lbl_len_photos.setStyleSheet(stylesheet2)

        self.lbl_len_socnets = QLabel(self)
        self.lbl_len_socnets.setText("Записей в таблице о социальных сетях:")
        self.lbl_len_socnets.setFont(font14)
        self.lbl_len_socnets.setStyleSheet(stylesheet2)

        self.lbl_err_photos = QLabel(self)
        self.lbl_err_photos.setText("Обнаружено ошибок в таблице данных о фотографиях:")
        self.lbl_err_photos.setFont(font14)
        self.lbl_err_photos.setStyleSheet(stylesheet2)
        self.lbl_err_photos.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_err_socnets = QLabel(self)
        self.lbl_err_socnets.setText("Обнаружено ошибок в таблице о социальных сетях:")
        self.lbl_err_socnets.setFont(font14)
        self.lbl_err_socnets.setStyleSheet(stylesheet2)
        self.lbl_err_socnets.setAlignment(QtCore.Qt.AlignRight)

        self.lbl_len_exists = QLabel(self)
        self.lbl_len_exists.setText("Фотографий в папке хранения:")
        self.lbl_len_exists.setFont(font14)
        self.lbl_len_exists.setStyleSheet(stylesheet2)

        self.lbl_len_thumbs = QLabel(self)
        self.lbl_len_thumbs.setText("Миниатюр в папке хранения:")
        self.lbl_len_thumbs.setFont(font14)
        self.lbl_len_thumbs.setStyleSheet(stylesheet2)

        self.len_photos_value = QLineEdit(self)
        self.len_photos_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[0])))
        self.len_photos_value.setDisabled(True)
        self.len_photos_value.setFont(font14)
        self.len_photos_value.setStyleSheet(stylesheet1)

        self.len_socnets_value = QLineEdit(self)
        self.len_socnets_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[1])))
        self.len_socnets_value.setDisabled(True)
        self.len_socnets_value.setFont(font14)
        self.len_socnets_value.setStyleSheet(stylesheet1)

        self.err_photos_value = QLineEdit(self)
        self.err_photos_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[0]))
        self.err_photos_value.setDisabled(True)
        self.err_photos_value.setFont(font14)
        self.err_photos_value.setStyleSheet(stylesheet1)

        self.err_socnets_value = QLineEdit(self)
        self.err_socnets_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[1]))
        self.err_socnets_value.setDisabled(True)
        self.err_socnets_value.setFont(font14)
        self.err_socnets_value.setStyleSheet(stylesheet1)

        self.len_exists_value = QLineEdit(self)
        self.len_exists_value.setText(str(len(SynhronizeDBMedia.research_all_media_photos())))
        self.len_exists_value.setDisabled(True)
        self.len_exists_value.setFont(font14)
        self.len_exists_value.setStyleSheet(stylesheet1)

        self.len_thumbs_value = QLineEdit(self)
        self.len_thumbs_value.setText(str(len(SynhronizeDBMedia.research_all_thumbnails())))
        self.len_thumbs_value.setDisabled(True)
        self.len_thumbs_value.setFont(font14)
        self.len_thumbs_value.setStyleSheet(stylesheet1)

        self.layout.addWidget(self.lbl_len_photos, 0, 0, 1, 1)
        self.layout.addWidget(self.len_photos_value, 0, 1, 1, 1)
        self.layout.addWidget(self.lbl_len_socnets, 1, 0, 1, 1)
        self.layout.addWidget(self.len_socnets_value, 1, 1, 1, 1)
        self.layout.addWidget(self.lbl_err_photos, 0, 2, 1, 1)
        self.layout.addWidget(self.err_photos_value, 0, 3, 1, 1)
        self.layout.addWidget(self.lbl_err_socnets, 1, 2, 1, 1)
        self.layout.addWidget(self.err_socnets_value, 1, 3, 1, 1)
        self.layout.addWidget(self.lbl_len_exists, 2, 0, 1, 1)
        self.layout.addWidget(self.len_exists_value, 2, 1, 1, 1)
        self.layout.addWidget(self.lbl_len_thumbs, 3, 0, 1, 1)
        self.layout.addWidget(self.len_thumbs_value, 3, 1, 1, 1)

        self.btn_recovery = QPushButton(self)
        self.btn_recovery.setText("Запустить восстановление")
        self.btn_recovery.setFont(font14)
        self.btn_recovery.setStyleSheet(stylesheet8)
        self.btn_recovery.clicked.connect(self.do_recovery_func)
        self.layout.addWidget(self.btn_recovery, 10, 0, 1, 1)

    # выполнение восстановления
    def do_recovery_func(self) -> None:
        self.loading_win = RecoveryLoadingWin(self)
        self.proccess = DoRecovery()
        self.proccess.finished.connect(self.loading_win.close)
        self.proccess.loading_text_show.connect(lambda t: self.loading_win.set_process_lbl(t))
        self.proccess.finished.connect(self.update_values)
        self.loading_win.show()
        self.proccess.start()

    # обновить GUI по завершении восстановления
    def update_values(self) -> None:
        self.len_photos_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[0])))
        self.len_socnets_value.setText(str(len(SynhronizeDBMedia.get_all_db_ways()[1])))
        self.err_photos_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[0]))
        self.err_socnets_value.setText(str(SynhronizeDBMedia.check_destination_corr_db()[1]))
        self.len_exists_value.setText(str(len(SynhronizeDBMedia.research_all_media_photos())))
        self.len_thumbs_value.setText(str(len(SynhronizeDBMedia.research_all_thumbnails())))
        self.proccess = None


# тупа анимация загрузки с надписью
class RecoveryLoadingWin(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.setWindowTitle('Загрузка')

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.label = QLabel(self)
        self.text = QLabel(self)
        self.text.setText('Загрузка, подождите')
        self.text.setStyleSheet(stylesheet2)
        self.text.setFont(font14)
        self.movie = QMovie(loading_icon)
        self.label.setMovie(self.movie)
        self.label.setStyleSheet(stylesheet2)
        self.movie.start()

        self.process_lbl = QLabel(self)
        self.layout.addWidget(self.process_lbl, 1, 0, 1, 2)

        self.layout.addWidget(self.text, 0, 0, 1, 1)
        self.layout.addWidget(self.label, 0, 1, 1, 1)

        self.resize(300, 100)

    def set_process_lbl(self, text):
        self.process_lbl.setText(f"{text}")


# непосредственно восстановление
class DoRecovery(QtCore.QThread):
    loading_text_show = pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self._init = False

    def run(self):
        self.loading_text_show.emit("Получение информации из базы данных")
        all_photos_db, all_socnets_db = SynhronizeDBMedia.get_all_db_ways()
        self.loading_text_show.emit("Проверка существования файлов, записанных в базе данных")
        SynhronizeDBMedia.check_exists_from_db(all_photos_db, all_socnets_db)
        self.loading_text_show.emit("Получение списка файлов из директории хранения")
        filelist_exist = SynhronizeDBMedia.research_all_media_photos()
        self.loading_text_show.emit("Добавление в базу данных недостающих записей")
        SynhronizeDBMedia.add_flaw_to_db(filelist_exist)
        self.loading_text_show.emit("Синхронизация фотографий и миниатюр")
        SynhronizeDBMedia.thumbnail_photo_conformity()
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RecoveryWin()
    win.show()
    sys.exit(app.exec_())

