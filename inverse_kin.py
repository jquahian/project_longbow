import math

# this is for 3 DOF rotation along the Y axis
# link lengths
a_1 = 200
a_2 = 150
a_3 = 150

def cosine_law_angle(side_a, side_b, side_c):
	angle = math.acos((side_c**2 - side_a**2 - side_b**2) / (-2 * side_a * side_b))
	return angle

def cosine_law_length(side_a, side_b, theta):
	length = math.sqrt((side_a**2 + side_b**2) - (2 * side_a * side_b * math.cos(theta)))
	return length

def to_coordinate(x, y, z):
	r_1 = math.sqrt(x**2 + z**2)
	
	phi_1 = math.atan(z / x)
	phi_2 = math.radians(90) - phi_1
	
	r_2 = cosine_law_length(r_1, a_1, phi_2)
	
	phi_3 = cosine_law_angle(a_1, r_2, r_1)
	phi_4 = cosine_law_angle(r_2, a_2, a_3)
	
	theta_1 = math.radians(180) - (phi_3 + phi_4)
	theta_2 = cosine_law_angle(a_2, a_3, r_2)

	# first revolute joint on x-z plane
	theta_1 = round(math.degrees(theta_1), 2)

	# second revolute joint on x-z plane
	theta_2 = round(math.degrees(theta_2), 2)

	# base joint - first revolute joint on x-y plane
	theta_3 = round(math.degrees(math.asin(y / x)), 2)
	
	print(theta_1, theta_2, theta_3)

	return theta_1, theta_2, theta_3

to_coordinate(12, 10, 10)
