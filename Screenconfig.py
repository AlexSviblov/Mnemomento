import ctypes
import os
from PyQt5 import QtGui

font16 = QtGui.QFont('Times', 16)
font14 = QtGui.QFont('Times', 14)
font12 = QtGui.QFont('Times', 12)
font10 = QtGui.QFont('Times', 10)
font8 = QtGui.QFont('Times', 8)
font6 = QtGui.QFont('Times', 6)

stylesheet1_light = """
                    border: 1px;
                    border-color: #A9A9A9;
                    border-style: solid;
                    color: #000000;
                    background-color: #F0F0F0
                """
stylesheet2_light = """
                    border: 0px;
                    color: #000000;
                    background-color: #F0F0F0
                """
stylesheet3_light = """
                    QHeaderView::section
                    {
                        border: 1px;
                        border-color: #A9A9A9;
                        border-style: solid;
                        background-color: #F0F0F0;
                        color: #000000;
                    }
                """
stylesheet4_light = """
                            QMenuBar 
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            }
                            QMenuBar::item::selected
                            {
                                color: #000000;
                                background-color: #C0C0C0
                            }
                        """
stylesheet5_light = """
                               QProgressBar
                               {
                                   border: 1px;
                                   border-color: #000000;
                                   border-style: solid;
                                   background-color: #FFFFFF;
                                   color: #000000
                               }
                               QProgressBar::chunk
                               {
                                   background-color: #00FF7F;  
                               }
                           """
stylesheet6_light = """
                    QTableView
                    {
                        border: 1px;
                        border-color: #A9A9A9;
                        border-style: solid;
                        color: #000000;
                        background-color: #F0F0F0;
                        gridline-color: #A9A9A9;
                    }
                """
stylesheet7_light = """
                QTabWidget::pane
                {
                    border: 1px;
                    border-color: #A9A9A9;
                    border-style: solid;
                    background-color: #F0F0F0;
                    color: #000000;
                }
                QTabBar::tab
                {
                    border: 1px;
                    border-color: #A9A9A9;
                    border-style: solid;
                    padding: 5px;
                    color: #000000;
                    min-width: 12em;
                }
                QTabBar::tab:selected
                {
                    border: 2px;
                    border-color: #A9A9A9;
                    border-style: solid;
                    margin-top: -1px;
                    background-color: #C0C0C0;
                    color: #000000;
                }
                """
stylesheet8_light = """
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
stylesheet9_light = """
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
stylesheet10_light = """
                            QMenu
                            {
                                border: 1px;
                                border-color: #A9A9A9;
                                border-style: solid;
                                color: #000000;
                                background-color: #F0F0F0
                            }
                            QMenu::item::selected
                            {
                                border: 2px;
                                background-color: #C0C0C0;
                            }
                            """
stylesheet11_light = """
                                QTableWidget
                                {
                                    border: 1px;
                                    border-color: #A9A9A9;
                                    border-style: solid;
                                    color: #000000;
                                    background-color: #F0F0F0;
                                    gridline-color: #A9A9A9;
                                }
                                QTableCornerButton::section 
                                {
                                    background-color: #F0F0F0;
                                }
                            """
icon_explorer_light = os.getcwd() + '/icons/explorer_light.png'
icon_view_light = os.getcwd() + '/icons/view_light.png'
icon_edit_light = os.getcwd() + '/icons/edit_light.png'
icon_delete_light = os.getcwd() + '/icons/delete_light.png'
loading_icon_light = os.getcwd() + '/icons/loading_light.gif'
statistics_text_color_light = "black"
statistics_plot_back_color_light = "white"
statistics_bar_time_color_light = "black"
statistics_bar_color_light = 'blue'
statistics_area_color_light = "#F4F4F4"

stylesheet1_dark = """
                    border: 1px;
                    border-color: #696969;
                    border-style: solid;
                    color: #D3D3D3;
                    background-color: #1C1C1C
                """
stylesheet2_dark = """
                    border: 0px;
                    color: #D3D3D3;
                    background-color: #1C1C1C
                """
stylesheet3_dark = """
                    QHeaderView::section
                    {
                        border: 1px;
                        border-color: #696969;
                        border-style: solid;
                        background-color: #1C1C1C;
                        color: #D3D3D3;
                    }
                """
stylesheet4_dark = """
                     QMenuBar 
                     {
                         border: 1px;
                         border-color: #696969;
                         border-style: solid;
                         color: #D3D3D3;
                         background-color: #1C1C1C
                     }
                     QMenuBar::item::selected
                     {
                         color: #D3D3D3;
                         background-color: #3F3F3F
                     }
                     """
stylesheet5_dark = """
                    QProgressBar
                    {
                        border: 1px;
                        border-color: #000000;
                        border-style: solid;
                        background-color: #CCCCCC;
                        color: #000000
                    }
                    QProgressBar::chunk
                    {
                        background-color: #1F7515;
                    }
                """
