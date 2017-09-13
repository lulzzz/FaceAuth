from picamera.array import PiRGBArray
from picamera import PiCamera
from pyzbar.pyzbar import decode
import barcode
import face_recognition
import os
import re
import time
import sys
import click
import numpy as np
import RPi.GPIO as GPIO # Only works on Pi's
import time
from tinydb import TinyDB, Query
#import barcode on generate part
# Lights tutorial
# http://lowvoltagelabs.com/products/pi-traffic/

BUTTON_1 = 9
BUTTON_2 = 10
BUTTON_3 = 12 # Doesn't currently work, need to use a different port
BUTTON_4 = 11

GREEN = 26
YELLOW = 13
RED = 19

db = None
User = None

def main():
    #Setup
    global db
    global User 
    db = TinyDB('db.json')
    User = Query()
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    output = np.empty((240, 320, 3), dtype=np.uint8)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(YELLOW, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print2("Setup complete")
    train()

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
        face_locations = face_recognition.face_locations(output)
        face_encodings = face_recognition.face_encodings(output, face_locations)
        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
        #    # See if the face is a match for the known face(s)
            result = face_recognition.compare_faces(known_face_encodings, face_encoding)
            nameList = list()
            if True in result:
                [print2("{}".format(name)) for is_match, name in zip(result, known_names) if is_match]
                [nameList.append(name) for is_match, name in zip(result, known_names) if is_match]
                displayBarcode(getBarcode(name))

            #TODO: Display Bar code through screen
         #   print (nameList)

# Param: IP, if null then look locally
#
def train(ip = 0):
    print2("Start train")
    if ip == 0:
        known_names, known_face_encodings = scan_known_people(os.getcwd() + "/../database/")
        # Loop through known_names, if not found then add the new known_name and known_face_encoding
        print2(type(known_names[0]))
        print2(known_names)
        for name in known_names:
            if not db.search(User.Name == name):
                print2(name)
                print2(known_face_encodings[known_names.index(name)])
                addUserToDB(name, known_face_encodings[known_names.index(name)])
                
    else:
        # Connect to DB
        print2(" Connectiong to DB ")
    print2(" Training complete ")

# TODO: Convert this into loading a csv/db file of param points
def scan_known_people(known_people_folder):
    print2("Loading faces")
    known_names = []
    known_face_encodings = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = face_recognition.load_image_file(file)
        print2("Starting encoding! ")
        encodings = face_recognition.face_encodings(img)
        print2(" Ending encoding! ")
        if len(encodings) > 1:
            click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))

        if len(encodings) == 0:
            click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            known_names.append(basename)
            known_face_encodings.append(encodings[0])
        print2(" Processed a face! ")
        
    return known_names, known_face_encodings

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def newUser():
    # While button pressed is true  
    while GPIO.input(BUTTON_1):
        barcode = scanForBarcode()
        if barcode != -1:
            GPIO.output(YELLOW, GPIO.HIGH)
            time.sleep(.5)
            GPIO.output(YELLOW, False)
            time.sleep(.5)
            GPIO.output(YELLOW, GPIO.HIGH)
            time.sleep(.5)
            GPIO.output(YELLOW, False)
            time.sleep(.5)
            GPIO.output(YELLOW, GPIO.HIGH)
            time.sleep(.5)
            GPIO.output(YELLOW, False)
            time.sleep(.5)
            #Take photo
            #TODO: This
            # Show green if registered successfully
            barcode = scanForBarCode()
            if barcode > 0:
                #db.insert({'Name': str(name), 'Encoding':  str(known_face_encodings[known_names.index(name)])})
                GPIO.output(GREEN, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(GREEN, False)
            # Show red if not registered successfully
            #GPIO.output(RED, GPIO.HIGH)

def generateBarcode(number):
    #TODO: The barcode type will probably need to be a parameter as it is gym by bym basis
    ean = barcode.get('ean13', '123456789102')
    ean.get_fullcode()
    filename = ean.save('ean13')
    image = Image.open('ea13.svg')
    image.show()
    print(filename)

def getBarcode(name):
    #TODO: Go through DB and find barcode associated with name
    return -1
    

def scanForBarcode():
    #TODO: Take images look for barcode
    print (" Not implemented yet ")
    #decode(output)
    return 1

def displayBarcode(barcode):
    ean = barcode.get('ean13', barcode, writer=ImageWriter())
    ean.get_fullcode()
    filename = ean.save('ean13')
    print(filename)
    image = Image.open('ean13.png')
    image.show()
    # Delete image file?
    
def deleteUser():
    # While button pressed is true
    if GPIO.input():
        print (" Not implemented yet ")

def addUserToDB(name, encoding):
    db.insert({'Name': str(name), 'Encoding':  str(encoding)})
    return 0

def ifUserExists(name):
    if db.search(User.name == str(name)):
        return True;
    return False:

def removeUserFromDB(user):
    db.delete(str(user))
    return 0

def print2(message):
    print(message)
    sys.stdout.flush()
    

if  __name__ =='__main__':main()

# For shutdown/restart button
# import os
# os.system('sudo shutdown -r now')
