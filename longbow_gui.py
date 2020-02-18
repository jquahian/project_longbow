import sys
import degrees_calc as dc
import inverse_kin as ik
import board_control as bc
import os
import csv
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

"""
TODO:
- begin splitting app into multiple windows
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
        self.is_connected = False
        self.is_calibrated = True
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()
        self.setLayout(layout)
        
        for i in range(30):
            layout.setColumnStretch(i, 1)
            layout.setRowStretch(i, 1)
        
        self.connect_btn = QPushButton("Connect")
        layout.addWidget(self.connect_btn, 0, 0)
        self.connect_btn.clicked.connect(lambda: self.connect())

        self.calibrate_btn = QPushButton("Calibrate")
        layout.addWidget(self.calibrate_btn, 0, 1)
        self.calibrate_btn.clicked.connect(lambda: self.calibrate_all())

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
        layout.addWidget(self.joint_gear_ratio_label, 1, 2)

        self.degree_readout_header = QLabel("Current \nDegree")
        layout.addWidget(self.degree_readout_header, 1, 3)

        self.target_degree_header = QLabel("Target \nDegree")
        layout.addWidget(self.target_degree_header, 1, 5)

        self.zero_all_btn = QPushButton("Zero All")
        layout.addWidget(self.zero_all_btn, 10, 6)
        self.zero_all_btn.clicked.connect(lambda: self.accept_all(True))

        self.accept_all_btn = QPushButton("Accept All")
        layout.addWidget(self.accept_all_btn, 10, 7)
        self.accept_all_btn.clicked.connect(lambda: self.accept_all(False))

        self.encoder_pos_header = QLabel("Current \nEncoder \nPosition")
        layout.addWidget(self.encoder_pos_header, 1, 8)

        self.coordinate_header = QLabel("Coordinate \nInput")
        layout.addWidget(self.coordinate_header, 1, 9)

        self.move_to_coord_btn = QPushButton("To Coordinates")
        layout.addWidget(self.move_to_coord_btn, 10, 10)
        self.move_to_coord_btn.clicked.connect(
            lambda: self.ik_move())

        self.joint_1_header = QLabel('Joint 1')
        self.joint_2_header = QLabel('Joint 2')
        self.joint_3_header = QLabel('Joint 3')
        self.joint_4_header = QLabel('Joint 4')
        self.joint_5_header = QLabel('Joint 5')
        self.joint_6_header = QLabel('Joint 6')
        
        self.home_1 = QPushButton('Home')
        self.home_2 = QPushButton('Home')
        self.home_3 = QPushButton('Home')
        self.home_4 = QPushButton('Home')
        self.home_5 = QPushButton('Home')
        self.home_6 = QPushButton('Home')

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
        self.joint_1_slider.setMaximum(bc.joint_1_max * 100)
        
        self.joint_2_slider = self.angle_slider()
        self.joint_2_slider.setMaximum(bc.joint_2_max * 100)

        self.joint_3_slider = self.angle_slider()
        self.joint_3_slider.setMaximum(bc.joint_3_max * 100)
        
        self.joint_4_slider = self.angle_slider()
        self.joint_4_slider.setMaximum(bc.joint_4_max * 100)
        
        self.joint_5_slider = self.angle_slider()
        self.joint_5_slider.setMaximum(bc.joint_5_max * 100)
        
        self.joint_6_slider = self.angle_slider()
        self.joint_6_slider.setMaximum(bc.joint_6_max*  100)
        
        layout.setColumnMinimumWidth(4, 500)

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

        self.accept_1 = QPushButton('Move Absolute')
        self.accept_2 = QPushButton('Move Absolute')
        self.accept_3 = QPushButton('Move Absolute')
        self.accept_4 = QPushButton('Move Absolute')
        self.accept_5 = QPushButton('Move Absolute')
        self.accept_6 = QPushButton('Move Absolute')

        self.encoder_pos_1 = QLabel('0')
        self.encoder_pos_2 = QLabel('0')
        self.encoder_pos_3 = QLabel('0')
        self.encoder_pos_4 = QLabel('0')
        self.encoder_pos_5 = QLabel('0')
        self.encoder_pos_6 = QLabel('0')

        self.x_coord_label = QLabel('X Coordinate:')
        self.x_coord_input = QLineEdit()
        self.x_coord_input.setText('0.00')
        self.x_coord_input.setValidator(QDoubleValidator())
        self.x_coord_input.setMaxLength(6)

        self.y_coord_label = QLabel('Y Coordinate:')
        self.y_coord_input = QLineEdit()
        self.y_coord_input.setText('0.00')
        self.y_coord_input.setValidator(QDoubleValidator())
        self.y_coord_input.setMaxLength(6)

        self.z_coord_label = QLabel('Z Coordinate:')
        self.z_coord_input = QLineEdit()
        self.z_coord_input.setText('0.00')
        self.z_coord_input.setValidator(QDoubleValidator())
        self.z_coord_input.setMaxLength(6)

        self.joint_headers = [self.joint_1_header, self.joint_2_header, self.joint_3_header,
                         self.joint_4_header, self.joint_5_header, self.joint_6_header]
        
        self.joint_home_btns = [self.home_1, self.home_2,
                                self.home_3, self.home_4, self.home_5, self.home_6]

        self.joint_gear_ratios = [self.joint_1_gear_ratio, self.joint_2_gear_ratio, self.joint_3_gear_ratio,
                             self.joint_4_gear_ratio, self.joint_5_gear_ratio, self.joint_6_gear_ratio]

        self.joint_current_degrees = [self.joint_1_current_degrees_label,
                                 self.joint_2_current_degrees_label,
                                 self.joint_3_current_degrees_label,
                                 self.joint_4_current_degrees_label,
                                 self.joint_5_current_degrees_label,
                                 self.joint_6_current_degrees_label]

        self.angle_sliders = [self.joint_1_slider, self.joint_2_slider, self.joint_3_slider,
                         self.joint_4_slider, self.joint_5_slider, self.joint_6_slider]

        self.readouts = [self.readout_1, self.readout_2, self.readout_3,
                    self.readout_4, self.readout_5, self.readout_6]

        self.zero_btns = [self.zero_1, self.zero_2, self.zero_3,
                     self.zero_4, self.zero_5, self.zero_6]

        self.accept_btns = [self.accept_1, self.accept_2, self.accept_3,
                       self.accept_4, self.accept_5, self.accept_6]

        self.encoder_pos_readouts = [self.encoder_pos_1, self.encoder_pos_2, self.encoder_pos_3,
                                self.encoder_pos_4, self.encoder_pos_5, self.encoder_pos_6]

        self.coordinate_inputs = [self.x_coord_label, self.x_coord_input, self.y_coord_label,
                             self.y_coord_input, self.z_coord_label, self.z_coord_input]

        for i in range(6):
            layout.addWidget(self.joint_headers[i], 2 + i, 0)
            layout.addWidget(self.joint_home_btns[i], 2 + i, 1)
            layout.addWidget(self.joint_gear_ratios[i], 2 + i, 2)
            layout.addWidget(self.joint_current_degrees[i], 2 + i, 3)
            layout.addWidget(self.angle_sliders[i], 2 + i, 4)
            layout.addWidget(self.readouts[i], 2 + i, 5)
            layout.addWidget(self.zero_btns[i], 2 + i, 6)
            layout.addWidget(self.accept_btns[i], 2 + i, 7)
            layout.addWidget(self.encoder_pos_readouts[i], 2 + i, 8)
            layout.addWidget(self.coordinate_inputs[i], 2 + i, 9)

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

        self.home_1.clicked.connect(lambda: self.home_joints(1, 2, 125, bc.joint_1_calibration, 1,
                                                             self.joint_1_current_degrees_label, self.joint_1_slider, self.readout_1, self.encoder_pos_1))
        self.home_2.clicked.connect(lambda: self.home_joints(2, 3, 125, bc.joint_2_calibration, 1,
                                                             self.joint_2_current_degrees_label, self.joint_2_slider, self.readout_2, self.encoder_pos_2))
        self.home_3.clicked.connect(lambda: self.home_joints(3, 4, 125, bc.joint_3_calibration, 1,
                                                             self.joint_3_current_degrees_label, self.joint_3_slider, self.readout_3, self.encoder_pos_3))
        self.home_4.clicked.connect(lambda: self.home_joints(4, 5, 125, bc.joint_4_calibration, 1,
                                                             self.joint_4_current_degrees_label, self.joint_4_slider, self.readout_4, self.encoder_pos_4))
        self.home_5.clicked.connect(lambda: self.home_joints(5, 6, 125, bc.joint_5_calibration, 1,
                                                             self.joint_5_current_degrees_label, self.joint_5_slider, self.readout_5, self.encoder_pos_5))
        self.home_6.clicked.connect(lambda: self.home_joints(6, 7, 5, bc.joint_6_calibration, 1,
                                                             self.joint_6_current_degrees_label, self.joint_6_slider, self.readout_6, self.encoder_pos_6))

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

    # will keep track of dropdowbn contents
    list_items = []

    # global coordinate storage for other coord loading functions
    saved_degree_rows = []
    
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
            self.create_message_box("Calibrated", "Longbow Calibration Complete")            
            self.is_calibrated = True
        else:
            self.create_message_box("Connection Needed", "Longbow Not Connected")

    def home_joints(self, joint_to_home, pin_num, gear_reduction, calibration_array, direction_modifier, label_to_modify, joint_slider_num, readout_value, encoder_readout):
        
        readout_value.setText(str(calibration_array[2]))
        self.set_joint_position_readouts(joint_slider_num, label_to_modify, readout_value, gear_reduction, encoder_readout)
        
        if self.is_connected and self.is_calibrated:
            bc.home_axis(pin_num = pin_num, joint_num = joint_to_home, gear_reduction = gear_reduction, joint_calibration_array = calibration_array, direction_modifier = direction_modifier)

            time.sleep(2.0)

            self.create_message_box(f'Joint {joint_to_home} Homed', f'Joint {joint_to_home} now homed')
        
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
        
        for i in range(len(self.saved_degree_rows)):
            # add the degrees, as encoder counts, to the position list in board control
            bc.j1_pos.append(dc.return_counts(float(self.saved_degree_rows[i][0]), 125))
            bc.j2_pos.append(dc.return_counts(float(self.saved_degree_rows[i][1]), 125))
            bc.j3_pos.append(dc.return_counts(float(self.saved_degree_rows[i][2]), 125))
            bc.j4_pos.append(dc.return_counts(float(self.saved_degree_rows[i][3]), 125))
            bc.j5_pos.append(dc.return_counts(float(self.saved_degree_rows[i][4]), 125))
            bc.j6_pos.append(dc.return_counts(float(self.saved_degree_rows[i][5]), 5))
       
        for i in range(loop_num):      
            print(f'loop number: {i}')
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
        
        '''
        only working in x-z plane for now
        '''
        
        x_coord = float(self.x_coord_input.text())
        y_coord = float(self.y_coord_input.text())
        z_coord = float(self.z_coord_input.text())

        ik.to_coordinate(
            bc.joint_angles[1], bc.joint_angles[2], bc.joint_angles[4], x_coord, y_coord, z_coord, 'parallel')
        
        # update the angles between joints
        # calculate the new absolute position of each joint
        joint_2_new_position = float(self.joint_2_current_degrees_label.text()) + ik.deltas[0]
        joint_3_new_position = float(self.joint_3_current_degrees_label.text()) + ik.deltas[1]
        joint_5_new_position = float(self.joint_5_current_degrees_label.text()) + ik.deltas[2]
        
        # update the readout and other positional GUI elements of where the joints are going to move to
        self.readout_2.setText(str(round(joint_2_new_position, 3)))
        self.readout_3.setText(str(round(joint_3_new_position, 3)))
        self.readout_5.setText(str(round(joint_5_new_position, 3)))
        
        self.set_joint_position_readouts(self.joint_2_slider, 'pass', self.readout_2, 125, self.encoder_pos_2)
        
        self.set_joint_position_readouts(
            self.joint_3_slider, 'pass', self.readout_3, 125, self.encoder_pos_3)
        
        self.set_joint_position_readouts(
            self.joint_5_slider, 'pass', self.readout_5, 125, self.encoder_pos_5)

        # clears all input to prep for new coordinates
        self.x_coord_input.clear()
        self.y_coord_input.clear()
        self.z_coord_input.clear()
        
        self.x_coord_input.setText('0.00')
        self.y_coord_input.setText('0.00')
        self.z_coord_input.setText('0.00')

    def accept_all(self, is_zero):
        # NEW ANGLES
        self.update_joint_angles()
        
        for i in range(6):
            joint_num = i + 1
            
            if joint_num == 6:
                gear_ratio = 5
            else:
                gear_ratio = 125
                        
            self.set_degrees(
                joint_num,
                self.angle_sliders[i],
                self.joint_current_degrees[i],
                self.readouts[i],
                gear_ratio,
                self.encoder_pos_readouts[i],
                is_zero)

    def update_joint_angles(self):        
        bc.joint_angles[1] = bc.joint_angles[1] + ik.deltas[0]

        bc.joint_angles[2] = bc.joint_angles[2] + ik.deltas[1]

        bc.joint_angles[4] = bc.joint_angles[4] + ik.deltas[2]
        
        print(bc.joint_angles[1], bc.joint_angles[2], bc.joint_angles[4])
               
    def angle_slider(self):
        self.joint_degree_slider = QSlider(Qt.Horizontal)
        self.joint_degree_slider.setValue(0)

        return self.joint_degree_slider

    def input_slider_value(self, joint_slider_num, joint_readout_num):
        degree_readout = round(joint_slider_num.value()/100, 1)
        joint_readout_num.setText(str(degree_readout))

    def set_degrees(self, joint_number, joint_slider, joint_degrees_label, readout_value, gear_ratio, encoder_readout, is_zero):
        if float(readout_value.text()) * 100 > joint_slider.maximum() or float(readout_value.text()) < 0:
            error_message = QErrorMessage()
            error_message.setFixedSize(700, 250)
            error_message.showMessage(
                f"The Value of {float(readout_value.text())} degrees is out of range.  \nValue must be between 0 and {joint_slider.maximum() / 100} degrees")
            error_message.setWindowTitle("Error: value out of range")
            error_message.exec_()
            readout_value.setText("0.0")
        else:
            if is_zero == True:
                readout_value.setText("0.0")
                
            self.set_joint_position_readouts(joint_slider, joint_degrees_label, readout_value, gear_ratio, encoder_readout)
            
            if self.is_connected and self.is_calibrated:
                self.return_encoder_counts(joint_degrees_label, gear_ratio, encoder_readout)
                bc.move_axis_absolute(joint_number, self.motor_encoder_count)
    def set_joint_position_readouts(self, joint_slider, joint_degrees_label, readout_value, gear_ratio, encoder_readout):
            readout_to_slider = float(readout_value.text()) * 100
            
            if joint_degrees_label != 'pass':
                joint_degrees_label.setText(str(readout_value.text()))
            
            joint_slider.setSliderPosition(int(readout_to_slider))
            self.return_encoder_counts(float(readout_value.text()), gear_ratio, encoder_readout)
            encoder_readout.setText(str(self.motor_encoder_count))

    def return_encoder_counts(self, readout_value, gear_ratio, encoder_readout):
            motor_encoder_count = dc.return_counts(readout_value, gear_ratio)
            self.motor_encoder_count = motor_encoder_count
            
            return self.motor_encoder_count

    def create_message_box(self, window_title, window_text):
        msg_box = QMessageBox()
        msg_box.setFixedSize(400, 150)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setWindowTitle(window_title)
        msg_box.setText(window_text)
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
