import os
import json
import math
import copy

import pathfinder as pf

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QCursor, QPixmap

from views.map import Map
from views.chart import Chart

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainView.ui', self)
        self.setFixedSize(self.size())

        self.legend_info = {
            'middle': {
                'color': QColor(50, 220, 50)
            },
            'left': {
                'color': QColor(220, 50, 50)
            },
            'right': {
                'color': QColor(50, 50, 220)
            },
            'pos': {
                'style': Qt.SolidLine
            },
            'vel': {
                'style': Qt.DashLine
            },
            'accel': {
                'style': Qt.DotLine
            }
        }

        self.chart = Chart(self.chart_label, self.legend_info)
        self.chart.setup_legend_boxes(
            self.left_profile_checkbox,
            self.right_profile_checkbox,
            self.middle_profile_checkbox,
            self.pos_profile_checkbox,
            self.vel_profile_checkbox,
            self.accel_profile_checkbox
        )
        self.map = Map(self.background_label, self.chart, self.legend_info)

        for path in ['left', 'right', 'middle']:
            label = eval("self." + path + "_line_label")
            pixmap = QPixmap(label.size())
            pixmap.fill(self.legend_info[path]['color'])
            label.setPixmap(pixmap)

        pen = QPen()
        pen.setColor(QColor(50, 50, 50))
        pen.setWidth(4)
        for val in ['pos', 'vel', 'accel']:
            label = eval("self." + val + "_line_label")
            pixmap = QPixmap(label.size())
            pixmap.fill(QColor(0, 0, 0, 0))
            qp = QPainter(pixmap)
            pen.setStyle(self.legend_info[val]['style'])
            qp.setPen(pen)
            qp.drawLine(0, pixmap.height() / 2, pixmap.width(), pixmap.height() / 2)
            qp.end()
            label.setPixmap(pixmap)

        self.show()

    def paintEvent(self, event):
        self.map.paint()
        self.chart.paint()
