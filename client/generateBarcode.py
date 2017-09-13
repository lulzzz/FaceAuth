#pip3 isntall pyBarcode

import barcode
from barcode.writer import ImageWriter
from PIL import Image

ean = barcode.get('ean13', '123456789102', writer=ImageWriter())
ean.get_fullcode()
filename = ean.save('ean13')
print(filename)
image = Image.open('ean13.png')
image.show()
