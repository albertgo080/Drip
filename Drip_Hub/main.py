#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 11, 2019

import RPi.GPIO as GPIO
import time
import os
from Pump import Pump
from TritonClient import TritonClient

import requests
import json

import argparse

import logging

class TritonHub():
    def __init__(self, client_name="Triton", off_interval=4, \
                    on_interval=4, num_pump_intervals=2, check_interval=1, threshold_temp=32):

         # ID of system as appears on server
        self.client_name = client_name

        #### VARIABLES - SHOULD BE CHANGED ######
        #### VARIABLES REGARDING RELAY DEVICE ###
        self.off_interval       = off_interval # seconds. modulate pump 4 seconds off
        self.on_interval        = on_interval # seconds. modulate pump 4 seconds on
        self.num_pump_intervals = num_pump_intervals # of times modulate_pump function will turn pump on an off.
        self.check_interval     = check_interval # minutes. how often the script will check the current temperature and decide whether or not to modulate the pump.
        self.threshold_temp     = threshold_temp #degrees. threshold below which we start Triton system

        self.pump_channel       = 17 # for pump relay
        self.led_green          = 16 # for status relay

        #########################################

        # Set RPi GPIO pins to blink LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_green, GPIO.OUT)


        # Create MQQT and weather object
        self.client = TritonClient(self.client_name)

        # Create Pump object
        self.pump = Pump(self.pump_channel)

    def pump_on(self):
        GPIO.output(self.led_green, GPIO.HIGH) #turn green led on
        self.pump.pump_on()
        logger.debug("Pump and LED on")
        return

    def pump_off(self):
        self.pump.pump_off()
        GPIO.output(self.led_green, GPIO.LOW) #turn green led off
        logger.debug("Pump and LED off")
        return

    def modulate_pump(self):
        for i in range(self.num_pump_intervals):
            time_cycled = time.time()
            self.pump_on()
            while self.on_interval - ((time.time() - time_cycled)) > 0 and not self.client.manual:
                pass
            time_cycled2 = time.time()
            self.pump_off()
            while self.on_interval - ((time.time() - time_cycled2)) > 0 and not self.client.manual:
                pass
        logger.debug("number of intervals completed: %i", self.num_pump_intervals)
        return

    def on_off_threshold(self):
        if self.client.temperature[0] > self.threshold_temp:
            self.pump_off()
            logger.debug("No freezing")
        else:
            return self.modulate_pump()

    def run_cycle(self):
        logger.debug("In run_cycle")
        if self.client.manual:
            self.pump_on()
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
        logger.debug("Start time: %f", starttime)

        # The code sleeps/pauses until a minute has passed by
        while 5*self.check_interval - ((time.time() - starttime)) > 0 and not self.client.manual:
            pass

        logger.debug("After waiting for check interval: %f, diff: %f", time.time(), time.time()-starttime)


# def main():
#     '''
#     Main function that calls the class
#     '''
#     logger.info('In main')
#     foo = vHub()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Triton systems")
    parser.add_argument('--off_interval', default=4, type=float, help='seconds that pump modulates off')
    parser.add_argument('--on_interval', default=4, type=float, help='seconds that pump modulates on')
    parser.add_argument('--num_intervals', default=2, type=int, help='Number of times pump modulates off')
    parser.add_argument('--check_interval', default=1, type=float, help='How often in seconds hub checks for new temperatures')
    parser.add_argument('--threshold_temp', default=32, type=float, help='degress Fahrenheight Threshold below which Triton starts')

    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    Hub = TritonHub("Triton", args.off_interval, args.on_interval, args.num_intervals, args.check_interval, args.threshold_temp)

    # run Triton until it is interrupted once server is setup
    try:
        while True:
            if Hub.client.setup:
                Hub.run_cycle()
    except KeyboardInterrupt:
        pass

    # turn off pump before exiting and clear raspi pin outs
    Hub.pump_off()
    GPIO.cleanup()

    logger.debug("Exited cleanly")
