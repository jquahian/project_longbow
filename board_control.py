import odrive
import time
import serial
import pyfirmata
import degrees_calc as dc
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

j1_pos = []
j2_pos = []
j3_pos = []
j4_pos = []
j5_pos = []
j6_pos = []

odrive_boards = [odrive_1, odrive_2, odrive_3]

joint_1_max = 180
joint_1_rest_pos = 0
joint_1_home_pos = 0

joint_2_max = 110
joint_2_rest_pos = 30
joint_2_home_pos = 0

joint_3_max = 120
joint_3_rest_pos = 0
joint_3_home_pos = 0

joint_4_max = 180
joint_4_rest_pos = 0
joint_4_home_pos = 0

joint_5_max = 90
joint_5_rest_pos = 0
joint_5_home_pos = 0

joint_6_max = 360
joint_6_rest_pos = 0
joint_6_home_pos = 0

def connect_to():
	# global odrive_boards

	# find the odrives
	odrive_boards[0] = odrive.find_any(serial_number=board_1_num)
	odrive_boards[1] = odrive.find_any(serial_number=board_2_num)
	odrive_boards[2] = odrive.find_any(serial_number=board_3_num)

	# odrive_boards = [odrive_1, odrive_2, odrive_3]

# calibrate odrives and set to closed loop control
def calibrate_all():
	# global odrive_boards
	
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
	global joint_2_home_pos

	if motor_axis == 1:
		odrive_boards[0].axis0.controller.pos_setpoint = (joint_1_home_pos + encoder_counts)

	if motor_axis == 2:
		odrive_boards[0].axis1.controller.pos_setpoint = (joint_2_home_pos - encoder_counts)

	if motor_axis == 3:
		odrive_boards[1].axis0.controller.pos_setpoint = (joint_3_home_pos + encoder_counts)

	if motor_axis == 4:
		odrive_boards[1].axis1.controller.pos_setpoint = (joint_4_home_pos + encoder_counts)

	if motor_axis == 5:
		odrive_boards[2].axis0.controller.pos_setpoint = -(joint_5_home_pos - encoder_counts)

	if motor_axis == 6:
		odrive_boards[2].axis1.controller.pos_setpoint = (joint_6_home_pos + encoder_counts)

def move_to_saved_pos(pos_index):
	if pos_index < len(j1_pos):
		odrive_boards[0].axis0.controller.pos_setpoint = j1_pos[pos_index]
		odrive_boards[0].axis1.controller.pos_setpoint = -j2_pos[pos_index]
		odrive_boards[1].axis0.controller.pos_setpoint = j3_pos[pos_index] 
		odrive_boards[1].axis1.controller.pos_setpoint = j4_pos[pos_index] 
		odrive_boards[2].axis0.controller.pos_setpoint = -j5_pos[pos_index] 
		odrive_boards[2].axis1.controller.pos_setpoint = j6_pos[pos_index]
		time.sleep(0.1)

		# need to take a look at a better way to tell if it's at the correct point...
		while abs(odrive_boards[0].axis0.encoder.vel_estimate) >= 300 or\
				abs(odrive_boards[0].axis1.encoder.vel_estimate) >= 300 or\
				abs(odrive_boards[1].axis0.encoder.vel_estimate) >= 300 or\
				abs(odrive_boards[1].axis1.encoder.vel_estimate) >= 300 or\
				abs(odrive_boards[2].axis0.encoder.vel_estimate) >= 300 or\
				abs(odrive_boards[2].axis1.encoder.vel_estimate) >= 300:
			time.sleep(0.1)
		else:
			move_to_saved_pos(pos_index + 1)  
	else:
		print('final point reached')
	
def home_axis():
	global joint_2_rest_pos
	global joint_2_home_pos

	print('homing all joints')
	arduino_board = pyfirmata.Arduino('/dev/ttyACM0')
	
	it = pyfirmata.util.Iterator(arduino_board)
	it.start()

	arduino_board.digital[7].mode = pyfirmata.INPUT

	buffer_counter = 0

	while True:
		joint_2_limit = arduino_board.digital[7].read()

		# move in 2 degree incriments until we hit the limit switch
		if joint_2_limit is True:
			move_axis(2, dc.return_counts(2.0, 125), 1)
		else:
			buffer_counter += 1
			if buffer_counter >= 2:
				buffer_counter = 0
				break
		
		time.sleep(0.1)
	
	print("limit reached")

	# provide a + 10 degree offset for the 'zero' or minimum position of the joint
	joint_2_home_pos = odrive_boards[0].axis1.controller.pos_setpoint - dc.return_counts(10, 125)
	
	move_axis_by_count(2, dc.return_counts(joint_2_rest_pos, 125))

	print(joint_2_home_pos)	
