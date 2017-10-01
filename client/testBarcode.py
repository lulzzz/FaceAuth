from picamera.array import PiRGBArray
from picamera import PiCamera
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np
import io
import time
#import picamera

# Camera works, trust me
#Setup
camera = PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32
#camera.capture('myphoto.jpg')
# While loop to capture until barcode is found
barcode = []
stream = io.BytesIO()
while True:
    #rawCapture = PiRGBArray(camera, size=(640, 480))
    #rawCapture = PiRGBArray(camera, size=(320, 240))
    #output = np.empty((240, 320, 3), dtype=np.uint8)
    #camera.start_preview() #This will not quit
    time.sleep(2)
    camera.capture(stream, format='jpeg')
    image = Image.open(stream)
    #stream.seek(0)
    
##print (decode(Image.open('myphoto.jpg')))
#print (barcode)
stream.seek(0)
image = Image.open(stream)
#print(barcode[0][0])
#print("Found one!")

#print (output)