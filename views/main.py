import os
import json
import math

from path import Path, Waypoint

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QCursor, QPixmap

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainView.ui', self)

        field_pixmap = QPixmap('img/powerup_field.png')
        self.background_label.setPixmap(field_pixmap.scaled(self.background_label.width(),self.background_label.height(), Qt.KeepAspectRatio))
        
        self.points = [
            Waypoint(0.6, 1.2, 0),
            Waypoint(4.2, 1.2, 0),
            Waypoint(6, 3, math.radians(90)),
            Waypoint(5.9, 15*0.3, math.radians(95)),
            Waypoint(24.5*0.3, 20.5*0.3, math.radians(-10))
        ]

        self.profile = Path(self.points, 0.6, d_t=0.1)
        self.profile.build_path()

        self.drag_mode = None
        self.point_being_dragged = None
        self.drag_offset = None
        self.ghost_point = None

        self.initUI()

    def _gui_point_to_path_point(self, x, y):
        pnt_scale = (self.canvas_label.size().height() - 30) / 8.2296
        x_offset = self.canvas_label.pos().x() + 33
        y_offset = self.canvas_label.pos().y() + 15
        return (x - x_offset) / pnt_scale, (y - y_offset) / pnt_scale

    def get_arm_gui_point(self, pnt):
        pnt_x, pnt_y = self.get_path_gui_point(pnt)
        return (pnt_x + math.cos(pnt.yaw) * 20), (pnt_y + math.sin(pnt.yaw) * 20)

    def get_path_gui_point(self, pnt):
        pnt_scale = (self.canvas_label.size().height() - 30) / 8.2296
        x_offset = self.canvas_label.pos().x() + 33
        y_offset = self.canvas_label.pos().y() + 15
        return pnt.x * pnt_scale + x_offset, pnt.y * pnt_scale + y_offset

    def get_closest_point(self, pos, min_dist=None):
        closest_pnt = None
        closest_dist = 1e10
        for pnt in self.points:
            pnt_x, pnt_y = self.get_path_gui_point(pnt)
            dist = math.sqrt((pnt_y - pos.y())**2 + (pnt_x - pos.x())**2)
            if dist < closest_dist and (min_dist is None or dist < min_dist):
                closest_pnt = pnt
        return closest_pnt

    def get_closest_arm(self, pos, min_dist=None):
        closest_pnt = None
        closest_dist = 1e10
        for pnt in self.points:
            pnt_x, pnt_y = self.get_path_gui_point(pnt)
            arm_x, arm_y = self.get_arm_gui_point(pnt)
            dist = math.sqrt((arm_y - pos.y())**2 + (arm_x - pos.x())**2)
            if dist < closest_dist and (min_dist is None or dist < min_dist):
                closest_pnt = pnt
        return closest_pnt

    def get_closest_path_point(self, pos, min_dist=None):
        closest_pnt = None
        closest_dist = 1e10
        for pnt in self.profile.get_path():
            pnt_x, pnt_y = self.get_path_gui_point(pnt)
            dist = math.sqrt((pnt_y - pos.y())**2 + (pnt_x - pos.x())**2)
            if dist < closest_dist and (min_dist is None or dist < min_dist):
                closest_pnt = pnt
        return closest_pnt

    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            pnt = self.get_closest_point(pos, 20)
            if pnt is not None:
                self.points.remove(pnt)
            else:
                pnt = self.get_closest_path_point(pos, 20)
                index = self.points.index(pnt.end_waypoint)
                new_point = Waypoint(*self._gui_point_to_path_point(pos.x(), pos.y()))
                print(pnt.end_waypoint)
                print(pnt.start_waypoint)
                new_point.yaw = math.atan2(pnt.end_waypoint.y - pnt.start_waypoint.y, pnt.end_waypoint.x - pnt.start_waypoint.x)
                self.points.insert(index, new_point)
            self.profile = Path(self.points, 0.6, d_t=0.1)
            self.profile.build_path()
            self.canvas_label.repaint()
        elif QApplication.keyboardModifiers() & Qt.AltModifier:
            pnt = self.get_closest_arm(pos, 20)
            if pnt is not None:
                if self.point_being_dragged is None:
                    self.drag_mode = "yaw"
                    self.point_being_dragged = pnt
                    self.ghost_point = pnt.copy()
                    arm_x, arm_y = self.get_arm_gui_point(self.point_being_dragged)
                    self.drag_offset = [
                        pos.x() - arm_x,
                        pos.y() - arm_y
                    ]
        else:
            pnt = self.get_closest_point(pos, 20)
            if pnt is not None:
                if self.point_being_dragged is None:
                    self.drag_mode = "pos"
                    self.point_being_dragged = pnt
                    self.ghost_point = pnt.copy()
                    pnt_x, pnt_y = self.get_path_gui_point(pnt)
                    self.drag_offset = [
                        pos.x() - pnt_x,
                        pos.y() - pnt_y
                    ]


    def mouseMoveEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        if self.point_being_dragged is not None:
            if self.drag_mode == 'pos':
                self.point_being_dragged.x, self.point_being_dragged.y = self._gui_point_to_path_point(
                    pos.x() - self.drag_offset[0], 
                    pos.y() - self.drag_offset[1]
                )
            elif self.drag_mode == 'yaw':
                x, y = self.get_path_gui_point(self.point_being_dragged)
                w = x - (pos.x() - self.drag_offset[0])
                h = y - (pos.y() - self.drag_offset[1])
                self.point_being_dragged.yaw = math.atan2(h, w) + math.pi
            self.profile = Path(self.points, 0.6, d_t=0.1)
            self.profile.build_path()
            self.canvas_label.repaint()


    def mouseReleaseEvent(self, QMouseEvent):
        if self.point_being_dragged is not None:
            self.drag_mode = None
            self.point_being_dragged = None
            self.drag_offset = None
            self.ghost_point = None
            self.profile = Path(self.points, 0.6, d_t=0.1)
            self.profile.build_path()
            self.canvas_label.repaint()
        
    def initUI(self):
        self.setWindowTitle('Drawing text')
        self.show()
        
    def paintEvent(self, event):
        pixmap = QPixmap(self.canvas_label.size())
        pixmap.fill(QColor(0, 0, 0, 0))
        qp = QPainter()
        qp.begin(pixmap)
        self.draw_path(qp)
        self.draw_waypoints(qp)
        qp.end()
        self.canvas_label.setPixmap(pixmap)

    def draw_waypoints(self, qp):
        pen = QPen()
        if self.ghost_point is not None:
            x, y = self.get_path_gui_point(self.ghost_point)
            v_x, v_y = self.get_arm_gui_point(self.ghost_point)
            pen.setColor(QColor(255, 150, 150))
            pen.setWidth(3)
            qp.setPen(pen)
            qp.drawLine(x, y, v_x, v_y)
            pen.setColor(QColor(255, 100, 100))
            pen.setWidth(8)
            qp.setPen(pen)
            qp.drawPoint(x, y)
        for pnt in self.points:
            x, y = self.get_path_gui_point(pnt)
            v_x, v_y = self.get_arm_gui_point(pnt)

            pen.setColor(QColor(250, 80, 80))
            pen.setWidth(3)
            qp.setPen(pen)
            qp.drawLine(x, y, v_x, v_y)

            pen.setColor(QColor(240, 20, 20))
            pen.setWidth(8)
            qp.setPen(pen)
            qp.drawPoint(x, y)

    def draw_path(self, qp):
        pen = QPen()
        pen.setColor(QColor(20, 20, 240))
        pen.setWidth(3)
        qp.setPen(pen)

        for path in [self.profile.get_left_path(), self.profile.get_right_path()]:
            for i in range(1, len(path)):
                pnt = path[i]
                pnt2 = path[i-1]
                qp.drawLine(
                    *self.get_path_gui_point(pnt),
                    *self.get_path_gui_point(pnt2)
                )
        pen = QPen()
        pen.setColor(QColor(20, 240, 200))
        pen.setWidth(3)
        qp.setPen(pen)
        for i in range(1, len(self.profile.get_path())):
            pnt = self.profile.get_path()[i]
            pnt2 = self.profile.get_path()[i-1]
            qp.drawLine(
                *self.get_path_gui_point(pnt),
                *self.get_path_gui_point(pnt2)
            )