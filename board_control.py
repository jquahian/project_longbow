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
joint_1_calibration = [joint_1_home_pos, joint_1_max, joint_1_rest_pos]

joint_2_max = 110
joint_2_rest_pos = 30
joint_2_home_pos = 0
joint_2_calibration = [joint_2_home_pos, joint_2_max, joint_2_rest_pos]

joint_3_max = 120
joint_3_rest_pos = 0
joint_3_home_pos = 0
joint_3_calibration = [joint_3_home_pos, joint_3_max, joint_3_rest_pos]

joint_4_max = 180
joint_4_rest_pos = 0
joint_4_home_pos = 0
joint_4_calibration = [joint_4_home_pos, joint_4_max, joint_4_rest_pos]

joint_5_max = 90
joint_5_rest_pos = 0
joint_5_home_pos = 0
joint_5_calibration = [joint_5_home_pos, joint_5_max, joint_5_rest_pos]

joint_6_max = 280
joint_6_rest_pos = 90
joint_6_home_pos = 0
joint_6_calibration = [joint_6_home_pos, joint_6_max, joint_6_rest_pos]

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

def move_axis_incremental(motor_axis, num_degrees, axis_value):
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

def move_axis_absolute(motor_axis, encoder_counts):

	if motor_axis == 1:
		odrive_boards[0].axis0.controller.pos_setpoint = (joint_1_home_pos + encoder_counts)

	if motor_axis == 2:
		odrive_boards[0].axis1.controller.pos_setpoint = (joint_2_calibration[0] - encoder_counts)

	if motor_axis == 3:
		odrive_boards[1].axis0.controller.pos_setpoint = (joint_3_home_pos + encoder_counts)

	if motor_axis == 4:
		odrive_boards[1].axis1.controller.pos_setpoint = (joint_4_home_pos + encoder_counts)

	if motor_axis == 5:
		odrive_boards[2].axis0.controller.pos_setpoint = -(joint_5_home_pos - encoder_counts)

	if motor_axis == 6:
		odrive_boards[2].axis1.controller.pos_setpoint = (joint_6_calibration[0] + encoder_counts)

def move_to_saved_pos(pos_index):
	if pos_index < len(j1_pos):
		move_axis_absolute(1, j1_pos[pos_index])
		move_axis_absolute(2, j2_pos[pos_index])
		move_axis_absolute(3, j3_pos[pos_index])
		move_axis_absolute(4, j4_pos[pos_index])
		move_axis_absolute(5, j5_pos[pos_index])
		move_axis_absolute(6, j6_pos[pos_index])

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
	
def home_axis(pin_num, joint_num, gear_reduction, joint_calibration_array, direction_modifier):

	print(f'homing joint {joint_num} on pin {pin_num}.')
	arduino_board = pyfirmata.Arduino('/dev/ttyACM0')
	
	it = pyfirmata.util.Iterator(arduino_board)
	it.start()

	arduino_board.digital[pin_num].mode = pyfirmata.INPUT

	# temporary solution to not having access to the arduino's PULLUP resistor.
	# need a hardware resistsor in the circuit...
	buffer_counter = 0

	while True:
		joint_limit_status = arduino_board.digital[pin_num].read()

		# move in 2 degree incriments until we hit the limit switch
		if joint_limit_status is True:
			move_axis_incremental(joint_num, dc.return_counts(2.0, gear_reduction), 1)
		else:
			buffer_counter += 1
			if buffer_counter >= 2:
				buffer_counter = 0
				break
		
		time.sleep(0.1)
	
	print("limit reached")

	if joint_num == 1:
		joint_zero = odrive_boards[0].axis0.controller.pos_setpoint
	elif joint_num == 2:
		joint_zero = odrive_boards[0].axis1.controller.pos_setpoint
	elif joint_num == 3:
		joint_zero = odrive_boards[1].axis0.controller.pos_setpoint
	elif joint_num == 4:
		joint_zero = odrive_boards[1].axis1.controller.pos_setpoint
	elif joint_num == 5:
		joint_zero = odrive_boards[2].axis0.controller.pos_setpoint
	elif joint_num == 6:
		joint_zero = odrive_boards[2].axis1.controller.pos_setpoint
	else:
		print('invalid joint')

	# provide a + 5 degree offset for the 'zero' or minimum position of the joint
	joint_calibration_array[0] = joint_zero + (direction_modifier * dc.return_counts(5, gear_reduction))

	# move the joint to the rest position some degrees off the limit switch
	move_axis_absolute(joint_num, dc.return_counts(joint_calibration_array[2], gear_reduction))


