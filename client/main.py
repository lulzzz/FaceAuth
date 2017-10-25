from picamera.array import PiRGBArray
from picamera import PiCamera
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
import decimal #For Float to string
import psutil
import signal # For timeouts on input
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

#Signal handeling

#class UserInputTimeoutError(Exception):
#    pass

#def handler(signum, frame):
#    rasie UserInputTimeoutError('No input from user')
    
#signal.signal(signal.SIGALRM, handler)
#signal.alarm(5)

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
    # TODO: Maybe change inoto that for loop from run.py
    print2("Running")
    blink(GREEN, 5)
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
        if GPIO.input(BUTTON_3):
            #Todo: implement event listener
            print2("Cancelling action")
        if GPIO.input(BUTTON_4):
            print2("Cancel button for add / remove user?")
            print2("Restting db")

        #If buttons 3 + 4 then reset device
            #print2("Resetting device")
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
            print2(type(known_face_encodings[0][0]))
            print2(known_face_encodings[0])
            distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            print2("Distance")
            print2(distance)
            result = face_recognition.compare_faces(known_face_encodings, face_encoding)
            nameList = list()
            print2(result)
            if True in result:
                index = -1
                print2(type(result))
                #Find spot in list that returned positive
                index = -1
                for idx, item in enumerate(result):
                    if item == True:
                        index = idx
                [print2("{}".format(name)) for is_match, name in zip(result, known_names) if is_match]
                [nameList.append(name) for is_match, name in zip(result, known_names) if is_match]
                print2(index)
               
                displayBarcode(known_names[index])
                endTime = timeBench()
                print2("Time to execute")
                print2(endTime - startTime)
                blink(GREEN,1)
            else:
                blink(RED,1)

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
        all = db.all()
        for elem in all:
            id = elem.get('Id')
            if id in known_names:
                print2("Found existing user")
            else:
                known_names.append(id)
                known_face_encodings.append(getEncodingFromDB(id))
        
        for name in known_names:
            #This is for the image directory
            if not ifUserExists(name):
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
            if len(encodings) > 1:
                click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))
            if len(encodings) == 0:
                click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                known_face_encodings.append(encodings[0])
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
            blink(YELLOW, 1)
            blink(YELLOW, 1)
            blink(YELLOW, 1)
            #Show green if registered successfully
            #Take photo of face, see if there is one and get the encoding
            camera.capture(output, format="rgb")
            face_locations = face_recognition.face_locations(output)
            face_encodings = face_recognition.face_encodings(output, face_locations)
            
            if len(face_encodings) == 1:
                if (ifUserExists(code)):
                    removeUserFromDB(code)
                addUserToDB(str(code), face_encodings[0])
                #db.insert({'Id': str(code), 'Encoding':  str(face_encodings[0])})
                known_face_encodings.append(face_encodings[0])
                known_names.append(code)
                blink(GREEN,1)
            else: # More than one or no faces found
                blink(RED,1)

def generateBarcode(number):
    #TODO: The barcode type will probably need to be a parameter as it is gym by bym basis4037456
    
    ean = barcode.get('ean13', '123456789102')
    ean.get_fullcode()
    filename = ean.save('ean13')
    image = Image.open('ea13p.svg')
    image.show()
    print2(filename)


def scanForBarcode():
    scan = input('')
    numerics = re.sub("[^[0-9]", "", scan)
    print(scan)
    return scan


def displayBarcode(barCodeInput):
    global barcodeImage
    global imageStatus

    barCodeInput = int(barCodeInput)
    ean = barcode.get('ean13', str(barCodeInput), writer=ImageWriter())
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
    print2("In Delete User")
    code = scanForBarcode()
    if (ifUserExists(code)):
        blink(GREEN, 0.5)
        removeUserFromDB(code)
    else:
        blink(RED, 0.5)
        
def float_to_str(f):
    ctx = decimal.Context()
    ctx.prec = 12
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')


def addUserToDB(name, encoding):
    print2("Adding " + str(name))
    
    stringEncoding = []
    for elem in encoding:
        
        stringEncoding.append(float_to_str(elem))
    #TODO: Make the string conversion float specific
    db.insert({'Id': str(name), 'Encoding':  stringEncoding})
    return 0

def ifUserExists(barcode):
    print2("Db search for " + str(barcode))
    if db.search(User.Id == str(barcode)):
        return True
    return False

def getEncodingFromDB(id):
    element = db.search(User.Id == str(id))
    floatList = []
    element = element[0].get('Encoding')
    for elem in element:
        
        floatList.append(float(elem))
    return floatList


#TODO: Multithread this for the main loop
def blink(color, inputTime):
    GPIO.output(color, GPIO.HIGH)
    time.sleep(inputTime)
    GPIO.output(color, False)
    time.sleep(0.5)

def cleanEncodingList(list):
    newList = []
    print2("Starting elements")
    for element in list:
        if len(element) > 0:
            #print2(element)
            stripNewLine = element.rstrip('\n')
            #print2(stripNewLine)
            newList.append(float(stripNewLine))
    return newList

def removeUserFromDB(code):
    global known_names
    global known_face_encodings
    print2("Removing user:" + str(code))
    for idx, item in enumerate(known_names):
        if code == item:
            index = idx
    del known_names[index]
    del known_face_encodings[index]
    db.remove(where('Id') == str(code))
    return 0

def print2(message):
    print(message)
    sys.stdout.flush()


def resetDatabase():
    #Might cause an issue if the file is referenced somewhere else
    os.remove('db.json')
    train()

def resetPi():
    #might be os.system('sudo shutdown -r now')
    os.system('sudo reboot -r now')


# TODO: Delete this in the future, no longer useful
# def getEncodingFromDB2(id):
#     #Right now it's one massive string, need to break into individual components of float, split by comma
#     element = db.search(User.Id == str(id))
#
#     encoding = element[0].get('Encoding')
#     #non_dec = re.compile(r'[^\d\s.]+')
#     non_dec = re.compile(r'[^-?\d\s.]+')
#     print2(type(encoding))
#     print2(encoding)
#     result = non_dec.sub('', encoding)
#     #print2("Start of Get Encoding")
#     print2("regex")
#     print2(result)
#     result2 = result.rstrip('\n')
#     result3 = result2.split(' ')
#     result4 = cleanEncodingList(result3)
#     result5 = np.asarray(result4) # To NP array
#     return result5
if  __name__ =='__main__':main()
