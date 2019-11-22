#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 11, 2019

import RPi.GPIO as GPIO
import time
import os
from Pump import Pump
from DripClient import DripClient

import requests
import json

import argparse

import logging

class DripHub():
    def __init__(self, client_name="Drip", off_interval=4, \
                    on_interval=4, num_pump_intervals=2, check_interval=1, threshold_temp=32):

         # ID of system as appears on server  
        self.client_name = client_name 
        
        #### VARIABLES - SHOULD BE CHANGED ######
        #### VARIABLES REGARDING RELAY DEVICE ###
        self.off_interval       = off_interval # seconds. modulate pump 4 seconds off
        self.on_interval        = on_interval # seconds. modulate pump 4 seconds on
        self.num_pump_intervals = num_pump_intervals # of times modulate_pump function will turn pump on an off. 
        self.check_interval     = check_interval # minutes. how often the script will check the current temperature and decide whether or not to modulate the pump.
        self.threshold_temp     = threshold_temp #degrees. threshold below which we start drip system
        
        self.pump_channel       = 17 # for pump relay
        self.led_green          = 16 # for status relay

        #########################################
    
        # Set RPi GPIO pins to blink LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_green, GPIO.OUT)


        # Create MQQT and weather object
        self.client = DripClient(self.client_name)

        # Create Pump object
        self.pump = Pump(self.pump_channel)

    def pump_on(self, pin):
        GPIO.output(self.led_green, GPIO.HIGH) #turn green led on
        self.pump.pump_on()
        logger.debug("Pump and LED on")
        return
    
    def pump_off(self, pin):
        self.pump.pump_off()
        GPIO.output(self.led_green, GPIO.LOW) #turn green led off
        logger.debug("Pump and LED off")
        return
        
    def modulate_pump(self):
        for i in range(self.num_pump_intervals):
            time_cycled = time.time()
            self.pump.pump_on()
            while self.on_interval - ((time.time() - time_cycled)) > 0 and not self.client.manual:
                pass
            time_cycled2 = time.time()
            self.pump.pump_off()
            while self.on_interval - ((time.time() - time_cycled2)) > 0 and not self.client.manual:
                pass
        logger.debug("number of intervals completed: %i", self.num_pump_intervals)
        return

    def on_off_threshold(self):
        if self.client.temperature[0] > self.threshold_temp:
            self.pump.pump_off()
            logger.debug("No freezing")
        else:
            return self.modulate_pump()

    def run_cycle(self):
        logger.debug("In run_cycle")
        if self.client.manual:
            self.pump.pump_on()
            self.client.state = 1
            self.client.danger = "Moderate"
            logger.debug("manual on")
        else:
            self.on_off_threshold()
        try:
            self.temperature=self.client.get_weather_data()
        except:
            pass
        starttime = time.time()

        # The code sleeps/pauses until a minute has passed by
        while 5*self.check_interval - ((time.time() - starttime)) > 0 and not self.client.manual:
            pass
                

# def main():
#     '''
#     Main function that calls the class
#     '''
#     logger.info('In main')
#     foo = DripHub()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the drip systems")
    parser.add_argument('off_interval', default=4, type=float, help='seconds that pump modulates off')
    parser.add_argument('on_interval', default=4, type=float, help='seconds that pump modulates on')
    parser.add_argument('num_intervals', default=2, type=int, help='Number of times pump modulates off')
    parser.add_argument('check_interval', default=1, type=float, help='How often in minutes hub checks for new temperatures')
    parser.add_argument('threshold_temp', default=32, type=float, help='degress Fahrenheight Threshold below which drip starts')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    Hub = DripHub("Drip", args.off_interval, args.on_interval, args.num_intervals, args.check_interval, args.threshold_temp)
    
    # run drip until it is interrupted
    try:
        while True:
            Hub.run_cycle()
    except KeyboardInterrupt:
        pass

    # turn off pump before exiting
    Hub.pump_off()

    logger.debug("Exited cleanly")



