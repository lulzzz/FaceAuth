from picamera.array import PiRGBArray
from picamera import PiCamera
from pyzbar.pyzbar import decode
from barcode.writer import ImageWriter
from tinydb import where
from PIL import Image
from time import time as timeBench
import picamera
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
import random
import psutil
from tinydb import TinyDB, Query
#import barcode on generate part
# Lights tutorial
# http://lowvoltagelabs.com/products/pi-traffic/

BUTTON_1 = 9
BUTTON_2 = 10
BUTTON_3 = 7
BUTTON_4 = 11

GREEN = 26
YELLOW = 13
RED = 19

known_face_encodings = None
known_names = None

camera = None

db = None
User = None

def main():
    #Setup
    global db
    global User
    global known_face_encodings
    global known_names
    global camera
    name = None
    db = TinyDB('db.json')
    User = Query()
    camera = PiCamera()
    #camera.resolution = (640, 480)
    camera.resolution = (320, 240)
    camera.framerate = 32
    #rawCapture = PiRGBArray(camera, size=(640, 480))
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
    print2("Running")
    while True:
        #print2(known_names)
        #print2(known_face_encodings)
        # http://razzpisampler.oreilly.com/ch07.html
        # Global Try
            # Evnts checked
        if GPIO.input(BUTTON_1):
            newUser()
        if GPIO.input(BUTTON_2):
            deleteUser()
        # Start recongize face
        camera.capture(output, format="rgb")
        getEncodingStart = timeBench()
        face_locations = face_recognition.face_locations(output)
        face_encodings = face_recognition.face_encodings(output, face_locations)
        getEncodingFinish = timeBench()
        print2("Time to calculate initial encodings")
        print2(getEncodingFinish - getEncodingStart)
        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            startTime = timeBench()
            distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            print2("Distance")
            print2(distance)
            result = face_recognition.compare_faces(known_face_encodings, face_encoding)
            nameList = list()
            print2(result)
            if True in result:
                [print2("{}".format(name)) for is_match, name in zip(result, known_names) if is_match]
                [nameList.append(name) for is_match, name in zip(result, known_names) if is_match]
                displayBarcode(getBarcode(name))
                endTime = timeBench()
                print2("Time to execute")
                print2(endTime - startTime)

                #TODO: Display Bar code through screen
            #output.truncate(0)

# Param: IP, if null then look locally
#
def train(ip = 0):
    print2("Start training")
    global known_names
    global known_face_encodings
    if ip == 0:
        known_names, known_face_encodings = scan_known_people(os.getcwd() + "/../database/")
        # Loop through known_names, if not found then add the new known_name and known_face_encoding
        print2(known_names)
        print2("DB ALL")
        #print2(db.all())
        all = db.all()
        print2(type(all))
        print2(all[0])
        print2(all[1])
        print2(type(all[0]))
        print2(dir(all[0]))
        print2(all[0].get('Id'))
        for elem in all:
            id = elem.get('Id')
            known_names.append(id)
            known_face_encodings.append(getEncodingFromDB(id))
        
        for name in known_names:
            if not db.search(User.Id == name):
                print2(name)
                print2(known_face_encodings[known_names.index(name)])
                addUserToDB(name, known_face_encodings[known_names.index(name)])
                
    else:
        # Connect to DB
        print2(" Connectiong to DB ")
    print2(" Training complete ")


def scan_known_people(known_people_folder):
    print2("Loading faces")
    global known_names
    global known_face_encodings
    known_names = []
    known_face_encodings = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = face_recognition.load_image_file(file) 
        if not ifUserExists(basename):
            print2("New User")
            print2(basename)
            encodings = face_recognition.face_encodings(img)
            print2(encodings)
            print2(" Ending encoding! ")
            if len(encodings) > 1:
                click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))
            if len(encodings) == 0:
                click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                known_face_encodings.append(encodings[0])
            print2(" Processed a face! ")
        else:
            known_names.append(basename)
            known_face_encodings.append(getEncodingFromDB(basename))
        
    return known_names, known_face_encodings

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def newUser():
    # While button pressed is true
    global camera
    output = np.empty((240, 320, 3), dtype=np.uint8)
    print2("Adding a new user")
    while GPIO.input(BUTTON_1):
        code = scanForBarcode()
        if code != -1:
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
            #Show green if registered successfully
            #Take photo of face, see if there is one and get the encoding
            camera.capture(output, format="rgb")
            face_locations = face_recognition.face_locations(output)
            face_encodings = face_recognition.face_encodings(output, face_locations)
            
            if len(face_encodings) == 1:
                db.insert({'Id': str(code), 'Encoding':  str(face_encodings[0])})
                known_face_encodings.append(face_encodings[0])
                known_names.append(code)
                GPIO.output(GREEN, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(GREEN, False)
            else: # More than one or no faces found
                GPIO.output(RED, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(RED, Fals)

def generateBarcode(number):
    #TODO: The barcode type will probably need to be a parameter as it is gym by bym basis
    ean = barcode.get('ean13', '123456789102')
    ean.get_fullcode()
    filename = ean.save('ean13')
    image = Image.open('ea13p.svg')
    image.show()
    
    print2(filename)

def getBarcode(name):
    #TODO: Go through DB and find barcode associated with name
    return -1
    

def scanForBarcode():
    #TODO: Take images look for barcode
    print2(" Not implemented yet ")
    barcode = random.randint(0,1000000)
    return barcode#decode(output)

def displayBarcode(code):
    global barcodeImage
    global imageStatus
    code = 123456789102 #TODO: CHANGE THIS!
    ean = barcode.get('ean13', str(code), writer=ImageWriter())
    ean.get_fullcode()
    filename = ean.save('ean13')
    print2(filename)
    #To do replace with process handling
    image = Image.open('ean13.png')
    image.show()
    time.sleep(2)
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()
    print2("Close completed")
    # Delete image file?
    
def deleteUser():
    # While button pressed is true
    if GPIO.input():
        print (" Not implemented yet ")

def addUserToDB(name, encoding):
    db.insert({'Id': str(name), 'Encoding':  str(encoding)})
    return 0

def ifUserExists(name):
    print2("Db search for " + str(name))
    if db.search(User.Id == str(name)):
        return True
    return False

def getEncodingFromDB(id):
    #Right now it's one massive string, need to break into individual components of float, split by comma
    element = db.search(User.Id == str(id))
    encoding = element[0].get('Encoding')
    #non_dec = re.compile(r'[^\d\s.]+')
    non_dec = re.compile(r'[^-?\d\s.]+')
    result = non_dec.sub('', encoding)
    #print2("Start of Get Encoding")
    print2("regex")
    print2(result)
    result2 = result.rstrip('\n')
    result3 = result2.split(' ')
    #print2(type(result2))
    #Result 3 is a list with some incorrect values
    #print2(result3)
    result4 = cleanEncodingList(result3)
    result5 = np.asarray(result4) # To NP array
    return result5

def cleanEncodingList(list):
    newList = []
    print2("Starting elements")
    for element in list:
        if len(element) > 0:
            #print2(element)
            stripNewLine = element.rstrip('\n')
            #print2(stripNewLine)
            newList.append(float(stripNewLine))
    #print2(len(newList))        
    #print2(newList)
    #print2(type(newList[3]))
    return newList

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
