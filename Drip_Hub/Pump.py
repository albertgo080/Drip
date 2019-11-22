import os
import RPi.GPIO as GPIO
import time

import logging
logger = logging.getLogger(__name__)


class Pump():
    def __init__(self, pin = 17):

        #Defining GPIO pin for the relay
        self.channel = pin

        GPIO.setmode(GPIO.BCM)  # Set's the numbering system to use channel number.  Pin numbers could be different on different Pi revisions
        GPIO.setup(self.channel, GPIO.OUT)

        self.pump_status = False  # True = On, False = Off

 
    def pump_on(self):
        GPIO.output(self.channel, GPIO.HIGH) #turn pump on
        self.pump_status = True
        logging.debug("Pump on")
        return
    
    def pump_off(self):
        GPIO.output(self.channel, GPIO.LOW)
        self.pump_status = False
        logging.debug("Pump off")
        return
