import math

import pathfinder as pf

from PyQt5.QtCore import Qt, QRect, QLine
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPixmap, QCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication, QLabel

class Chart(QLabel):
    def __init__(self, parent, legend_info):
        super().__init__(parent)
        self.parent = parent
        self.legend_info = legend_info
        self.setFixedSize(self.parent.size())
        self.axis_rect = QRect(60, 15, self.width() - 85, self.height() - 60)
        self.drag_offset = [0, 0]
        self.last_profile = None
        self.profile = None
        self.left_profile = None
        self.right_profile = None
        self.last_move_point = None
        self.x_scale = 1
        self.y_scale = 1
        self.x_min = 0
        self.x_max = 5
        self.y_min = 0
        self.y_max = 10

    def reset(self):
        self.drag_offset = [0, 0]
        self.last_profile = None
        self.profile = None
        self.left_profile = None
        self.right_profile = None
        self.last_move_point = None
        self.x_scale = 1
        self.y_scale = 1
        self.x_min = 0
        self.x_max = 5
        self.y_min = 0
        self.y_max = 10
        pixmap = QPixmap(self.size())
        pixmap.fill(QColor(0, 0, 0, 0))
        self.setPixmap(pixmap)

    def setup_legend(self, home_button, first_box, second_box, main_box, pos_box, vel_box, accel_box, x_slider, y_slider, x_slider_label, y_slider_label, curor_val_label):
        self.home_button = home_button
        self.home_button.clicked.connect(self.reset_view)
        self.first_box = first_box
        self.main_box = main_box
        self.second_box = second_box
        self.pos_box = pos_box
        self.vel_box = vel_box
        self.accel_box = accel_box
        self.x_slider = x_slider
        self.y_slider = y_slider
        self.x_slider_label = x_slider_label
        self.y_slider_label = y_slider_label
        self.curor_val_label = curor_val_label

    def mousePressEvent(self, QMouseEvent):
        self.last_move_point = QMouseEvent.pos()

    def mouseMoveEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        self.drag_offset[0] += pos.x() - self.last_move_point.x()
        self.drag_offset[1] += pos.y() - self.last_move_point.y()
        self.last_move_point = pos

        label = "x:{} y:{}".format(*[round(e, 1) for e in self.convert_gui_point_to_chart_point(pos.x(), pos.y())])
        self.curor_val_label.setText(label)
        self.curor_val_label.repaint()

    def setProfiles(self, profile, left_profile, right_profile):
        self.profile = profile
        self.left_profile = left_profile
        self.right_profile = right_profile

    def reset_view(self):
        self.drag_offset = [0, 0]
        self.x_slider.setValue(10)
        self.y_slider.setValue(10)

    def paint(self, force=False):
        pos = self.mapFromGlobal(QCursor.pos())
        if pos.x() > self.x() and pos.x() < self.x() + self.width() and pos.y() > self.y() and pos.y() < self.y() + self.height():
            label = "x:{} y:{}".format(*[round(e, 1) for e in self.convert_gui_point_to_chart_point(pos.x(), pos.y())])
            self.curor_val_label.setText(label)

        if self.profile is self.last_profile and not False:
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

        x_slider_scale = self.x_slider.value() / 10
        y_slider_scale = self.y_slider.value() / 10
        self.x_slider_label.setText(str(round(x_slider_scale, 1)))
        self.y_slider_label.setText(str(round(y_slider_scale, 1)))

        if abs(self.drag_offset[0]) / x_slider_scale > self.axis_rect.width():
            self.drag_offset[0] = self.axis_rect.width() * x_slider_scale * (1 if self.drag_offset[0] >= 0 else -1)
        if abs(self.drag_offset[1]) / y_slider_scale > self.axis_rect.height():
            self.drag_offset[1] = self.axis_rect.height() * y_slider_scale * (1 if self.drag_offset[1] >= 0 else -1)

        self.num_x_ticks = 10
        self.num_y_ticks = 10
        self.x_min = 0
        self.x_max = len(self.left_profile) * self.left_profile[0].dt
        self.x_scale = self.axis_rect.width() / (self.x_max - self.x_min) * x_slider_scale

        profiles = []
        if self.first_box.isChecked():
            profiles += self.left_profile
        if self.second_box.isChecked():
            profiles += self.right_profile
        if self.main_box.isChecked():
            profiles += self.profile
        y_vals = []
        if self.accel_box.isChecked():
            y_vals.append([e.acceleration for e in profiles])
        if self.vel_box.isChecked():
            y_vals.append([e.velocity for e in profiles])
        if self.pos_box.isChecked():
            y_vals.append([e.position for e in profiles])
        if not y_vals:
            return
        self.y_min = min([min(e) for e in y_vals])
        self.y_max = max([max(e) for e in y_vals])

        self.y_scale = self.axis_rect.height() / (self.y_max - self.y_min) * y_slider_scale

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
            *self.convert_chart_point_to_gui_point(0, 0, offset_x=False),
            *self.convert_chart_point_to_gui_point(self.x_max, 0, offset_x=False)
        )  # Draw 0 line
        x_tick_rate = self.axis_rect.width() / self.num_x_ticks
        for i in range(0, self.num_x_ticks + 1):  # Draw x ticks
            x = self.axis_rect.x() + i * x_tick_rate
            y = self.axis_rect.y() + self.axis_rect.height()
            label = str(round(i * x_tick_rate / self.x_scale - self.drag_offset[0] / self.x_scale - self.x_min, 2))
            temp_pen = QPen(pen)
            temp_pen.setColor(QColor(50, 50, 50, 50))
            qp.setPen(temp_pen)
            qp.drawLine(x, self.y(), x, self.y() + self.height())
            qp.setPen(pen)
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
            label = str(round((i * y_tick_rate + self.drag_offset[1]) / self.y_scale + self.y_min, 1))
            temp_pen = QPen(pen)
            temp_pen.setColor(QColor(50, 50, 50, 50))
            qp.setPen(temp_pen)
            qp.drawLine(self.x(), y, self.x() + self.width(), y)
            qp.setPen(pen)
            qp.drawLine(x-5, y, x, y)
            qp.drawText(QRect(x-50, y-7, 40, 15), Qt.AlignRight, label);


        # Draw Data

        get_val = [
            lambda e: e.position,
            lambda e: e.velocity,
            lambda e: e.acceleration
        ]

        pen = QPen()
        pen.setWidth(2)
        keys = ['first', 'second', 'main']
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


    def convert_chart_point_to_gui_point(self, x, y, offset_x=True, offset_y=True):
        x = (x - self.x_min) * self.x_scale + self.axis_rect.x() + (self.drag_offset[0] if offset_x else 0)
        y = self.axis_rect.height() + self.axis_rect.y() - ((y - self.y_min) * self.y_scale) + (self.drag_offset[1] if offset_y else 0)
        return x, y

    def convert_gui_point_to_chart_point(self, x, y, offset_x=True, offset_y=True):
        x = (x - (self.drag_offset[0] if offset_x else 0) - self.axis_rect.x()) / self.x_scale + self.x_min
        y = -(y - (self.drag_offset[1] if offset_y else 0) - self.axis_rect.height() - self.axis_rect.y()) / self.y_scale + self.y_min
        return x, y

