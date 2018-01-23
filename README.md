# Greenhouse-Automation-and-Monitoring-System
It is My Final Year Bachleors Degree Coursework Project

It consists of temperature and humidity sensor node, soil moisture sensor node hardwired into raspberry pi where the final python code is embedded in the operating system as a high priority startup background daemon.

As soon as you will boot the raspberry pi the system will start functioning. 

The sensors nodes are interfaced using Standard Peripheral Interface Bus (SPI) and they communicate mutually in a half-duplex manner, when sensor nodes send the data it is preprocessed using a dynamic linear mean queue which is then published to an Open Source IoT Cloud where data analytics will be performed; then the cloud will send the data to the subscribed app using publish/subscribe pattern.

The actuation of the climate control system has three operation modes; Time Based, Sensor Based, and User Based. 
The fan will be turned ON/OFF inside the greenhouse, if the sensor reads the temperature below the fixed threshold in sensor based mode, in a time based mode the fan will be ON for a particular period of time, and in user based mode the fan will in control of the user of the system.

Similar is the system for the water pump but it has only two modes Time-Based and User Based. 


# Getting Started
Connect Reaspberry Pi and Other Circuitory in Proper Manner
The Components needed will be,
-> DHT 11 or any DHT Family Hygrometer and Temperature Sensor
-> Generic Soil Hygrometer
-> Raspberry Pi (Any Version)
-> Generic Relay Motor Driver Circuit
-> Water pump
-> Fan (Small Size)

Note: I have Used Low Voltage Components on AC Supply via AC to DC converter.

# Contributing
### Author : Neel Shah
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.
Versioning

# License

This project is licensed under the GNU GPLv3 License - see the LICENSE file for details

