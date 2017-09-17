import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import math
import numpy
import os
import sys
import urllib2
from Adafruit_IO import Client



ThingSpeakAPI = "PDI7070UUTOAA4N2"
AdaFruitAIO="e3cd68fbc4ee4a5297c0ecdaed8755c3"

QueueSizeTemp = 10
CurPosTemp = 0

QueueSizeHumidity = 10
CurPosHumidity = 0

############################################################
# Arrays for moving average over last few samples
############################################################
QueueTemp = []
QueueHumid = []

#def Enqueue(QueueName, NewElement, Size, CurrPos):
# print 'NewElement=%d, Size=%d, CurrPos=%d' % (NewElement, Size, CurrPos)

def EnqueueTemp(NewElement):
 global QueueSizeTemp, CurPosTemp, QueueTemp

 QueueTemp[CurPosTemp]=NewElement 
 CurPosTemp += 1
 CurPosTemp %= QueueSizeTemp

def EnqueueHumidity(NewElement):
 global QueueSizeHumidity, CurPosHumidity, QueueHumid

 QueueHumid[CurPosHumidity]=NewElement 
 CurPosHumidity += 1
 CurPosHumidity %= QueueSizeHumidity
 
def calculateTempAverage():
 global CurrentTemp
 global QueueTemp

 CurrentTemp = sum(QueueTemp) / float(len(QueueTemp))
 print '%s temp average=%d' % (getTimestamp(), CurrentTemp)
 print 'Temperature list ', QueueTemp
 return;

def calculateHumidAverage():
 global CurrentHumid
 global QueueHumid

 CurrentHumid = sum(QueueHumid) / float(len(QueueHumid))
 print '%s humidity average=%d' % (getTimestamp(), CurrentHumid)
 print 'Humidity list ', QueueHumid
 return;
                                                                                                                                                                  
MotorMode = "SENSOR"

GPIO.setmode(GPIO.BCM)

CurrentTemp = 0 #FIXME
CurrentHumid = 0 #FIXME

TemperatureThreshold = 0
HumidityThreshold = 0

TempOffset = 14
HumidOffset = -100

GPIOFan=19
GPIOPump=20
GPIODHT=4
GPIOSoilMoisture=26

Debug = True

def getTimestamp():
 CurTime = time.asctime(time.localtime(time.time()))
 return CurTime;
 

def debugPrint(message):
 global Debug

 if Debug == True:
  print   getTimestamp(), message
  
 return;

def setMotorMode(mode):
 global MotorMode 
 MotorMode = mode
 return;

# Initialzing Threshold
def setThreshold(TempThreshold, HumidThreshold):
 global TemperatureThreshold
 global HumidityThreshold

 TemperatureThreshold = TempThreshold
 HumidityThreshold = HumidThreshold
 print '%s Setting thresholds temp=%d, humidity=%d' % (getTimestamp(), TemperatureThreshold, HumidityThreshold)
 return;

#Reading Temperature and Humidity
def readTemperatureAndHumidity(TempHumidPin):
  global CurrentTemp
  global CurrentHumid
  global TempOffset
  global HumidOffset
  global QueueSize
  global QueueTemp, QueueHumid
  global QueueSizeHumidity, QueueSizeTemp
  global CurPosHumidity, CurPosTemp

  HumidReading, TempReading = Adafruit_DHT.read_retry(11, TempHumidPin)  
  if HumidReading is not None and TempReading is not None:
    TempNet = (TempReading + TempOffset)
    HumidNet = (HumidReading + HumidOffset)
    print('TempNet={0:0.1f}*  HumidNet={1:0.1f}%'.format(TempNet,HumidNet))

    EnqueueTemp(TempNet)
    calculateTempAverage()

    EnqueueHumidity(HumidNet)
    calculateHumidAverage()

  else:
    print(getTimestamp(), 'Failed to get reading. Try again!')
  return;


