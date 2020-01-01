import odrive
import time
import serial
from odrive.enums import *

# board with axis 1, 2
board_1_num = '20873592524B'

# board with axis 3, 4
<<<<<<< HEAD
board_2_num = '387F37573437'
=======
board_2_num = '207C377E3548'
>>>>>>> c616a88913d4e1da6837ed05f91219b67f9bfcf3

# board with axis 5, 6
board_3_num = '207D37A53548'

# find the odrives
odrive_1 = odrive.find_any(serial_number=board_1_num)
odrive_2 = odrive.find_any(serial_number=board_2_num)
<<<<<<< HEAD
odrive_3 = odrive.find_any(serial_number=board_3_num)
=======
# odrive_3 = odrive.find_any(serial_number=board_3_num)
>>>>>>> c616a88913d4e1da6837ed05f91219b67f9bfcf3

odrive_boards = [odrive_1, odrive_2, odrive_3]

# calibrate odrives and set to closed loop control
def calibrate_all():	
	print('\n\nbeginning calibration...')

	for board in odrive_boards:

		print(f'\nnow calibrating {board} axis 0')
		board.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
		while board.axis0.current_state != AXIS_STATE_IDLE:
			time.sleep(0.1)

		print(f'\n{board} axis 0 in CLOSED LOOP CONTROL')
		board.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

<<<<<<< HEAD
		time.sleep(0.5)

		print(f'\nnow calibrating {board} axis 1')
=======
		time.sleep(5.0)

		print(f'\nnow calibrating board 1 axis 1')
>>>>>>> c616a88913d4e1da6837ed05f91219b67f9bfcf3
		board.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
		while board.axis1.current_state != AXIS_STATE_IDLE:
			time.sleep(0.1)

		print(f'\n{board} axis 1 in CLOSED LOOP CONTROL')
		board.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
<<<<<<< HEAD
=======
	
	time.sleep(5.0)

	print(f'\nnow calibrating board 2 axis 0')
	odrive_2.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
	while odrive_2.axis0.current_state != AXIS_STATE_IDLE:
		time.sleep(0.1)

	print(f'\nboard 2 axis 0 in CLOSED LOOP CONTROL')
	odrive_2.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
>>>>>>> c616a88913d4e1da6837ed05f91219b67f9bfcf3

	print('\n\n calibration complete')

def move_axis(motor_axis, num_degrees, axis_value):
	
	# send commands to each joint
	if motor_axis == 1:
		odrive_1.axis0.controller.pos_setpoint += (num_degrees * axis_value)
	
	if motor_axis == 2:
		odrive_1.axis1.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 3:
<<<<<<< HEAD
		odrive_2.axis0.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 4:
		odrive_2.axis1.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 5:
		odrive_3.axis0.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 6:
		odrive_3.axis1.controller.pos_setpoint += (num_degrees * axis_value)

def home_axis():
	print("HOMING AXIS")
=======
		odrive_2.axis0.controller.pos_setpoint += (num_degrees * axis_value)
>>>>>>> c616a88913d4e1da6837ed05f91219b67f9bfcf3
