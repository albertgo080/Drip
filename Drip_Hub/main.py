#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 11, 2019

import RPi.GPIO as GPIO
import time
import os
from Pump import Pump
from TritonClient import TritonClient

from StatusLED import StatusLED

import requests
import json

import argparse

import logging

class TritonHub():

    def __init__(self, config, client_name="Triton", off_interval=4, \
                    on_interval=4, num_pump_intervals=2, check_interval=1, threshold_temp=32, testing=True):
         # ID of system as appears on server
        self.client_name = client_name

        #### VARIABLES - SHOULD BE CHANGED ######
        #### VARIABLES REGARDING RELAY DEVICE ###
        self.off_interval       = off_interval # seconds. modulate pump 4 seconds off
        self.on_interval        = on_interval # seconds. modulate pump 4 seconds on
        self.num_pump_intervals = num_pump_intervals # of times modulate_pump function will turn pump on an off.
        self.check_interval     = check_interval # minutes. how often the script will check the current temperature and decide whether or not to modulate the pump.
        self.threshold_temp     = threshold_temp #degrees. threshold below which we start Triton system
        self.cycle_length       = 15*60 # 15 minutes
        self.cycle_num          = 4 #4 * 15 minutes = 1 hour
        self.which_cycle        = 1 #to count which of the four cycles
        self.pump_channel       = 5 # for pump relay
        self.led_green          = 16 # for status relay
        self.testing            = testing
        #########################################

        # Set RPi GPIO pins to blink LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_green, GPIO.OUT)

        self.status_led = StatusLED()

        # Create MQQT and weather object
        self.client = TritonClient(config, self.client_name, testing=self.testing)

        # Create Pump object
        self.pump = Pump(self.pump_channel)
        self.start_time=-1
    def pump_on(self):
        GPIO.output(self.led_green, GPIO.HIGH) #turn green led on
        self.pump.pump_on()
        # logger.debug("Pump and LED on")
        return

    def pump_off(self):
        self.pump.pump_off()
        GPIO.output(self.led_green, GPIO.LOW) #turn green led off
        # logger.debug("Pump and LED off")
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

    def get_cutoff(self):
        off=self.client.time
        if self.testing: #use conduction equations. 6 min on
            on=6
        else: #use convection equations. on = 20 (?)
            on=20
        if (on+off)>60: #scale down to hour long cycle
            self.cycle_length=60*60
            self.cycle_num=1
        elif (on+off)>30: #scale down to 30 min cycle
            self.cycle_length=30*60
            self.cycle_num=2
        else: #scale to 15 min cycle
            self.cycle_length=15*60
            self.cycle_num=4

        self.cutoff=on/(off+on)*self.cycle_length

    def run_cycle(self):
        '''

        if not self.manual: if time has been more than 15 minutes since last
        weather update, update weather and set on off ratio. if time has been
        less than x minutes since last update, be on. If time is greater than
        x, be off.
        '''

        self.status_led.color1()
        time.sleep(0.1)
        self.status_led.color2()

        if self.client.manual:
            if self.client.pump_control_on:
                logger.info("Manual on: Pump on")
                self.pump_on()
                self.client.active = 1
            else:
                logger.info("Manual on: Pump off")
                self.pump_off()
                self.client.active=0
        else:
            if ((time.time()-self.start_time)>self.cycle_length or self.client.changed):
                if self.which_cycle > self.cycle_num or self.client.changed:
                    logger.info("Updating weather and bins")
                    #only update after 4 cycles (so an hour)
                    self.temperature = self.client.get_weather_data()
                    self.get_cutoff()
                    self.which_cycle=1
                    self.client.changed=False
                else:
                    logger.info("Remaining cycles. No weather update needed")
                    self.which_cycle+=1
                self.start_time = time.time()

            if ( (time.time() - self.start_time) < self.cutoff and self.client.active):
                # logger.info("Turning pump on")
                self.pump_on()
            else:
                # logger.info("Turning pump off")
                self.pump_off()

                '''
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
        while 5*self.check_interval - (time.time() - starttime) > 0 and not self.client.manual:
            pass

        logger.debug("After waiting for check interval: %f, diff: %f", time.time(), time.time()-starttime)
        '''

def main(args):
    # Get path to main.py script
    main_path = os.path.dirname(os.path.abspath(__file__))
    config_filename = 'config.json'
    config_path = main_path+'/'+config_filename

    # Make sure config file is present
    if not os.path.isfile(config_path):
        logger.warning('No configuration file. Creating file')

        # Create blank configuration file
        config = {'aws_endpoint':'Add AWS endpoint address', 
                    'ca-cert':'Absolute path to aws ca-certificate',
                    'private-key': 'Absolute path to aws private key',
                    'cert': 'Absolute path to aws certifcate',
                    'coordinates': {'long': None,'lat': None},
                    'path-to-config': config_path }

        with open(config_path, 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        logger.info("Created blank configuration file. Please fill out with information in 'config.json' and rerun script")
        return
    else:
        # Given the file exists, load, and check for coordinates
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            if config['coordinates']['long'] is not None:
                logger.info('Using previous configuration location: %f long, %f lat', config['coordinates']['long'], config['coordinates']['lat'])
                coords=True
            else:
                logger.info('Previous coordinates not set')
                coords=False
    Hub = TritonHub(config, "Triton-Zero", args.off_interval, args.on_interval, args.num_intervals, args.check_interval, args.threshold_temp)
    if coords:
        Hub.client.setup=coords #sets setup to true if lat and long are already present
        Hub.client.get_weather_data()
    # run Triton until it is interrupted once server is setup
    try:
        while True:
            if Hub.client.setup:
                Hub.run_cycle()
            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("Trying to exit script")
        pass

    # turn off pump before exiting and clear raspi pin outs
    Hub.pump_off()
    GPIO.cleanup()

    logger.info("Exited cleanly")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Triton systems")
    parser.add_argument('--off_interval', default=4, type=float, help='seconds that pump modulates off')
    parser.add_argument('--on_interval', default=4, type=float, help='seconds that pump modulates on')
    parser.add_argument('--num_intervals', default=2, type=int, help='Number of times pump modulates off')
    parser.add_argument('--check_interval', default=1, type=float, help='How often in seconds hub checks for new temperatures')
    parser.add_argument('--threshold_temp', default=32, type=float, help='degress Fahrenheight Threshold below which Triton starts')
    parser.add_argument('--debug', action='store_true', help='Show DEBUG messages. Otherwise just shows INFO and above')
    parser.add_argument('--testing', default=1, type=int, help='Tells Triton whether you are using the testing setup (conduction model) or a real setup (convection model)')

    args = parser.parse_args()

    if (args.debug):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    main(args)
    
