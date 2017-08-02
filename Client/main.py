from picamera.array import PiRGBArray
from picamera import PiCamera
import face_recognition
import os
import re
import time
import sys
import click
import numpy as np
import RPi.GPIO as GPIO # Only works on Pi's
import time
#import barcode on generate part
# Lights tutorial
# http://lowvoltagelabs.com/products/pi-traffic/

BUTTON_1 = 1
BUTTON_2 = 2

GREEN_LIGHT = 3
YELLOW_LIGHT = 4
RED_LIGHT = 5

def main():
    #Setup
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    output = np.empty((240, 320, 3), dtype=np.uint8)
    train()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Recognize faces
    # TODO: Maybe change into that for loop from run.py
    while True:
        # http://razzpisampler.oreilly.com/ch07.html
        # Global Try
            # Evnts checked
        if GPIO.input(BUTTON_1):
            newUser()
        if GPIO.input(BUTTON_2):
            deleteUser()
        # Start recongize face
        camera.capture(output, format="rgb")
        # Finds faces
        face_locations = face_recognition.face_locations(output)
        face_encodings = face_recognition.face_encodings(output, face_locations)
        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            result = face_recognition.compare_faces(known_face_encodings, face_encoding)
            nameList = list()
            if True in result:
                [print("{}".format(name)) for is_match, name in zip(result, known_names) if is_match]
                [nameList.append(name) for is_match, name in zip(result, known_names) if is_match]

            #TODO: Display Bar code through screen
            print (nameList)

# Param: IP, if null then look locally
#
def train(ip = 0):
    if ip == 0:
        known_names, known_face_encodings = scan_known_people(os.getcwd() + "/../database/")
    else:
        # Connect to DB
        print (" Connectiong to DB ")
    print(" Training complete ")
    sys.stdout.flush()

# TODO: Convert this into loading a csv/db file of param points
def scan_known_people(known_people_folder):
    print ("Loading faces")
    sys.stdout.flush()
    known_names = []
    known_face_encodings = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 1:
            click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))

        if len(encodings) == 0:
            click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            known_names.append(basename)
            known_face_encodings.append(encodings[0])

    return known_names, known_face_encodings

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def newUser():
    # While button pressed is true
    while GPIO.input(BUTTON_1):
        barcode = scanForBarcode()
        if barcode != -1:
            GPIO.output(YELLOW_LIGHT)
            time.sleep(.5)
            GPIO.output(YELLOW_LIGHT)
            time.sleep(.5)
            GPIO.output(YELLOW_LIGHT)
            time.sleep(.5)
            #Take photo
            #TODO: This
            # Show green if registered successfully
            GPIO.output(GREEN_LIGHT, GPIO.HIGH)
            # Show red if not registered successfully
            GPIO.output(RED_LIGHT, GPIO.HIGH)


def scanForBarcode():
    #TODO :
    print (" Not implemented yet ")

def deleteUser():
    # While button pressed is true
    if GPIO.input():
        print (" Not implemented yet ")

if  __name__ =='__main__':main()

# For shutdown/restart button
# import os
# os.system('sudo shutdown -r now')