def startWaterPump(Duration):
  global GPIOPump

  print '%s Starting the water pump for %d secs on port %d' % (getTimestamp(), Duration, GPIOPump)
  startMotor(GPIOPump, Duration)
  return;



def startExhaustFan(Mode, Duration):
 global GPIOFan
 global GPIODHT
 global TemperatureThreshold
 global CurrentTemp
 print '%s Starting the exhaust fan on port %d until temp lowers to %d' % (getTimestamp(), GPIOFan, TemperatureThreshold)

 GPIO.setwarnings(False)
 GPIO.setup(GPIOFan,GPIO.OUT)
 print getTimestamp(), " Exhaust fan on"
 GPIO.output(GPIOFan,GPIO.LOW)
 setMotorMode("SENSOR")
 if  Mode==MotorMode:
  while CurrentTemp >= TemperatureThreshold:
   readTemperatureAndHumidity(GPIODHT)
  time.sleep(2)
 else:
  time.sleep(Duration)

 print getTimestamp(), " Exhaust fan off"
 GPIO.output(GPIOFan,GPIO.HIGH)
 
#Actucate Motors of Fan and Water Pump
def startMotor(MotorPin, Duration):
 GPIO.setwarnings(False)
 GPIO.setup(MotorPin,GPIO.OUT)
 print getTimestamp(), " on"
 GPIO.output(MotorPin,GPIO.LOW)

 time.sleep(Duration)

 print getTimestamp(), " off"
 GPIO.output(MotorPin,GPIO.HIGH)

def takeAction():
 global CurrentTemp
 global CurrentHumid
 global TemperatureThreshold
 global HumidityThreshold
 print '%s CurrentTemp=%d CurrentHumid=%d TemperatureThreshold=%d  HumidityThreshold=%d' % (getTimestamp(), CurrentTemp, CurrentHumid, TemperatureThreshold, HumidityThreshold)
 if CurrentTemp > TemperatureThreshold:
   startExhaustFan("DURATION", 10)
 else:
   debugPrint("NO Exhaust ACTION")
 return;
  
  

def soilMoistureAction(channel):
 if GPIO.input(channel):
  print "%s Low Soil Moisture Startin Water Pump" %(getTimestamp())
  startWaterPump(5)
 else:
  print "OK !"

########################################################
# Install callback for soil moisture level
########################################################
# Set our GPIO numbering to BCM
# Define the GPIO pin that we have our digital output from our sensor connected $
channel = GPIOSoilMoisture

# Set the GPIO pin to an input
GPIO.setup(channel, GPIO.IN)

# This line tells our script to keep an eye on our gpio pin and let us know when$
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)

# This line asigns a function to the GPIO pin so that when the above line tells $
GPIO.add_event_callback(channel, soilMoistureAction)


setThreshold(25, 50)

def uploadData(ApiKey):
 print 'Uploading....'
 baseURL = 'https://api.thingspeak.com/update?api_key=%s' % ApiKey
 try:
  f = urllib2.urlopen(baseURL + "&field1=%s&field2=%s" % (CurrentTemp, CurrentHumid))
  print (f.read())
  f.close()
 except:
  print 'Error Uploading'

def AdafruitUpload(AioKey):
 aio = Client(AioKey)
 aio.send('TempGauge', CurrentTemp)
 aio.send('HumidGauge',CurrentHumid)
 dataTemp = aio.receive('TempGauge')
 print('Received value: {0}'.format(dataTemp.value))
 dataHumid = aio.receive('TempGauge')
 print('Received value: {0}'.format(dataHumid.value))

  
#Main Loop
for i in range(QueueSizeTemp):
 QueueTemp.append(27)
 
for j in range(QueueSizeHumidity):
 QueueHumid.append(46)

print 'init Ttemperature', QueueTemp
print 'init Humidity', QueueHumid

while True:
  readTemperatureAndHumidity(GPIODHT)
  takeAction()
  time.sleep(1)
  uploadData(ThingSpeakAPI)
  AdafruitUpload(AdaFruitAIO)
  time.sleep(2)
