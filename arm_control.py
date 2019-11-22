import pygame
import board_control as bc

bc.calibrate_all()

# initialize pygame
pygame.init()

# flag to say when the 'game' is done
done = False

# some window size
size = [300, 500]

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

# initialize the joystick
pygame.joystick.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class TextPrint:
	def __init__(self):
		self.reset()
		self.font = pygame.font.Font(None, 20)

	def print(self, screen, textString):
		textBitmap = self.font.render(textString, True, BLACK)
		screen.blit(textBitmap, [self.x, self.y])
		self.y += self.line_height
		
	def reset(self):
		self.x = 10
		self.y = 10
		self.line_height = 15
		
	def indent(self):
		self.x += 10
		
	def unindent(self):
		self.x -= 10

textPrint = TextPrint()

a_btn_down = False
b_btn_down = False
x_btn_down = False
start_btn_down = False

while done == False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True

	screen.fill(WHITE)
	textPrint.reset()
	joystick_count = pygame.joystick.get_count()

	for i in range(joystick_count):
		# initialize our joystick
		joystick = pygame.joystick.Joystick(i)
		joystick.init()

		joystick_count = pygame.joystick.get_count()
		button_count = joystick.get_numbuttons()
		axes_count = joystick.get_numaxes()
		dpad_count = joystick.get_numhats()

		textPrint.print(screen, "Joystick {}".format(i) )
		textPrint.indent()
	
		# Get the name from the OS for the controller/joystick
		name = joystick.get_name()
		textPrint.print(screen, "Joystick name: {}".format(name))
		
		# Usually axis run in pairs, up/down for one, and left/right for
		# the other.
		axes = joystick.get_numaxes()
		textPrint.print(screen, "Number of axes: {}".format(axes))
		textPrint.indent()
		
		# handle axis inputs
		for controller_axis in range(axes_count):
			axis_value = joystick.get_axis(controller_axis)
			textPrint.print(screen, "Axis {} value: {:>6.3f}".format(controller_axis, axis_value))
			
			if controller_axis == 0 and abs(axis_value) >= 0.70:
				bc.move_axis(1, bc.reduction_100, axis_value)

			if controller_axis == 1 and abs(axis_value) >= 0.70:
				bc.move_axis(2, bc.reduction_100, axis_value)

			if controller_axis == 3 and abs(axis_value) >= 0.70:
				bc.move_axis(3, bc.reduction_100, axis_value)

		# # handle the button inputs -- output is 0/1
		# for button in range(button_count):
		# 	btn_value = joystick.get_button(button)

	pygame.display.flip()

	clock.tick(60)

# to prevent the program from hanging
pygame.quit()
