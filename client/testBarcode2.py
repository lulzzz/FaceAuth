from pyzbar.pyzbar import decode
from PIL import Image
from time import time


#Needs a better camera and algorithm,
#https://online-barcode-reader.inliteresearch.com/
#Barcode2.png works
#barcode_4 works
#barcode3 doesn't work

print("Starting Decode")
startTime = time()
print(decode(Image.open('cam.png')))
endTime = time()
print(endTime - startTime)
print("Done")

