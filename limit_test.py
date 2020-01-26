import pyfirmata
import time

board = pyfirmata.Arduino('/dev/ttyACM0')
it = pyfirmata.util.Iterator(board)
it.start()

board.digital[7].mode = pyfirmata.INPUT

counter = 0

while True:
    sw = board.digital[7].read()

    if sw is True:
        print(counter)
    else:
        counter += 1
        if counter >=2:
            print("LOW")
            break
    
    time.sleep(0.1)