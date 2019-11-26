#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: MIT 2.009 Purple Team
# Date: November 11, 2019
from __future__ import print_function
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import os

import requests
from bs4 import BeautifulSoup
import json
import netifaces as ni

import sys
import ssl
import datetime
import logging, traceback

logger = logging.getLogger(__name__)

class TritonClient():
    '''
    Initialize the MQTT server.
    Params:
        client_name (string) - id of Triton system on server
        net_interface (string) - network interface to use (wifi vs ethernet), only tested on wifi now
        level1Temp, level2Temp, level3Temp (int) - the warning temperatures for this Triton install
    '''
    def __init__(self, client_name='Triton', net_interface='wlan0', level1Temp=32, level2Temp=10, level3Temp=0):
        #constants for server connection
        self.IoT_protocol_name = "Triton"
        self.aws_iot_endpoint = "a2rpq57lrt0k72-ats.iot.us-east-2.amazonaws.com" # <random>.iot.<region>.amazonaws.com
        self.url = "https://{}".format(self.aws_iot_endpoint)

        self.ca = "/usr/local/share/ca-certificates/aws3.crt"
        self.private = "/home/purple/26b644023d-private.pem.key"
        self.cert = "/home/purple/26b644023d-certificate.pem.crt"
        #end aws server constants

        # define script name for when it appears on server
        self.client_name = client_name

        # define the address of the server
        self.net_interface = net_interface
        self.serverAddress = ni.ifaddresses(self.net_interface)[ni.AF_INET][0]['addr']
        logger.debug("Server address: %s", self.serverAddress)

        # define the client
        self.mqtt_client = mqtt.Client(self.client_name)

        #more aws setup
        self.ssl_context= self.ssl_alpn()
        self.mqtt_client.tls_set_context(context=self.ssl_context)

        # Callback function is called when script is connected to mqtt server
        self.mqtt_client.on_connect = self.on_connect

        # Establishing and calling callback functions for when messages from different topics are received
        self.mqtt_client.message_callback_add(self.client_name + '/location', self.on_message_location)
        logger.debug("Location topic: %s", self.client_name+'/location')
        self.mqtt_client.message_callback_add(self.client_name + '/startup', self.on_message_startup)
        self.mqtt_client.message_callback_add(self.client_name + '/manual', self.on_message_manual)
        self.mqtt_client.on_message = self.on_message

        #connect to aws iot (DA CLOUD)
        self.mqtt_client.connect(self.aws_iot_endpoint, port=8883)

        # Subscribe to everything that starts with Client name
       # self.mqtt_client.connect(self.serverAddress)
        self.mqtt_client.subscribe(self.client_name+'/#')

        # Defining location variables
        self.latitude  = None
        self.longitude = None

        # Defining variables that the app subscribes to - THESE ARE DUMMY VARIABLES
        self.temperature = [50,0]
        self.state       = 0
        self.battery     = 90
        self.danger      = 'None'

        # Defining whether or not setup has been completed
        self.setup = False

        ## LOGIC VARIABLES
        self.level1Temp = level1Temp
        self.level2Temp = level2Temp
        self.level3Temp = level3Temp

        # Tells if Triton was manually set to be on
        self.manual = False

        # Causes mqtt to run continuously
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        '''
        Callback function for when the script is connected to the server
        Prints connected to verify
        '''
        logger.info("Connected to server")

    def on_message(self, client, userdata, msg):
        '''
        Prints message for any message not received through Triton/ topics
        '''
        message = msg.payload.decode(encoding='UTF-8')
        logger.debug("Message %s", message)

    def on_message_location(self, client, userdata, msg):
        '''
        Callback function for Triton/location topics
        Gets the temperature based on the location that is specified
        '''
        message = msg.payload.decode(encoding='UTF-8')
        logger.debug(message)
        #split on the comma because the message in the form of "latitude, longitude"
        location = message.split(",")

        self.latitude = location[0]
        self.longitude = location[1]
        logger.debug("Latitude: %s, Longitude: %s", self.latitude, self.longitude)
        try:
            self.temperature = self.get_weather_data()
        except KeyError:
            logger.error("Could not get weather data for given long/lat. Temp staying the same")

        logger.debug("Temperature: %f", self.temperature[0])

    def on_message_startup(self, client, userdata, msg):
        '''
        Callback function for Triton/startup topic
        Publishes State, Temperature, Battery, and Danger information to the respective topics
        This function is called everythime someone opens the Triton dashboard in the app
        Also is called when someone hits the refresh button on the app
        '''
        client.publish(self.client_name + "/State", "State,{}".format(self.state))
        client.publish(self.client_name + "/Temperature","Temp,{}".format(self.temperature[0]))
        client.publish(self.client_name + "/Battery", "Bat,{}".format(self.battery))
        client.publish(self.client_name + "/Danger", "Danger,{}".format(self.danger))
        self.setup = True
        logger.debug("Setup has been completed")

    def on_message_manual(self, client, userdata, msg):
        '''
        Callback function for Triton/manual topic
        Sets the self.manual variabl as true and thus opens the valve
        '''
        message = msg.payload.decode(encoding='UTF-8')
        print (message)
        if message == "on":
            self.manual = True
        else:
            self.manual = False
        logger.debug("Manual Settings: %d", self.manual)

    def get_weather_data(self):
        '''
        Gets weather data from the location specified by latittude and longitude
        Returns a list of temperatures fro the next 150 hours
        '''
        logger.debug("Getting weather data!")
        # define url that takes latitiude and longitude variables
        url = 'https://api.weather.gov/points/' + str(self.latitude) + ',' + str(self.longitude)
        initial = requests.get(url)
        html = BeautifulSoup(initial.content,features="html.parser")

        # Get new URL for weather at specific coordinates
        dict_one = json.loads(html.text)
        logger.debug("Dict one: %s",str(dict_one))
        try:
            url = dict_one["properties"]["forecastHourly"]
            logger.debug("Url: %s", url)

        except KeyError:
            logger.error("Location given does produce dict with a 'properties key'")
            err = KeyError("Location given does produce dict with a 'properties key'")
            raise err

        # do again but with new url
        initial = requests.get(url)
        html = BeautifulSoup(initial.content,features="html.parser")
        dict_one = json.loads(html.text)
        logger.debug("Dict one 2: %s", str(dict_one))
        try:
            props = dict_one["properties"]
            logger.debug("Props: %s", str(props))
        except KeyError:
            logger.error("Location given does produce dict 2 with a 'properties key'")
            err = KeyError("Location given does produce dict with a 'properties key'")
            raise err

        logger.debug("Successfully called weather API")
    
        #get temp data
        temps = [period["temperature"] for period in props["periods"]]

        #now do wind speed
        speeds = [period["windSpeed"] for period in props["periods"]]

        current_temp = temps[0]
        current_wind_speed=speeds[0]
        
        if current_temp > self.level1Temp:
            self.state = 0
            self.danger = "None"
        elif current_temp < self.level1Temp:
            self.state = 1
            self.danger = "Low"
        elif current_temp < self.level2Temp:
            self.state = 2
            self.danger = "Moderate"
        elif current_temp < self.level3Temp:
            self.state = 3
            self.danger = "High"
        return temps


    def ssl_alpn(self): #aws helper function

        #debug print opnessl version
        #logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
        ssl_context = ssl.create_default_context()
        ssl_context.set_alpn_protocols([self.IoT_protocol_name])
        ssl_context.load_verify_locations(cafile=self.ca)
        ssl_context.load_cert_chain(certfile=self.cert, keyfile=self.private)
        return  ssl_context
