import numpy as np
import RPi.GPIO as GPIO
import time

# On normal config 26 is 2 and 4 at the same time, 6 is the 2 button, 19 is 1 and 2

GPIO.setmode(GPIO.BCM)

#GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#GPIO.setup(test, GPIO.IN)
#GPIO.setup(5, GPIO.IN)
#GPIO.setup(6, GPIO.IN)

#chan_list = [13, 19, 26, 6]
#22 10 9 11 ground
#chan_list = 22
#one = 22
#two = 10
#three = 11
#four = 9
one = 9
two = 10
#three = 12
three = 7
four = 11
GPIO.setup(one, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(two, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(three, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(four, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#print (chan_list)
while True:
    
    if GPIO.input(one):
        print("1: input was high")
    if GPIO.input(two):
        print("2: input was high")
    if GPIO.input(three):
        print("3: input was high")
    if GPIO.input(four):
        print("4: input was high")
    #else:
     #   print("input was low")


GPIO.cleanup()
