import pyfirmata
import time

board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()

board.digital[3].mode = pyfirmata.INPUT

buffer_counter = 0

while True:
    sw = board.digital[3].read()

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