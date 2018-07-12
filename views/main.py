import os
import json
import math
import copy

import pathfinder as pf

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
            pf.Waypoint(0.6, 1.2, 0),
            pf.Waypoint(4.2, 1.2, 0),
            pf.Waypoint(6, 3, math.radians(90)),
            pf.Waypoint(5.9, 15*0.3, math.radians(95)),
            pf.Waypoint(24.5*0.3, 20.5*0.3, math.radians(-10))
        ]
        self.create_profiles()

        self.drag_mode = None
        self.point_being_dragged = None
        self.drag_offset = None
        self.ghost_point = None

        self.initUI()

    def create_profiles(self):
        _, self.middle_profile = pf.generate(self.points,
                                       pf.FIT_HERMITE_QUINTIC,
                                       pf.SAMPLES_HIGH,
                                       dt=0.1,
                                       max_velocity=3,
                                       max_acceleration=5,
                                       max_jerk=25)
        modifier = pf.modifiers.TankModifier(self.middle_profile).modify(0.6)
        self.left_profile = modifier.getLeftTrajectory()
        self.right_profile = modifier.getRightTrajectory()


    def _gui_point_to_path_point(self, x, y):
        pnt_scale = (self.canvas_label.size().height() - 30) / 8.2296
        x_offset = self.canvas_label.pos().x() + 33
        y_offset = self.canvas_label.pos().y() + 15
        return (x - x_offset) / pnt_scale, (y - y_offset) / pnt_scale

    def get_arm_gui_point(self, pnt):
        pnt_x, pnt_y = self.get_path_gui_point(pnt)
        return (pnt_x + math.cos(pnt.angle) * 20), (pnt_y + math.sin(pnt.angle) * 20)

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
        closest_dist = 1e100
        for pnt in self.middle_profile:
            pnt_x, pnt_y = self.get_path_gui_point(pnt)
            dist = math.sqrt((pnt_y - pos.y())**2 + (pnt_x - pos.x())**2)
            if dist < closest_dist and (min_dist is None or dist < min_dist):
                closest_pnt = pnt
                closest_dist = dist
        return closest_pnt

    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()

        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            pnt = self.get_closest_point(pos, 20)
            if pnt is not None:
                self.points.remove(pnt)
            else:
                pnt = self.get_closest_path_point(pos, 20)
                new_point = pf.Waypoint(pnt.x, pnt.y, pnt.heading)
                if pnt is not None:
                    index = None
                    for i in range(self.middle_profile.index(pnt), len(self.middle_profile)):
                        profile_pnt = self.middle_profile[i]
                        for j in range(len(self.points)):
                            waypnt = self.points[j]
                            dist = math.sqrt((waypnt.y - profile_pnt.y)**2 + (waypnt.x - profile_pnt.x)**2)
                            if dist < 0.2:
                                self.points.insert(j, new_point)
                                break
                        else:
                            continue
                        break
            self.create_profiles()
            self.canvas_label.repaint()

        elif QApplication.keyboardModifiers() & Qt.AltModifier:
            pnt = self.get_closest_arm(pos, 20)
            if pnt is not None:
                if self.point_being_dragged is None:
                    self.drag_mode = "angle"
                    self.point_being_dragged = pnt
                    self.ghost_point = pf.Waypoint(pnt.x, pnt.y, pnt.angle)
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
                    self.ghost_point = pf.Waypoint(pnt.x, pnt.y, pnt.angle)
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
            elif self.drag_mode == 'angle':
                x, y = self.get_path_gui_point(self.point_being_dragged)
                w = x - (pos.x() - self.drag_offset[0])
                h = y - (pos.y() - self.drag_offset[1])
                self.point_being_dragged.angle = math.atan2(h, w) + math.pi
            self.create_profiles()
            self.canvas_label.repaint()


    def mouseReleaseEvent(self, QMouseEvent):
        if self.point_being_dragged is not None:
            self.drag_mode = None
            self.point_being_dragged = None
            self.drag_offset = None
            self.ghost_point = None
            self.create_profiles()
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

        for path in [self.left_profile, self.right_profile]:
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
        for i in range(1, len(self.middle_profile)):
            pnt = self.middle_profile[i]
            pnt2 = self.middle_profile[i-1]
            qp.drawLine(
                *self.get_path_gui_point(pnt),
                *self.get_path_gui_point(pnt2)
            )