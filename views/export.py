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

        self.waypoints_radio.toggled.connect(self.update_preview)
        self.trajectories_radio.toggled.connect(self.update_preview)
        self.csv_radio.toggled.connect(self.update_preview)
        self.json_radio.toggled.connect(self.update_preview)
        self.java_radio.toggled.connect(self.update_preview)
        self.cpp_radio.toggled.connect(self.update_preview)
        self.python_radio.toggled.connect(self.update_preview)

        self.java_settings.setVisible(False)

        self.show()

    def update_preview(self):
        new_string = ""
        filename = "data.txt"
        if self.csv_radio.isChecked():
            if self.trajectories_radio.isChecked():
                ['time', 'position', 'velocity', 'acceleration', 'jerk', 'x', 'y', 'heading']
                pass

            elif self.waypoints_radio.isChecked():
                # open(filename, 'w+').write(self.get_csv_waypoints_str())
                new_string, filename = self.get_csv_waypoints_str()

        elif self.json_radio.isChecked():
            if self.trajectories_radio.isChecked():
                pass
            elif self.waypoints_radio.isChecked():
                # open(filename, 'w+').write(self.get_json_waypoints_str())
                new_string, filename = self.get_json_waypoints_str()

        elif self.java_radio.isChecked():
            if self.trajectories_radio.isChecked():
                [ass]
            elif self.waypoints_radio.isChecked():
                # open(filename, 'w+').write(self.get_java_waypoints_str())
                new_string, filename = self.get_java_waypoints_str()

        elif self.cpp_radio.isChecked():
            if self.trajectories_radio.isChecked():
                pass
            elif self.waypoints_radio.isChecked():
                pass

        elif self.python_radio.isChecked():
            if self.trajectories_radio.isChecked():
                pass
            elif self.waypoints_radio.isChecked():
                pass

        # self.csv_settings.setVisible(self.csv_radio.isChecked())
        # self.json_settings.setVisible(self.json_radio.isChecked())
        self.java_settings.setVisible(self.java_radio.isChecked())
        # self.cpp_settings.setVisible(self.cpp_radio.isChecked())
        # self.python_settings.setVisible(self.python_radio.isChecked())

        self.file_text = new_string
        self.filename = filename
        self.text_preview.setPlainText(new_string)

    def get_csv_waypoints_str(self):
        headers = ['x', 'y', 'angle']
        dump_str = ""
        dump_str += ", ".join(headers) + "\n"
        for point in self.points:
            dump_str += ", ".join([str(eval("point." + h, {'point': point})) for h in headers]) + "\n"
        return dump_str, "waypoints.csv"

    def get_json_waypoints_str(self):    
        data = [
            {
                'x': point.x,
                'y': point.y,
                'angle': point.angle
            } for point in self.points
        ]
        return json.dumps(data), "waypoints.json"

    def get_java_waypoints_str(self):
        class_name = self.class_name_input.text()
        package_name = self.package_name_input.text()
        dump_str = ""
        if package_name:
            dump_str += "package {};\n\n".format(package_name)
        dump_str += "import jaci.pathfinder.Pathfinder;\nimport jaci.pathfinder.Trajectory;\nimport jaci.pathfinder.Waypoint;\n\n"
        dump_str += "public class {} {{\n".format(class_name)
        dump_str += "    public static Waypoint[] waypoints = {\n"
        dump_str += ",\n".join(["        new Waypoint({}, {}, {})".format(point.x, point.y, point.angle) for point in self.points])
        dump_str += " \n   }\n"
        dump_str += "}\n"
        return dump_str, "{}.java".format(class_name)

    def save_button_clicked(self):
        file_str = self.file_text
        filename = self.filename
        file_type = self.filename.split(".")[-1]
            
        filename = QFileDialog.getSaveFileName(None, 'Save Data', filename, '*.' + file_type)[0]
        open(filename, 'w+').write(file_str)
        self.close()

