from picamera.array import PiRGBArray
from picamera import PiCamera
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np


# Camera works, trust me
#Setup
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
#camera.capture('myphoto.jpg')
# While loop to capture until barcode is found
barcode = []
while len(barcode) == 0:
    rawCapture = PiRGBArray(camera, size=(640, 480))
    output = np.empty((240, 320, 3), dtype=np.uint8)
    
    print(decode(output))
    barcode = decode(output)
##print (decode(Image.open('myphoto.jpg')))
print (barcode)
print(barcode[0][0])
print("Found one!")

#print (output)