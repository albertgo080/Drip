#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 11, 2019

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import os

import requests
from bs4 import BeautifulSoup
import json
import netifaces as ni

class Drip():
	def __init__(self):

		self.clientName    = "Drip" #Define the script's name for when it appears on the Server
		ni.ifaddresses('wlan0')
		self.serverAddress = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr'] #Define the address of the server
		self.mqttClient    = mqtt.Client(self.clientName) #Define the client

		#Callback function is called when script is connected to mqtt server
		self.mqttClient.on_connect = self.on_connect

		#Establishing and calling callback functions for when messages from different topics are received
		self.mqttClient.message_callback_add('Drip/location',self.on_message_location)
		self.mqttClient.message_callback_add('Drip/startup',self.on_message_startup)
		self.mqttClient.on_message = self.on_message

		#Subscribe to everything that starts with Drip/
		self.mqttClient.connect(self.serverAddress)
		self.mqttClient.subscribe("Drip/#")

		#Defining location variables
		self.latitude  = None
		self.longitude = None
		
		#Defining global variables that the app subscribes to - THESE ARE DUMMY VARIABLES
		self.temperature = [20,0]
		self.state       = 1
		self.battery     = 90
		self.danger      = 'Moderate'

		#Defining whether or not setup has been completed
		self.setup = False

		#Defining GPIO pin for the relay
		self.channel = 17

		#### VARIABLES - SHOULD BE CHANGED ######
		#### VARIABLES REGARDING RELAY DEVICE ###
		self.off_interval       = 4 #seconds. modulate pump 3 seconds off, 1 second on
		self.on_interval        = 1 #seconds. modulate pump 3 seconds off, 1 second on
		self.num_pump_intervals = 2 #of times modulate_pump function will turn pump on an off. may need to be variable going forward.
		self.check_interval     = 5 #minutes. how often the script will check the current temperature and decide whether or not to modulate the pump.
		self.threshold_temp     = 32 #degrees. threshold below which we start drip system

		## LOGIC VARIABLES
		self.level1Temp = 32
		self.level2Temp = 10
		self.level3Temp = 0
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.channel, GPIO.OUT)

		#This causes the script to loop forever
		self.mqttClient.loop_start()
		self.run_cycle()

	def on_connect(self, client, userdata, flags, rc):
		'''
		Callback function for when the script is connected to the server
		Prints connected to verify
		'''
		print('Connected')
		
	def on_message(self, client, userdata, msg):
		'''
		Prints message for any message not received through Drip/ topics
		'''
		message = msg.payload.decode(encoding='UTF-8')
		print(message)

	def on_message_location(self, client, userdata, msg):
		'''
		Callback function for Drip/location topics
		Gets the temperature based on the location that is specified
		'''
		message = msg.payload.decode(encoding='UTF-8')
		print(message)
		#split on the comma because the message in the form of "latitude, longitude"
		location=message.split(",")

		self.latitude = location[0]
		self.longitude = location[1]

		self.temperature=self.get_weather_data()
		print(self.temperature)
		
	def on_message_startup(self, client, userdata, msg):
		'''
		Callback function for Drip/startup topic
		Publishes State, Temperature, Battery, and Danger information to the respective topics
		This function is called everythime someone opens the Drip dashboard in the app
		Also is called when someone hits the refresh button on the app
		'''
		client.publish("Drip/State", "State,{}".format(self.state))
		client.publish("Drip/Temperature","Temp,{}".format(self.temperature[0]))
		client.publish("Drip/Battery", "Bat,{}".format(self.battery))
		client.publish("Drip/Danger", "Danger,{}".format(self.danger))
		self.setup = True
	
	def get_weather_data(self):
		'''
		Gets weather data from the location specified by latittude and longitude
		Returns a list of temperatures fro the next 150 hours
		'''
		#define url that takes latitiude and longitude variables
		url='https://api.weather.gov/points/'+str(self.latitude)+','+str(self.longitude)
		initial=requests.get(url)
		html=BeautifulSoup(initial.content,features="html.parser")

		dict_one=json.loads(html.text)
		url=dict_one["properties"]["forecastHourly"]
		#do again but with new url
		initial=requests.get(url)
		html=BeautifulSoup(initial.content,features="html.parser")
		dict_one=json.loads(html.text)
		props=dict_one["properties"]
		temps=[]

		for period in props["periods"]:
	        	temps.append(period["temperature"])

		currentTemp = temps[0]
		if currentTemp>self.level1Temp:
			self.state=0
			self.danger = "None"
		elif currentTemp<self.level1Temp:
			self.state=1
			self.danger = "Low"
		elif currentTemp<self.level2Temp:
			self.state=2
			self.danger = "Moderate"
		elif currentTemp<self.level3Temp:		
			self.state=3
			self.danger = "High"
		return temps

	def pump_on(self, pin):
		os.system('./test_code_rf/CC1101/raspi/TX_Go -a1 -r2 -i1000 -t0 -c1 -f434 -m250')
		GPIO.output(pin, GPIO.HIGH) #turn pump on
		print("Pump on")
    
	def pump_off(self, pin):
		os.system('./test_code_rf/CC1101/raspi/TX_Stop -a1 -r2 -i1000 -t0 -c1 -f434 -m250')
		GPIO.output(pin, GPIO.LOW)
		print("Pump off")
		
	    
	def modulate_pump(self):
		for i in range(self.num_pump_intervals):
			time_cycled = time.time()
			self.pump_on(self.channel)
			time.sleep(self.on_interval)
			self.pump_off(self.channel)
			time.sleep(self.off_interval)
		print("number of intervals completed: ", self.num_pump_intervals)

	def on_off_threshold(self):
		if self.temperature[0] > self.threshold_temp:
			print("No freezing")
		else:
			return self.modulate_pump()

	def run_cycle(self):
		while True:
			print("While True")
			self.on_off_threshold()
			try:
				self.temperature=self.get_weather_data()
			except:
				pass
			starttime = time.time()
		#The code sleeps/pauses until a minute has passed by
		#time.sleep(abs((60*self.check_interval - ((time.time() - starttime) % 60.0))))
			while 60*self.check_interval - ((time.time() - starttime)) > 0:
			#while 2 - ((time.time() - starttime)) > 0:
				pass
				

def main():
	'''
	Main function that calls the class
	'''
	print('main')
	foo = Drip()

if __name__ == '__main__':
	main()




