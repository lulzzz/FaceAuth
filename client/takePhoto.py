from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview(alpha=200)
sleep(5)
camera.capture('myphoto.jpg')
camera.stop_preview()

