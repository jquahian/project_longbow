import pyfirmata
import time

"""
pin 2 = joint 1
pin 3 = joint 2
pin 4 = joint 3
pin 5 = joint 4
pin 6 = joint 5
pin 7 = joint 6
"""

pin = 2

port = 0

board = pyfirmata.Arduino(f'/dev/ttyACM{str(port)}')
it = pyfirmata.util.Iterator(board)
it.start()

board.digital[pin].mode = pyfirmata.INPUT

buffer_counter = 0

while True:
    sw = board.digital[pin].read()
    
    if sw is True:
        print("HIGH")
    else:
        buffer_counter += 1
        print(buffer_counter)
        if buffer_counter >= 2:
            print("LOW")
            buffer_counter = 0
            break
        
    
    time.sleep(0.1)