#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio

import requests
from bs4 import BeautifulSoup
import json

class Drip():
	def __init__(self):

		self.clientName = "Drip"
		self.serverAddress = "18.21.156.233"
		self.mqttClient = mqtt.Client(self.clientName)

		self.mqttClient.message_callback_add('Drip/location',self.on_message_location)
		self.mqttClient.message_callback_add('Drip/startup',self.on_message_startup)


		self.mqttClient.on_connect = self.on_connect
		self.mqttClient.on_message = self.on_message
		self.mqttClient.connect(self.serverAddress)
		self.mqttClient.subscribe("Drip/#")
		
		self.temperature = [20,0]
		self.state=1
		self.battery=90

		self.mqttClient.loop_forever()

	def on_connect(self, client, userdata, flags, rc):
		#Subscribe client to topic
		print('Connected')

	def on_message(self, client, userdata, msg):
		message = msg.payload.decode(encoding='UTF-8')
		print(message)

	def on_message_location(self, client, userdata, msg):
		message = msg.payload.decode(encoding='UTF-8')
		print(message)
		location=message.split(",")
		self.temperature=self.get_weather_data(location[0],location[1])
		print(self.temperature)
		
	def on_message_startup(self, client, userdata, msg):
		client.publish("Drip/State", "State,{}".format(self.state))
		client.publish("Drip/Temperature","Temp,{}".format(self.temperature[0]))
		client.publish("Drip/Battery", "Bat,{}".format(self.battery))
	
	def get_weather_data(self,lat,long):
	    url='https://api.weather.gov/points/'+str(lat)+','+str(long)
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

	    return temps

def main():
	print('main')
	foo = Drip()

if __name__ == '__main__':
	main()




