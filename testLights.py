import numpy as np
import RPi.GPIO as GPIO # Only works on Pi's
import time

#First set is at far end
#13, 19, 26 and G
#Second set begins 8 down from end
#9, 10, 11
# GPIO.setmode(GPIO.BOARD)
YELLOW = 13
RED = 19
GREEN = 26


GPIO.setmode(GPIO.BCM)
chan_list = [9, 10, 11]
GPIO.setup(chan_list, GPIO.OUT)
#GPIO.setup(GREEN, GPIO.OUT)
#GPIO.setup(YELLOW, GPIO.OUT)
#GPIO.setup(RED, GPIO.OUT)
while 1:

        #GPIO.output(chan_list, GPIO.HIGH)
	#GPIO.output(YELLOW, GPIO.HIGH)
	#GPIO.output(RED, GPIO.HIGH)
	#GPIO.output(GREEN, GPIO.HIGH)
	#GPIO.output(YELLOW, False)
	#GPIO.output(RED, False)
	#GPIO.output(GREEN, False)
	#GPIO.output(20, false)
        GPIO.output(chan_list, False)
        #GPIO.cleanup()
# GPIO.output(1)
