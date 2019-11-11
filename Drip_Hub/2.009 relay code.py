#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:09:49 2019

@author: zacharykopstein




# https://www.youtube.com/watch?v=51f3ZazNW-w

******ADAPTED CODE FROM LINK ABOVE*******



# relay (+) to 5v pin on ras pi
# relay (-) to ground pin on ras pi
# relay (S) (or whatever the third pin says) to ras pi GPIO pin 17
'''

"""


import RPi.GPIO as GPIO
import time
import get_weather

channel = 17 #GPIO pin 17

#### VARIABLES - SHOULD BE CHANGED ######

off_interval = 3 #seconds. modulate pump 3 seconds off, 1 second on
on_interval = 1 #seconds. modulate pump 3 seconds off, 1 second on
num_pump_intervals = 10 #of times modulate_pump function will turn pump on an off. may need to be variable going forward.
check_interval = 1 #minutes. how often the script will check the current temperature and decide whether or not to modulate the pump.
threshold_temp = 39 #degrees. threshold below which we start drip system




# GPIO setup

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)


#functions


def pump_on(pin):
    GPIO.output(pin, GPIO.HIGH) #turn pump on
    print("Pump on")
    
def pump_off(pin):
    GPIO.output(pin, GPIO.LOW)
    print("Pump off")
    
def modulate_pump(num_pump_intervals):
    for i in range(num_pump_intervals):

    	pump_on(channel)
    	time.sleep(on_interval)
    	pump_off(channel)
    	time.sleep(off_interval)
    print("number of intervals completed: ", num_pump_intervals)

def get_current_temp():
	lat,long=get_weather.get_location()
	data=get_weather.get_weather_data(lat,long)
#	print(data)
	return data[0]

def on_off_threshold():
	if get_current_temp() > threshold_temp:
		return "No freezing"
	else:
		return modulate_pump(num_pump_intervals)

def run_cycle():
	starttime = time.time()
	while True:
		print(on_off_threshold())
		time.sleep(abs((60*check_interval - ((time.time() - starttime) % 60.0))))
#from stack overflow question "what is the best way to repeatedly execute a function ever x seconds in python"

### TESTING THE CODE###

print(run_cycle())

'''
print(get_current_temp())

print(on_off_threshold())


print(on_off_threshold(threshold_temp))
'''

