# Intellivendo: Face Recognition Project
This project is an open source solution to help traditional retailers compete against intelligent competators. 

## Directory structure
- Client: Raspberry pi code
- hardware: 3D printed models
- Libraries: Support for the face recognition
- testData: Example images to be used for examples

## Operating
Run the following to execute the program
``` sudo python3 client/main.py ```
Sudo is required for the barcode scanner to work.

## Hardware required
- Raspberry pi 3+ (https://www.amazon.com/gp/product/B01CD5VC92/)
- Raspberry pi camrea (https://www.amazon.com/gp/product/B01ER2SKFS)
- 3D Model - Provided in hardware directory
- Barcode scanner (https://www.amazon.com/gp/product/B01LXNM0Y1)
- Lights (https://www.amazon.com/gp/product/B00RIIGD30)
- Key pad - https://www.amazon.com/gp/product/B00OKCRZ70
- LED Display - (https://www.tinydeal.com/5-inch-lcd-hdmi-touch-screen-800-x-480-for-raspberry-pi-3-model-b-p-164014.html)
- SD Card (https://www.amazon.com/gp/product/B0143RT8OY)
- Pi wires (https://www.amazon.com/gp/product/B01LZF1ZSZ/)

## Libraries
- https://github.com/ageitgey/face_recognition
- TinyDB
- barcode (https://pypi.org/project/python-barcode/)