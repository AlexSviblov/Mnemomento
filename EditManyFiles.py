import os
import sys
import folium
import json
import math
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pathlib import Path

import PhotoDataDB
import Screenconfig
import Metadata
import Settings
import Thumbnail
import EditFiles


stylesheet1 = str()
stylesheet2 = str()
stylesheet3 = str()
stylesheet6 = str()
stylesheet7 = str()
stylesheet8 = str()
stylesheet9 = str()
icon_explorer = str()
icon_view = str()
icon_edit = str()
icon_delete = str()


font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)


class ManyPhotoEdit(QWidget):

    def __init__(self):
        super().__init__()

        self.layout_outside = QGridLayout(self)
        self.setLayout(self.layout_outside)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManyPhotoEdit()
    win.show()
    sys.exit(app.exec_())