stylesheet6_dark = """
                    QTableView
                    {
                        border: 1px;
                        border-color: #696969;
                        border-style: solid;
                        color: #D3D3D3;
                        background-color: #1c1c1c;
                        gridline-color: #696969;
                    }
                """
stylesheet7_dark = """
                    QTabWidget::pane
                    {
                        border: 1px;
                        border-color: #696969;
                        border-style: solid;
                        color: #D3D3D3;
                        background-color: #1C1C1C;
                        color: #D3D3D3
                    }
                    QTabBar::tab
                    {
                        border: 1px;
                        border-color: #696969;
                        border-style: solid;
                        padding: 5px;
                        color: #D3D3D3;
                        min-width: 12em;
                    } 
                    QTabBar::tab:selected
                    {
                        border: 2px;
                        border-color: #6A6A6A;
                        border-style: solid;
                        margin-top: -1px;
                        background-color: #1F1F1F;
                        color: #D3D3D3
                    }
                """
stylesheet8_dark = """
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
stylesheet9_dark = """
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
stylesheet10_dark = """
                            QMenu
                            {
                                border: 1px;
                                border-color: #696969;
                                border-style: solid;
                                color: #D3D3D3;
                                background-color: #1C1C1C
                            }
                            QMenu::item::selected
                            {
                                border: 2px;
                                background-color: #2F2F2F;
                            }
                            """
stylesheet11_dark = """
                                QTableView
                                {
                                    border: 1px;
                                    border-color: #696969;
                                    border-style: solid;
                                    color: #D3D3D3;
                                    background-color: #1c1c1c;
                                    gridline-color: #696969;
                                }
                                QTableCornerButton::section 
                                {
                                    background-color: #1c1c1c;
                                }

                            """
icon_explorer_dark = os.getcwd() + '/icons/explorer_dark.png'
icon_view_dark = os.getcwd() + '/icons/view_dark.png'
icon_edit_dark = os.getcwd() + '/icons/edit_dark.png'
icon_delete_dark = os.getcwd() + '/icons/delete_dark.png'
loading_icon_dark = os.getcwd() + '/icons/loading_dark.gif'
statistics_text_color_dark = "white"
statistics_plot_back_color_dark = "#585858"
statistics_bar_time_color_dark = "yellow"
statistics_bar_color_dark = "#fff100"
statistics_area_color_dark = "#181818"

light_style = {'stylesheet1': stylesheet1_light,
               'stylesheet2': stylesheet2_light,
               'stylesheet3': stylesheet3_light,
               'stylesheet4': stylesheet4_light,
               'stylesheet5': stylesheet5_light,
               'stylesheet6': stylesheet6_light,
               'stylesheet7': stylesheet7_light,
               'stylesheet8': stylesheet8_light,
               'stylesheet9': stylesheet9_light,
               'stylesheet10': stylesheet10_light,
               'stylesheet11': stylesheet11_light,
               'icon_explorer': icon_explorer_light,
               'icon_view': icon_view_light,
               'icon_edit': icon_edit_light,
               'icon_delete': icon_delete_light,
               'loading_icon': loading_icon_light,
               'map_tiles': "OpenStreetMap",
               'statistics': {
                   'text_color': statistics_text_color_light,
                   'plot_back_color': statistics_plot_back_color_light,
                   'bar_time_color': statistics_bar_time_color_light,
                   'bar_color': statistics_bar_color_light,
                   'area_color': statistics_area_color_light
               }
               }

dark_style = {'stylesheet1': stylesheet1_dark,
              'stylesheet2': stylesheet2_dark,
              'stylesheet3': stylesheet3_dark,
              'stylesheet4': stylesheet4_dark,
              'stylesheet5': stylesheet5_dark,
              'stylesheet6': stylesheet6_dark,
              'stylesheet7': stylesheet7_dark,
              'stylesheet8': stylesheet8_dark,
              'stylesheet9': stylesheet9_dark,
              'stylesheet10': stylesheet10_dark,
              'stylesheet11': stylesheet11_dark,
              'icon_explorer': icon_explorer_dark,
              'icon_view': icon_view_dark,
              'icon_edit': icon_edit_dark,
              'icon_delete': icon_delete_dark,
              'loading_icon': loading_icon_dark,
              'map_tiles': "OpenStreetMap",
              'statistics': {
                  'text_color': statistics_text_color_dark,
                  'plot_back_color': statistics_plot_back_color_dark,
                  'bar_time_color': statistics_bar_time_color_dark,
                  'bar_color': statistics_bar_color_dark,
                  'area_color': statistics_area_color_dark
              }
              }

style_dict = {'light': light_style, 'dark': dark_style}


def monitor_info() -> tuple[tuple[int, int], float]:
    """
    """
    screen_size = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    return screen_size, scale_factor
