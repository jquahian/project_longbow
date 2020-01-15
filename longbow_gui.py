import sys
import degrees_calc as dc
# import board_control as bc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


class App(QWidget):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = "Longbow GUI Control"
        
        # window start position
        self.left = 100
        self.top = 100

        # app size
        self.width = 1280
        self.height = 350
        self.longbow_UI()

    def longbow_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()
        self.setLayout(layout)
        
        self.calibrate_btn = QPushButton("Calibrate All")
        layout.addWidget(self.calibrate_btn, 0, 0)
        self.calibrate_btn.clicked.connect(lambda: self.calibrate_all())

        self.joint_header = QLabel("Joint \nNumber")
        layout.addWidget(self.joint_header, 1, 0)

        self.joint_gear_ratio_label = QLabel("Gear \nReduction")
        layout.addWidget(self.joint_gear_ratio_label, 1, 1)

        self.degree_readout_header = QLabel("Current \nDegree")
        layout.addWidget(self.degree_readout_header, 1, 2)

        self.degree_readout_header = QLabel("Target \nDegree")
        layout.addWidget(self.degree_readout_header, 1, 4)

        self.encoder_pos_header = QLabel("Current \nEncoder \nPosition")
        layout.addWidget(self.encoder_pos_header, 1, 6)

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

        self.readout_1 = QLabel('0.0')
        self.readout_2 = QLabel('0.0')
        self.readout_3 = QLabel('0.0')
        self.readout_4 = QLabel('0.0')
        self.readout_5 = QLabel('0.0')
        self.readout_6 = QLabel('0.0')

        self.accept_1 = QPushButton('Accept')
        self.accept_2 = QPushButton('Accept')
        self.accept_3 = QPushButton('Accept')
        self.accept_4 = QPushButton('Accept')
        self.accept_5 = QPushButton('Accept')
        self.accept_6 = QPushButton('Accept')

        self.encoder_pos_1 = QLabel('0.0000')
        self.encoder_pos_2 = QLabel('0.0000')
        self.encoder_pos_3 = QLabel('0.0000')
        self.encoder_pos_4 = QLabel('0.0000')
        self.encoder_pos_5 = QLabel('0.0000')
        self.encoder_pos_6 = QLabel('0.0000')

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

        accept_btns = [self.accept_1, self.accept_2, self.accept_3,
                       self.accept_4, self.accept_5, self.accept_6]

        encoder_pos_readouts = [self.encoder_pos_1, self.encoder_pos_2, self.encoder_pos_3, 
                                self.encoder_pos_4, self.encoder_pos_5, self.encoder_pos_6]

        for i in range(6):
            layout.addWidget(joint_headers[i], 2 + i, 0)
            layout.addWidget(joint_gear_ratios[i], 2 + i, 1)
            layout.addWidget(joint_current_degrees[i], 2 + i, 2)
            layout.addWidget(angle_sliders[i], 2 + i, 3)
            layout.addWidget(readouts[i], 2 + i, 4)
            layout.addWidget(accept_btns[i], 2 + i, 5)
            layout.addWidget(encoder_pos_readouts[i], 2 + i, 6)

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

        self.accept_1.clicked.connect(
            lambda: self.set_degrees(1, self.joint_1_current_degrees_label, self.readout_1, 125, self.encoder_pos_1))
        self.accept_2.clicked.connect(
            lambda: self.set_degrees(2, self.joint_2_current_degrees_label, self.readout_2, 125, self.encoder_pos_2))
        self.accept_3.clicked.connect(
            lambda: self.set_degrees(3, self.joint_3_current_degrees_label, self.readout_3, 125, self.encoder_pos_3))
        self.accept_4.clicked.connect(
            lambda: self.set_degrees(4, self.joint_4_current_degrees_label, self.readout_4, 125, self.encoder_pos_4))
        self.accept_5.clicked.connect(
            lambda: self.set_degrees(5, self.joint_5_current_degrees_label, self.readout_5, 125, self.encoder_pos_5))
        self.accept_6.clicked.connect(
            lambda: self.set_degrees(6, self.joint_6_current_degrees_label, self.readout_6, 5, self.encoder_pos_6))
    
    def calibrate_all(self):
        # bc.calibrate_all()
        pass
     
    def angle_slider(self):
        self.joint_degree_slider = QSlider(Qt.Horizontal)
        self.joint_degree_slider.setMinimum(-27000)
        self.joint_degree_slider.setMaximum(27000)
        self.joint_degree_slider.setValue(0)

        return self.joint_degree_slider

    def input_slider_value(self, joint_slider_num, joint_readout_num):
        degree_readout = round(joint_slider_num.value()/100, 1)
        joint_readout_num.setText(str(degree_readout))

    def set_degrees(self, joint_number, joint_degrees_label, readout_value, gear_ratio, encoder_readout):
        joint_degrees_label.setText(str(readout_value.text()))
        motor_encoder_count = dc.return_counts(float(joint_degrees_label.text()), gear_ratio)
        encoder_readout.setText(str(motor_encoder_count))
        # bc.move_axis_by_count(joint_number, motor_encoder_count)

        print(f'degrees: {joint_degrees_label.text()}, \ngear ratio: {gear_ratio}, \nencoder counts: {motor_encoder_count}\n')

def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
