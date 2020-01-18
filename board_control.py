import odrive
import time
import serial
from odrive.enums import *

# board with axis 1, 2
board_1_num = '20873592524B'

# board with axis 3, 4
board_2_num = '387F37573437'

# board with axis 5, 6
board_3_num = '207D37A53548'

odrive_1 = 0
odrive_2 = 0
odrive_3 = 0

odrive_boards = []

def connect_to():
	global odrive_1	
	global odrive_2	
	global odrive_3
	global odrive_boards

	# find the odrives
	odrive_1 = odrive.find_any(serial_number = board_1_num)
	odrive_2 = odrive.find_any(serial_number = board_2_num)
	odrive_3 = odrive.find_any(serial_number = board_3_num)

	odrive_boards = [odrive_1, odrive_2, odrive_3]

# calibrate odrives and set to closed loop control
def calibrate_all():
	global odrive_boards
	
	print('\n\nbeginning calibration...')

	for board in odrive_boards:

		print(f'\nnow calibrating {board} axis 0')
		board.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
		while board.axis0.current_state != AXIS_STATE_IDLE:
			time.sleep(0.1)

		print(f'\n{board} axis 0 in CLOSED LOOP CONTROL')
		board.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

		time.sleep(0.5)

		print(f'\nnow calibrating {board} axis 1')
		board.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
		while board.axis1.current_state != AXIS_STATE_IDLE:
			time.sleep(0.1)

		print(f'\n{board} axis 1 in CLOSED LOOP CONTROL')
		board.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

	print('\n\n calibration complete')

def move_axis(motor_axis, num_degrees, axis_value):
	global odrive_boards

	# send commands to each joint by degrees
	if motor_axis == 1:
		odrive_boards[0].axis0.controller.pos_setpoint += (num_degrees * axis_value)
	
	if motor_axis == 2:
		odrive_boards[0].axis1.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 3:
		odrive_boards[1].axis0.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 4:
		odrive_boards[1].axis1.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 5:
		odrive_boards[2].axis0.controller.pos_setpoint += (num_degrees * axis_value)

	if motor_axis == 6:
		odrive_boards[2].axis1.controller.pos_setpoint += (num_degrees * axis_value)

def move_axis_by_count(motor_axis, encoder_counts):
	global odrive_boards

	if motor_axis == 1:
		odrive_boards[0].axis0.controller.pos_setpoint = encoder_counts

	if motor_axis == 2:
		odrive_boards[0].axis1.controller.pos_setpoint = -encoder_counts

	if motor_axis == 3:
		odrive_boards[1].axis0.controller.pos_setpoint = encoder_counts

	if motor_axis == 4:
		odrive_boards[1].axis1.controller.pos_setpoint = encoder_counts

	if motor_axis == 5:
		odrive_boards[2].axis0.controller.pos_setpoint = -encoder_counts

	if motor_axis == 6:
		odrive_boards[2].axis1.controller.pos_setpoint = encoder_counts
	
def home_axis():
	print("HOMING AXIS")
