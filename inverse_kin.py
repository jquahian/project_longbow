import math

# constants

# distance from ground to joint 2 (mm)
a_1 = 307.787

# distance from joint 2 to joint 3 (mm)
a_2 = 168.742

# distance from joint 3 to orbital joint 2 (mm)
a_3 = 286.176

# distance from orbital joint 2 to orbital joint 3 (mm)
joint_6_offset = 97.905

# distance from orbital joint 3 to tool center point (TCP)
# this will be input from the GUI (mm)
tool_offset = 137.000

# variables
theta_1 = 0
theta_2 = 0
theta_3 = 0

thetas = [theta_1, theta_2, theta_3]

joint_2_delta = 0
joint_3_delta = 0
joint_6_delta = 0

deltas = [joint_2_delta, joint_3_delta, joint_6_delta]

def cosine_law_angle(side_a, side_b, side_c):
	angle = math.acos((side_c**2 - side_a**2 - side_b**2) /
						(-2 * side_a * side_b))
	return angle

def cosine_law_length(side_a, side_b, theta):
	length = math.sqrt((side_a**2 + side_b**2) - \
						(2 * side_a * side_b * math.cos(theta)))
	return length


def to_coordinate(joint_2_origin_angle, joint_2_3_angle, joint_3_6_angle, x, y, z, approach):

	r_1 = math.sqrt(x**2 + z**2)

	phi_1 = math.atan(z / x)
	phi_2 = math.radians(90) - phi_1

	r_2 = cosine_law_length(r_1, a_1, phi_2)

	phi_3 = cosine_law_angle(a_1, r_2, r_1)
	phi_4 = cosine_law_angle(r_2, a_2, a_3)

	thetas[0] = math.radians(180) - (phi_3 + phi_4)
	thetas[1] = cosine_law_angle(a_2, a_3, r_2)

	# first revolute joint on x-z plane
	thetas[0] = round(math.degrees(thetas[0]), 2)

	# second revolute joint on x-z plane
	thetas[1] = round(math.degrees(thetas[1]), 2)

	# base joint - first revolute joint on x-y plane
	thetas[2] = round(math.degrees(math.asin(y / x)), 2)

	# print(f'joint 2: {thetas[0]} \njoint 3: {thetas[1]} \njoint 1: {thetas[2]}')

	calculate_deltas(
		joint_2_origin_angle, joint_2_3_angle, joint_3_6_angle, thetas[0], thetas[1], thetas[2], approach)

def calculate_deltas(joint_2_origin_angle, joint_2_3_angle, joint_3_6_angle, theta_1, theta_2, theta_3, approach):
	# joint 2 always relative to vertical z which will never change.
	# theta_1 is now the new angle for joint 2 apply it to the current joint position
	deltas[0] = theta_1
	deltas[0] = round(deltas[0], 3)

	# joint 3 is relative to joint 2
	# take the required delta, subtract it from the current delta and apply it to the current joint position
	deltas[1] = theta_2 - joint_2_3_angle
	deltas[1] = round(deltas[1], 3)

	# joint 6 delta is going to depend on the approach that we want
	# if parallel or perpendicular to the ground plane, we can calculate it based on the vertical axis which will never change
	if approach == 'parallel':
		deltas[2] = (theta_2 - theta_1) - 90
	elif approach == 'perpendicular':
		deltas[2] = (theta_2 - theta_1)
	
	deltas[2] = round(deltas[2], 3)

	print(
		f'\ndelta joint 2: {deltas[0]} \ndelta joint 3: {deltas[1]} \ndelta joint 6: {deltas[2]}')
 
	return deltas[0], deltas[1], deltas[2]
