import RPi.GPIO as GPIO
import os
import sys
from Adafruit_IO import Client
import time
import Adafruit_DHT
import math
import numpy

AioKey="96df5edd973a4e30a389a03b8294957d"
FanPin=19
PumpPin=20

CurrentTemp = 0 #FIXME
CurrentHumid = 0 #FIXME

Debug = True
        
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FanPin,GPIO.OUT)
GPIO.setup(PumpPin,GPIO.OUT)

TempOffset = 14
HumidOffset = -100

QueueSizeTemp = 10
CurPosTemp = 0

QueueSizeHumidity = 10
CurPosHumidity = 0

############################################################
# Arrays for moving average over last few samples
############################################################
QueueTemp = []
QueueHumid = []

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


def getTimestamp():
    CurTime = time.asctime(time.localtime(time.time()))
    return CurTime;


def debugPrint(message):
    global Debug

    if Debug == True:
        print   getTimestamp(), message

    return;
           

def onFan():
 aio = Client(AioKey)
 ValueOne = aio.receive('On Fan')
 print('Received value: {0}'.format(ValueOne.value))
 if (ValueOne.value == '1'):
     print"fan On"
     GPIO.output(19,GPIO.LOW)
 if (ValueOne.value == '0'):
     print"fan Off"
     GPIO.output(19,GPIO.HIGH)

def onPump():
 aio = Client(AioKey)
 ValueTwo = aio.receive('On Pump')
 print('Received value: {0}'.format(ValueTwo.value))
 if (ValueTwo.value == '1'):
     print"Pump On"
     GPIO.output(20,GPIO.LOW)
 if (ValueTwo.value == '0'):
     print"Pump Off"
     GPIO.output(20,GPIO.HIGH)


def AdafruitUpload():
 aio = Client(AioKey)
 aio.send('Temperature', CurrentTemp)
 aio.send('Humidity',CurrentHumid)
 dataTemp = aio.receive('Temperature')
 print('Received value: {0}'.format(dataTemp.value))
 dataHumid = aio.receive('Humidity')
 print('Received value: {0}'.format(dataHumid.value))


#Reading Temperature and Humidity
def readTemperatureAndHumidity():
 global CurrentTemp
 global CurrentHumid
 global TempOffset
 global HumidOffset
 global QueueSize
 global QueueTemp, QueueHumid
 global QueueSizeHumidity, QueueSizeTemp
 global CurPosHumidity, CurPosTemp

 HumidReading, TempReading = Adafruit_DHT.read_retry(11, 4 )
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
                            

def ControlThread():
    onFan()
    onPump()
    
def MonitorThread():
 readTemperatureAndHumidity()
 AdafruitUpload()
    
 
#try:
# thread.start_new_thread( ControlThread, () )
# thread.start_new_thread( MonitorThread, () )
#except:
# print "Error: unable to start thread"

#Main Loop
for i in range(QueueSizeTemp):
 QueueTemp.append(27)

for j in range(QueueSizeHumidity):
 QueueHumid.append(46)

print 'init Ttemperature', QueueTemp
print 'init Humidity', QueueHumid
                                 
while True:
 ControlThread()
 MonitorThread()
 time.sleep(1)
 # pass

