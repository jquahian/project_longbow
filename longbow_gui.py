import sys
import degrees_calc as dc
import inverse_kin as ik
import board_control as bc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

"""
todo:
1. zero button to zero out the sliders for joints
2. integer input for joint degrees
3. way to save coordinates in a list for later use
4. reduce the speeds of the motors!
5. get the limit switches working
6. get homing working
7. get 3D visualization of robot position
8. IK constrain IK solver properly
"""

class App(QWidget):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = "Longbow GUI Control"
        
        # window start position
        self.left = 100
        self.top = 100

        # app size
        self.width = 1980
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

        self.calibrate_btn = QPushButton("Calibrate")
        layout.addWidget(self.calibrate_btn, 0, 1)
        self.calibrate_btn.clicked.connect(lambda: self.calibrate_all())

        self.home_joints_btn = QPushButton("Home")
        layout.addWidget(self.home_joints_btn, 0, 2)
        self.home_joints_btn.clicked.connect(lambda: self.home_joints())

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
        self.move_to_coord_btn.clicked.connect(lambda: self.move_to_coordinates())

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
    
        zero_btns = [self.zero_1, self.zero_2, self.zero_3, self.zero_4, self.zero_5, self.zero_6]

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

    def calibrate_all(self):
        bc.calibrate_all()
        calibrate_message = QMessageBox()
        calibrate_message.setFixedSize(400, 150)
        calibrate_message.setIcon(QMessageBox.Information)
        calibrate_message.setStandardButtons(QMessageBox.Ok)
        calibrate_message.setWindowTitle("Calibrated")
        calibrate_message.setText("Longbow Calibration Complete")
        calibrate_message.exec_()

    def home_joints(self):
        pass

    def move_to_coordinates(self):
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
        self.set_degrees(1, self.joint_1_slider, self.joint_1_current_degrees_label, self.readout_1, 125, self.encoder_pos_1, is_zero)
        self.set_degrees(2, self.joint_2_slider, self.joint_2_current_degrees_label, self.readout_2, 125, self.encoder_pos_2, is_zero)
        self.set_degrees(3, self.joint_3_slider, self.joint_3_current_degrees_label, self.readout_3, 125, self.encoder_pos_3, is_zero)
        self.set_degrees(4, self.joint_4_slider, self.joint_4_current_degrees_label, self.readout_4, 125, self.encoder_pos_4, is_zero)
        self.set_degrees(5, self.joint_5_slider, self.joint_5_current_degrees_label, self.readout_5, 125, self.encoder_pos_5, is_zero)
        self.set_degrees(6, self.joint_6_slider, self.joint_6_current_degrees_label, self.readout_6, 5, self.encoder_pos_6, is_zero)

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
            error_message.showMessage(f"The Value of {float(readout_value.text())} degrees is out of range.  \nValue must be between +/- 270.0 degrees")
            error_message.setWindowTitle("Error: value out of range")
            error_message.exec_()
            readout_value.setText("0.0")
        else:
            if is_zero == True:
                readout_value.setText("0.0")
            
            readout_to_slider = float(readout_value.text()) * 100
            joint_degrees_label.setText(str(readout_value.text()))
            joint_slider.setSliderPosition(readout_to_slider)
            motor_encoder_count = dc.return_counts(float(joint_degrees_label.text()), gear_ratio)
            encoder_readout.setText(str(motor_encoder_count))
            
            # bc.move_axis_by_count(joint_number, motor_encoder_count)

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
