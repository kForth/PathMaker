import math

import pathfinder as pf

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QCursor, QPixmap

from views.map import Map
from views.chart import Chart

class WaypointWidget(QWidget):
    
    def __init__(self, waypoint):
        super().__init__()
        uic.loadUi('ui/Waypoint.ui', self)
        self.setFixedSize(self.size())
        self.waypoint = waypoint
        self.updateWaypoint()
        self.show()

    def updateWaypoint(self):
        print(self.waypoint)
        self.x_val_box.setValue(self.waypoint.x)
        self.y_val_box.setValue(self.waypoint.y)
        self.angle_val_box.setValue(((2 * math.pi) - self.waypoint.angle) % (2 * math.pi))

    def paintEvent(self, event):
        pass
        # self.updateWaypoint()