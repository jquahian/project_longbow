import sys
import degrees_calc as dc
import inverse_kin as ik
import board_control as bc
import os
import csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

"""
TODO:
- degree saving
- limit switches
- homing
- 3D visualization of robot position
- constrain IK solver properly
"""


class App(QWidget):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = "Longbow GUI Control"

        # window start position
        self.left = 100
        self.top = 100

        # app size
        self.width = 1920
        self.height = 500
        self.longbow_UI()

    def longbow_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()
        self.setLayout(layout)

        self.connect_btn = QPushButton("Connect")
        layout.addWidget(self.connect_btn, 0, 0)
        self.connect_btn.clicked.connect(lambda: self.connect())
        self.is_connected = False

        self.calibrate_btn = QPushButton("Calibrate")
        layout.addWidget(self.calibrate_btn, 0, 1)
        self.calibrate_btn.clicked.connect(lambda: self.calibrate_all())
        self.is_calibrated = True

        self.home_joints_btn = QPushButton("Home")
        layout.addWidget(self.home_joints_btn, 0, 2)
        self.home_joints_btn.clicked.connect(lambda: self.home_joints())

        self.app_list = QComboBox()
        layout.addWidget(self.app_list, 0, 3)

        self.app_list_refresh = QPushButton("Refresh Apps")
        layout.addWidget(self.app_list_refresh, 0, 4)
        self.app_list_refresh.clicked.connect(
            lambda: self.refresh_dropdown_list(self.app_list_refresh, self.app_list, 'apps'))

        self.degrees_list = QComboBox()
        layout.addWidget(self.degrees_list, 0, 5)
        self.degrees_list.activated[str].connect(
            lambda: self.degrees_loader('saved_degrees', str(self.degrees_list.currentText())))

        self.degrees_list_refresh = QPushButton("Refresh Saved Degrees")
        layout.addWidget(self.degrees_list_refresh, 0, 6)
        self.degrees_list_refresh.clicked.connect(
            lambda: self.refresh_dropdown_list(self.degrees_list_refresh, self.degrees_list, 'saved_degrees'))
        
        self.degrees_list_loop = QLineEdit()
        layout.addWidget(self.degrees_list_loop, 0, 7)
        self.degrees_list_loop.setValidator(QIntValidator())
        self.degrees_list_loop.setText('1')
        
        self.degrees_run = QPushButton("Run Saved Degrees")
        layout.addWidget(self.degrees_run, 0, 8)
        self.degrees_run.setEnabled(False)
        self.degrees_run.clicked.connect(
            lambda: self.run_saved_degrees()
        )

        self.joint_header = QLabel("Joint \nNumber")
        layout.addWidget(self.joint_header, 1, 0)

        self.joint_gear_ratio_label = QLabel("Gear \nReduction")
        layout.addWidget(self.joint_gear_ratio_label, 1, 1)

        self.degree_readout_header = QLabel("Current \nDegree")
        layout.addWidget(self.degree_readout_header, 1, 2)

        self.target_degree_header = QLabel("Target \nDegree")
        layout.addWidget(self.target_degree_header, 1, 4)

        self.zero_all_btn = QPushButton("Zero All")
        layout.addWidget(self.zero_all_btn, 10, 5)
        self.zero_all_btn.clicked.connect(lambda: self.accept_all(True))

        self.accept_all_btn = QPushButton("Accept All")
        layout.addWidget(self.accept_all_btn, 10, 6)
        self.accept_all_btn.clicked.connect(lambda: self.accept_all(False))

        self.encoder_pos_header = QLabel("Current \nEncoder \nPosition")
        layout.addWidget(self.encoder_pos_header, 1, 7)

        self.coordinate_header = QLabel("Coordinate \nInput")
        layout.addWidget(self.coordinate_header, 1, 8)

        self.move_to_coord_btn = QPushButton("To Coordinates")
        layout.addWidget(self.move_to_coord_btn, 10, 8)
        self.move_to_coord_btn.clicked.connect(
            lambda: self.ik_move())

        self.joint_1_header = QLabel('Joint 1')
        self.joint_2_header = QLabel('Joint 2')
        self.joint_3_header = QLabel('Joint 3')
        self.joint_4_header = QLabel('Joint 4')
        self.joint_5_header = QLabel('Joint 5')
        self.joint_6_header = QLabel('Joint 6')

        self.joint_1_gear_ratio = QLabel('125')
        self.joint_2_gear_ratio = QLabel('125')
        self.joint_3_gear_ratio = QLabel('125')
        self.joint_4_gear_ratio = QLabel('125')
        self.joint_5_gear_ratio = QLabel('125')
        self.joint_6_gear_ratio = QLabel('5')

        self.joint_1_current_degrees_label = QLabel('0.0')
        self.joint_2_current_degrees_label = QLabel('0.0')
        self.joint_3_current_degrees_label = QLabel('0.0')
        self.joint_4_current_degrees_label = QLabel('0.0')
        self.joint_5_current_degrees_label = QLabel('0.0')
        self.joint_6_current_degrees_label = QLabel('0.0')

        self.joint_1_slider = self.angle_slider()
        self.joint_2_slider = self.angle_slider()
        self.joint_3_slider = self.angle_slider()
        self.joint_4_slider = self.angle_slider()
        self.joint_5_slider = self.angle_slider()
        self.joint_6_slider = self.angle_slider()

        self.readout_1 = QLineEdit()
        self.readout_1.setText("0.0")
        self.readout_2 = QLineEdit()
        self.readout_2.setText("0.0")
        self.readout_3 = QLineEdit()
        self.readout_3.setText("0.0")
        self.readout_4 = QLineEdit()
        self.readout_4.setText("0.0")
        self.readout_5 = QLineEdit()
        self.readout_5.setText("0.0")
        self.readout_6 = QLineEdit()
        self.readout_6.setText("0.0")

        self.zero_1 = QPushButton('Zero')
        self.zero_2 = QPushButton('Zero')
        self.zero_3 = QPushButton('Zero')
        self.zero_4 = QPushButton('Zero')
        self.zero_5 = QPushButton('Zero')
        self.zero_6 = QPushButton('Zero')

        self.accept_1 = QPushButton('Accept')
        self.accept_2 = QPushButton('Accept')
        self.accept_3 = QPushButton('Accept')
        self.accept_4 = QPushButton('Accept')
        self.accept_5 = QPushButton('Accept')
        self.accept_6 = QPushButton('Accept')

        self.encoder_pos_1 = QLabel('0')
        self.encoder_pos_2 = QLabel('0')
        self.encoder_pos_3 = QLabel('0')
        self.encoder_pos_4 = QLabel('0')
        self.encoder_pos_5 = QLabel('0')
        self.encoder_pos_6 = QLabel('0')

        self.x_coord_label = QLabel('X Coorinate:')
        self.x_coord_input = QLineEdit()
        self.x_coord_input.setValidator(QIntValidator())
        self.x_coord_input.setMaxLength(4)

        self.y_coord_label = QLabel('Y Coorinate:')
        self.y_coord_input = QLineEdit()
        self.y_coord_input.setValidator(QIntValidator())
        self.y_coord_input.setMaxLength(4)

        self.z_coord_label = QLabel('Z Coorinate:')
        self.z_coord_input = QLineEdit()
        self.z_coord_input.setValidator(QIntValidator())
        self.z_coord_input.setMaxLength(4)

        joint_headers = [self.joint_1_header, self.joint_2_header, self.joint_3_header,
                         self.joint_4_header, self.joint_5_header, self.joint_6_header]

        joint_gear_ratios = [self.joint_1_gear_ratio, self.joint_2_gear_ratio, self.joint_3_gear_ratio,
                             self.joint_4_gear_ratio, self.joint_5_gear_ratio, self.joint_6_gear_ratio]

        joint_current_degrees = [self.joint_1_current_degrees_label,
                                 self.joint_2_current_degrees_label,
                                 self.joint_3_current_degrees_label,
                                 self.joint_4_current_degrees_label,
                                 self.joint_5_current_degrees_label,
                                 self.joint_6_current_degrees_label]

        angle_sliders = [self.joint_1_slider, self.joint_2_slider, self.joint_3_slider,
                         self.joint_4_slider, self.joint_5_slider, self.joint_6_slider]

        readouts = [self.readout_1, self.readout_2, self.readout_3,
                    self.readout_4, self.readout_5, self.readout_6]

        zero_btns = [self.zero_1, self.zero_2, self.zero_3,
                     self.zero_4, self.zero_5, self.zero_6]

        accept_btns = [self.accept_1, self.accept_2, self.accept_3,
                       self.accept_4, self.accept_5, self.accept_6]

        encoder_pos_readouts = [self.encoder_pos_1, self.encoder_pos_2, self.encoder_pos_3,
                                self.encoder_pos_4, self.encoder_pos_5, self.encoder_pos_6]

        coordinate_inputs = [self.x_coord_label, self.x_coord_input, self.y_coord_label,
                             self.y_coord_input, self.z_coord_label, self.z_coord_input]

        for i in range(6):
            layout.addWidget(joint_headers[i], 2 + i, 0)
            layout.addWidget(joint_gear_ratios[i], 2 + i, 1)
            layout.addWidget(joint_current_degrees[i], 2 + i, 2)
            layout.addWidget(angle_sliders[i], 2 + i, 3)
            layout.addWidget(readouts[i], 2 + i, 4)
            layout.addWidget(zero_btns[i], 2 + i, 5)
            layout.addWidget(accept_btns[i], 2 + i, 6)
            layout.addWidget(encoder_pos_readouts[i], 2 + i, 7)
            layout.addWidget(coordinate_inputs[i], 2 + i, 8)

        self.joint_1_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_1_slider, self.readout_1))
        self.joint_2_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_2_slider, self.readout_2))
        self.joint_3_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_3_slider, self.readout_3))
        self.joint_4_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_4_slider, self.readout_4))
        self.joint_5_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_5_slider, self.readout_5))
        self.joint_6_slider.valueChanged.connect(
            lambda: self.input_slider_value(self.joint_6_slider, self.readout_6))

        self.zero_1.clicked.connect(
            lambda: self.set_degrees(1, self.joint_1_slider, self.joint_1_current_degrees_label, self.readout_1, 125, self.encoder_pos_1, True))
        self.zero_2.clicked.connect(
            lambda: self.set_degrees(2, self.joint_2_slider, self.joint_2_current_degrees_label, self.readout_2, 125, self.encoder_pos_2, True))
        self.zero_3.clicked.connect(
            lambda: self.set_degrees(3, self.joint_3_slider, self.joint_3_current_degrees_label, self.readout_3, 125, self.encoder_pos_3, True))
        self.zero_4.clicked.connect(
            lambda: self.set_degrees(4, self.joint_4_slider, self.joint_4_current_degrees_label, self.readout_4, 125, self.encoder_pos_4, True))
        self.zero_5.clicked.connect(
            lambda: self.set_degrees(5, self.joint_5_slider, self.joint_5_current_degrees_label, self.readout_5, 125, self.encoder_pos_5, True))
        self.zero_6.clicked.connect(
            lambda: self.set_degrees(6, self.joint_6_slider, self.joint_6_current_degrees_label, self.readout_6, 5, self.encoder_pos_6, True))

        self.accept_1.clicked.connect(
            lambda: self.set_degrees(1, self.joint_1_slider, self.joint_1_current_degrees_label, self.readout_1, 125, self.encoder_pos_1, False))
        self.accept_2.clicked.connect(
            lambda: self.set_degrees(2, self.joint_2_slider, self.joint_2_current_degrees_label, self.readout_2, 125, self.encoder_pos_2, False))
        self.accept_3.clicked.connect(
            lambda: self.set_degrees(3, self.joint_3_slider, self.joint_3_current_degrees_label, self.readout_3, 125, self.encoder_pos_3, False))
        self.accept_4.clicked.connect(
            lambda: self.set_degrees(4, self.joint_4_slider, self.joint_4_current_degrees_label, self.readout_4, 125, self.encoder_pos_4, False))
        self.accept_5.clicked.connect(
            lambda: self.set_degrees(5, self.joint_5_slider, self.joint_5_current_degrees_label, self.readout_5, 125, self.encoder_pos_5, False))
        self.accept_6.clicked.connect(
            lambda: self.set_degrees(6, self.joint_6_slider, self.joint_6_current_degrees_label, self.readout_6, 5, self.encoder_pos_6, False))

    def connect(self):
        bc.connect_to()
        connect_message = QMessageBox()
        connect_message.setFixedSize(400, 150)
        connect_message.setIcon(QMessageBox.Information)
        connect_message.setStandardButtons(QMessageBox.Ok)
        connect_message.setWindowTitle("Connected")
        connect_message.setText("Longbow Connected")
        connect_message.exec_()
        
        self.is_connected = True

    def calibrate_all(self):
        if self.is_connected:
            bc.calibrate_all()
            calibrate_message = QMessageBox()
            calibrate_message.setFixedSize(400, 150)
            calibrate_message.setIcon(QMessageBox.Information)
            calibrate_message.setStandardButtons(QMessageBox.Ok)
            calibrate_message.setWindowTitle("Calibrated")
            calibrate_message.setText("Longbow Calibration Complete")
            calibrate_message.exec_()
            self.is_calibrated = True
        else:
            calibrate_message = QMessageBox()
            calibrate_message.setFixedSize(400, 150)
            calibrate_message.setIcon(QMessageBox.Information)
            calibrate_message.setStandardButtons(QMessageBox.Ok)
            calibrate_message.setWindowTitle("Longbow Connection Needed")
            calibrate_message.setText("Connection Missing")
            calibrate_message.exec_()

    def home_joints(self):
        pass
    
    # will keep track of dropdowbn contents
    list_items = []
    
    def refresh_dropdown_list(self, btn_to_update, dropdown_to_update, dir_path):
        file_list = os.listdir(dir_path)
        
        # populate a list with the current contents of the dropbox menu
        if dropdown_to_update.count() > 0:                
            for i in range(dropdown_to_update.count()):
                if dropdown_to_update.itemText(i) not in self.list_items:
                    self.list_items.append(dropdown_to_update.itemText(i))
         
        # load only .py or .csv
        # do not load if already listed in the dropdown
        for files in file_list:
            if files not in self.list_items:
                if files[-3:] == 'csv' or files[-3:] == '.py':
                    dropdown_to_update.addItem(files)
        
        print(self.list_items)

    # global coordinate storage for other coord loading functions
    saved_degree_rows = []
    
    def degrees_loader(self, dir, list_selection):
        # clear loading a new file
        self.saved_degree_rows = []
        self.degrees_run.setEnabled(True)
        
        with open(os.path.join(dir, list_selection), mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                self.saved_degree_rows.append(row)
            
            # always display the first set of coordinates in the UI when selecting coordinate files
            self.readout_1.setText(str(self.saved_degree_rows[0][0]))
            self.readout_2.setText(str(self.saved_degree_rows[0][1]))
            self.readout_3.setText(str(self.saved_degree_rows[0][2]))
            self.readout_4.setText(str(self.saved_degree_rows[0][3]))
            self.readout_5.setText(str(self.saved_degree_rows[0][4]))
            self.readout_6.setText(str(self.saved_degree_rows[0][5]))
            
            print(len(self.saved_degree_rows))

    # runs through all the coordinates in a given CSV file
    def run_saved_degrees(self):
        loop_num =  int(self.degrees_list_loop.text())        

        # clear any previously saved degrees
        bc.j1_pos = []
        bc.j2_pos = []
        bc.j3_pos = []
        bc.j4_pos = []
        bc.j5_pos = []
        bc.j6_pos = []
        
        for i in range(loop_num):      
            # add the degrees, as encoder counts, to the position list in board control
            for i in range(len(self.saved_degree_rows)):
                bc.j1_pos.append(dc.return_counts(float(self.saved_degree_rows[i][0]), 125))
                bc.j2_pos.append(dc.return_counts(float(self.saved_degree_rows[i][1]), 125))
                bc.j3_pos.append(dc.return_counts(float(self.saved_degree_rows[i][2]), 125))
                bc.j4_pos.append(dc.return_counts(float(self.saved_degree_rows[i][3]), 125))
                bc.j5_pos.append(dc.return_counts(float(self.saved_degree_rows[i][4]), 125))
                bc.j6_pos.append(dc.return_counts(float(self.saved_degree_rows[i][5]), 5))

            # run through the coordinates
            
            if self.is_calibrated:       
                bc.move_to_saved_pos(0)

        # popup saying completed run or loop though from the start
        run_complete_message = QMessageBox()
        run_complete_message.setFixedSize(750, 300)
        run_complete_message.setIcon(QMessageBox.Information)
        run_complete_message.setStandardButtons(QMessageBox.Ok)
        run_complete_message.setWindowTitle("Completed")
        run_complete_message.setText("Run Complete")
        run_complete_message.exec_()

        # always display the last set of coordinates in the UI when the run has completed
        final_joint_pos = len(self.saved_degree_rows) - 1
        
        self.readout_1.setText(str(self.saved_degree_rows[final_joint_pos][0]))
        self.readout_2.setText(str(self.saved_degree_rows[final_joint_pos][1]))
        self.readout_3.setText(str(self.saved_degree_rows[final_joint_pos][2]))
        self.readout_4.setText(str(self.saved_degree_rows[final_joint_pos][3]))
        self.readout_5.setText(str(self.saved_degree_rows[final_joint_pos][4]))
        self.readout_6.setText(str(self.saved_degree_rows[final_joint_pos][5]))
    
    def ik_move(self):
        x_coord = int(self.x_coord_input.text())
        y_coord = int(self.y_coord_input.text())
        z_coord = int(self.z_coord_input.text())

        ik.to_coordinate(x_coord, y_coord, z_coord)

        """
        these thetas correspond with only these joints:
        theta 1: joint 2
        theta 2: joint 3
        theta 3: joint 5
        """
        print(ik.theta_1, ik.theta_2, ik.theta_3)

        self.x_coord_input.clear()
        self.y_coord_input.clear()
        self.z_coord_input.clear()

        # update slider positions
        # update readout positions
        # automatically move the arm to the coordinate

    def accept_all(self, is_zero):
        self.set_degrees(1, self.joint_1_slider, self.joint_1_current_degrees_label,
                         self.readout_1, 125, self.encoder_pos_1, is_zero)
        self.set_degrees(2, self.joint_2_slider, self.joint_2_current_degrees_label,
                         self.readout_2, 125, self.encoder_pos_2, is_zero)
        self.set_degrees(3, self.joint_3_slider, self.joint_3_current_degrees_label,
                         self.readout_3, 125, self.encoder_pos_3, is_zero)
        self.set_degrees(4, self.joint_4_slider, self.joint_4_current_degrees_label,
                         self.readout_4, 125, self.encoder_pos_4, is_zero)
        self.set_degrees(5, self.joint_5_slider, self.joint_5_current_degrees_label,
                         self.readout_5, 125, self.encoder_pos_5, is_zero)
        self.set_degrees(6, self.joint_6_slider, self.joint_6_current_degrees_label,
                         self.readout_6, 5, self.encoder_pos_6, is_zero)

    def angle_slider(self):
        self.joint_degree_slider = QSlider(Qt.Horizontal)
        self.joint_degree_slider.setMinimum(-27000)
        self.joint_degree_slider.setMaximum(27000)
        self.joint_degree_slider.setValue(0)

        return self.joint_degree_slider

    def input_slider_value(self, joint_slider_num, joint_readout_num):
        degree_readout = round(joint_slider_num.value()/100, 1)
        joint_readout_num.setText(str(degree_readout))

    def set_degrees(self, joint_number, joint_slider, joint_degrees_label, readout_value, gear_ratio, encoder_readout, is_zero):
        if float(readout_value.text()) * 100 > 27000 or float(readout_value.text()) * 100 < -27000:
            error_message = QErrorMessage()
            error_message.setFixedSize(700, 250)
            error_message.showMessage(
                f"The Value of {float(readout_value.text())} degrees is out of range.  \nValue must be between +/- 270.0 degrees")
            error_message.setWindowTitle("Error: value out of range")
            error_message.exec_()
            readout_value.setText("0.0")
        else:
            if is_zero == True:
                readout_value.setText("0.0")

            readout_to_slider = float(readout_value.text()) * 100
            joint_degrees_label.setText(str(readout_value.text()))
            joint_slider.setSliderPosition(int(readout_to_slider))
            motor_encoder_count = dc.return_counts(
                float(joint_degrees_label.text()), gear_ratio)
            encoder_readout.setText(str(motor_encoder_count))

            if self.is_calibrated:
                bc.move_axis_by_count(joint_number, motor_encoder_count)

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
