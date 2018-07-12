import math

import pathfinder as pf

from PyQt5.QtCore import Qt, QRect, QLine
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPixmap
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication, QLabel

class Chart(QLabel):
    def __init__(self, parent, legend_info):
        super().__init__(parent)
        self.parent = parent
        self.legend_info = legend_info
        self.setFixedSize(self.parent.size())
        self.axis_rect = QRect(50, 35, self.width() - 85, self.height() - 85)
        self.last_profile = None
        self.profile = None

    def setup_legend_boxes(self, left_box, right_box, middle_box, pos_box, vel_box, accel_box):
        self.left_box = left_box
        self.middle_box = middle_box
        self.right_box = right_box
        self.pos_box = pos_box
        self.vel_box = vel_box
        self.accel_box = accel_box

    def setProfiles(self, profile, left_profile, right_profile):
        self.profile = profile
        self.left_profile = left_profile
        self.right_profile = right_profile

    def paint(self):
        if self.profile is self.last_profile:
            return
        self.last_profile = list(self.profile)
        pixmap = QPixmap(self.size())
        pixmap.fill(QColor(0, 0, 0, 0))
        qp = QPainter()
        qp.begin(pixmap)

        pen = QPen()
        pen.setColor(QColor(50, 50, 50, 200))
        pen.setWidth(1.5)
        qp.setPen(pen)

        self.num_x_ticks = 10
        self.num_y_ticks = 10
        self.x_min = 0
        self.x_max = len(self.left_profile) * self.left_profile[0].dt
        self.x_scale = self.axis_rect.width() / (self.x_max - self.x_min)

        self.y_min = min([min(e.position, e.velocity, e.acceleration) for e in self.left_profile + self.right_profile])
        self.y_max = max([max(e.position, e.velocity, e.acceleration) for e in self.left_profile + self.right_profile])

        self.y_scale = self.axis_rect.height() / (self.y_max - self.y_min)

        qp.drawLine(
            self.axis_rect.x(), 
            self.axis_rect.y() + self.axis_rect.height(), 
            self.axis_rect.x() + self.axis_rect.width(), 
            self.axis_rect.y() + self.axis_rect.height()
        )  # Draw x axis
        qp.drawText(QRect(
            self.axis_rect.x() + self.axis_rect.width() / 2 - 50, 
            self.axis_rect.y() + self.axis_rect.height() + 25, 
            100, 15
        ), Qt.AlignCenter, "Time (s)");
        qp.drawLine(
            *self.convert_chart_point_to_gui_point(0, 0),
            *self.convert_chart_point_to_gui_point(self.x_max, 0)
        )  # Draw 0 line
        x_tick_rate = self.axis_rect.width() / self.num_x_ticks
        for i in range(0, self.num_x_ticks + 1):  # Draw x ticks
            x = self.axis_rect.x() + i * x_tick_rate
            y = self.axis_rect.y() + self.axis_rect.height()
            label = str(round(i * x_tick_rate / self.x_scale, 1))
            qp.drawLine(x, y, x, y + 5)
            qp.drawText(QRect(x - 15, y + 10, 30, 15), Qt.AlignCenter, label);

        qp.drawLine(
            self.axis_rect.x(), 
            self.axis_rect.y(), 
            self.axis_rect.x(), 
            self.axis_rect.y() + self.axis_rect.height()
        )  # Draw y axis
        y_tick_rate = round(self.axis_rect.height() / self.num_y_ticks)
        for i in range(0, self.num_y_ticks + 1):  # Draw y ticks
            x = self.axis_rect.x()
            y = self.axis_rect.y() + self.axis_rect.height() - i * y_tick_rate
            label = str(round(i * y_tick_rate / self.y_scale, 1))
            qp.drawLine(x-5, y, x, y)
            qp.drawText(QRect(x-40, y-7, 30, 15), Qt.AlignRight, label);


        # Draw Data

        get_val = [
            lambda e: e.position,
            lambda e: e.velocity,
            lambda e: e.acceleration
        ]

        pen = QPen()
        pen.setWidth(2)
        keys = ['left', 'right', 'middle']
        val_keys = ['pos', 'vel', 'accel']
        for p in range(len(keys)):
            if not eval("self." + keys[p] + "_box").isChecked():
                continue
            profile = [self.left_profile, self.right_profile, self.profile][p]
            pen.setColor(self.legend_info[keys[p]]['color'])
            for i in range(1, len(profile)):  # Draw points
                pnt = profile[i]
                pnt2 = profile[i-1]
                x = i * pnt.dt
                for j in range(len(val_keys)):
                    if not eval("self." + val_keys[j] + "_box").isChecked():
                        continue
                    pen.setStyle(self.legend_info[val_keys[j]]['style'])
                    qp.setPen(pen)
                    qp.drawLine(
                        *self.convert_chart_point_to_gui_point(x, get_val[j](pnt)),
                        *self.convert_chart_point_to_gui_point(x - pnt.dt, get_val[j](pnt2))
                    )

        qp.end()
        self.setPixmap(pixmap)


    def convert_chart_point_to_gui_point(self, x, y):
        x = (x - self.x_min) * self.x_scale + self.axis_rect.x()
        y = self.axis_rect.height() + self.axis_rect.y() - ((y - self.y_min) * self.y_scale)
        return x, y

