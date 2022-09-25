import time
import json
import os
import base64
import requests
import RPi.GPIO as GPIO
from picamera import PiCamera

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)

camera = PiCamera()
time.sleep(2)

camera.capture("newpic.jpg")

def call_api(file):
    url = 'https://m25fu6wmrv4v2aklwzxt4qbgpq0mmiws.lambda-url.us-east-1.on.aws/'
    image_file = open(file, "rb")
    image_data_binary = image_file.read()
    image_data = (base64.b64encode(image_data_binary)).decode('ascii')
    headers = {'Content-type': 'text/plain; charset=utf-8'}
    r = requests.post(url, headers=headers, data=image_data)
    print(r.content)

call_api("newpic.jpg")
GPIO.output(4, GPIO.HIGH)
