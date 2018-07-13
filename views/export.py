import math
import json

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog

class ExportWindow(QDialog):
    
    def __init__(self, points, path, lpath, rpath):
        super().__init__()
        self.points = points
        uic.loadUi('ui/ExportView.ui', self)
        self.setFixedSize(self.size())

        self.save_button.clicked.connect(self.save_button_clicked)
        self.cancel_button.clicked.connect(self.close)

        self.show()

    def save_button_clicked(self):

        if self.csv_radio.isChecked():
            filename = QFileDialog.getSaveFileName(None, 'Save Data', 'data.csv', '*.csv')[0]

            if self.trajectories_radio.isChecked():
                ['time', 'position', 'velocity', 'acceleration', 'jerk', 'x', 'y', 'heading']
                print("Save Trajectories as CSV")

            elif self.waypoints_radio.isChecked():
                file = open(filename, 'w+')
                headers = ['x', 'y', 'angle']
                file.write(", ".join(headers) + "\n")
                for point in self.points:
                    file.write(", ".join([str(eval("point." + h, {'point': point})) for h in headers]) + "\n")
                file.close()
                self.close()

        elif self.json_radio.isChecked():
            filename = QFileDialog.getSaveFileName(None, 'Save Data', 'data.json', '*.json')[0]
            if self.trajectories_radio.isChecked():
                print("Save Trajectories as JSON")
            elif self.waypoints_radio.isChecked():
                data = [
                    {
                        'x': point.x,
                        'y': point.y,
                        'angle': point.angle
                    } for point in self.points
                ]
                json.dump(data, open(filename, 'w+'))
                self.close()

        elif self.java_radio.isChecked():
            filename = QFileDialog.getSaveFileName(None, 'Save Data', 'data.class', '*.class')[0]
            if self.trajectories_radio.isChecked():
                print("Save Trajectories as Java")
            elif self.waypoints_radio.isChecked():
                print("Save Waypoints as Java")

        elif self.cpp_radio.isChecked():
            filename = QFileDialog.getSaveFileName(None, 'Save Data', 'data.cpp', '*.cpp')[0]
            if self.trajectories_radio.isChecked():
                print("Save Trajectories as C++")
            elif self.waypoints_radio.isChecked():
                print("Save Waypoints as C++")

        elif self.python_radio.isChecked():
            filename = QFileDialog.getSaveFileName(None, 'Save Data', 'data.py', '*.py')[0]
            if self.trajectories_radio.isChecked():
                print("Save Trajectories as Python")
            elif self.waypoints_radio.isChecked():
                print("Save Waypoints as Python")