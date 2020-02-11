import math

# constants

# distance from ground to joint 2 (mm)
a_1 = 391.000

# distance from joint 2 to joint 3 (mm)
a_2 = 168.742

# distance from joint 3 to orbital joint 2 (mm)
a_3 = 286.164

# distance from orbital joint 2 to orbital joint 3 (mm)
joint_6_offset = 97.918

# distance from orbital joint 3 to tool center point (TCP)
# this will be input from the GUI (mm)
tool_offset = 137.000

# variables

theta_1 = 0
theta_2 = 0
theta_3 = 0

thetas = [theta_1, theta_2, theta_3]

# need to calculate the rotations needed for the TCP to get to a specific point
# joint_6_theta = length a3, joint_6_offset + tool_center_pt, 

# i want joint 6 + tcp to be paralell at all times to the ground plane

"""
all angles are relative to vertical Z

					|
					|
					|
					|
					|
					|
					|
					|
-theta _____________________________ +theta

but in the robot, we measure relative to the home switch as zero

this needs to be translated to the same reference frame to the robot

i.e. 
- we provide a +5 degree offset from the limit switches as the zero for safety on all joints

- joint 2 rest position is 60 degrees from the switch which returns us to 90 degrees relative to the floor, or zero degrees relative to the IK axis

- rest position is +20 degrees 

"""

def cosine_law_angle(side_a, side_b, side_c):
	angle = math.acos((side_c**2 - side_a**2 - side_b**2) /
						(-2 * side_a * side_b))
	return angle

def cosine_law_length(side_a, side_b, theta):
	length = math.sqrt((side_a**2 + side_b**2) - \
						(2 * side_a * side_b * math.cos(theta)))
	return length

def to_coordinate(x, y, z):
	
	x = x -joint_6_offset

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

	print(f'absolute degrees: \njoint 2: {thetas[0]} \njoint 3: {thetas[1]} \njoint 1: {thetas[2]}')
 
	return thetas[0], thetas[1], thetas[2]

def transform_to_coordinate_frame(theta_1, theta_2, theta_3):
    pass


# set the approach coordinate to be two tool lengths away
to_coordinate(597.918 - 2 * tool_offset, 0.000, 260.000)
