import RPi.GPIO as GPIO
import os
import sys
from Adafruit_IO import Client


AioKey="96df5edd973a4e30a389a03b8294957d"
FanPin=19
PumpPin=20
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FanPin,GPIO.OUT)
GPIO.setup(PumpPin,GPIO.OUT)


while True:
 aio = Client(AioKey)
 ValueOne = aio.receive('On Fan')
 print('Received value: {0}'.format(ValueOne.value)) 
 ValueTwo = aio.receive('On Pump')
 print('Received value: {0}'.format(ValueTwo.value))
 if (ValueOne.value == '1'):
     print"fan On"
     GPIO.output(FanPin,GPIO.LOW)
 if (ValueOne.value == '0'):
     print"fan Off"
     GPIO.output(FanPin,GPIO.HIGH)
 if (ValueTwo.value == '1'):
     print"Pump On"
     GPIO.output(PumpPin,GPIO.LOW)
 if (ValueTwo.value == '0'):
     print"Pump Off"
     GPIO.output(FanPin,GPIO.HIGH)


      
