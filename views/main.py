import math

import pathfinder as pf

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap

from views.map import Map
from views.chart import Chart
from views.waypoint import WaypointWidget

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
        self.chart.setup_legend(
            self.home_button,
            self.left_profile_checkbox,
            self.right_profile_checkbox,
            self.middle_profile_checkbox,
            self.pos_profile_checkbox,
            self.vel_profile_checkbox,
            self.accel_profile_checkbox,
            self.x_scale_slider,
            self.y_scale_slider,
            self.x_scale_label,
            self.y_scale_label,
            self.cursor_val_label
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

        self.add_button.clicked.connect(self.add_waypoint)
        self.waypoint_table.setColumnCount(3)
        self.waypoint_table.setHorizontalHeaderLabels(("X", "Y", "Angle"))
        self.waypoint_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.waypoint_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.waypoint_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.waypoint_table.itemChanged.connect(self.update_from_table)

        self.export_button.clicked.connect(self.export)

        self.show()

    def export(self):
        

    def add_waypoint(self, x=0, y=0, angle=0):
        pnt = pf.Waypoint(x, y, angle)
        self.map.points.append(pnt)
        self.waypoint_table.setRowCount(len(self.map.points))
        self.update_waypoints()

    def update_waypoints(self):
        for i in range(len(self.map.points)):
            pnt = self.map.points[i]
            self.waypoint_table.setItem(i, 0, QTableWidgetItem(str(round(pnt.x, 2))))
            self.waypoint_table.setItem(i, 1, QTableWidgetItem(str(round(pnt.y, 2))))
            self.waypoint_table.setItem(i, 2, QTableWidgetItem(str(round(((math.pi * 2) - pnt.angle) % (math.pi * 2) * (180 / math.pi), 2))))

    def update_from_table(self, item):
        pnt = self.map.points[item.row()]
        col = row = item.column()
        if col == 0:
            pnt.x = float(item.text())
        if col == 1:
            pnt.y = float(item.text())
        if col == 2:
            pnt.angle = abs(float(item.text()) / (180 / math.pi) - 2 * math.pi)

    def paintEvent(self, event):
        if self.map.paint():
            self.update_waypoints()
        self.chart.paint()
