from pyzbar.pyzbar import decode
from PIL import Image


#Needs a better camera and algorithm,
#https://online-barcode-reader.inliteresearch.com/
#Barcode2.png works
#barcode_4 works
#barcode3 doesn't work


print(decode(Image.open('barcode3.jpg'))) 


