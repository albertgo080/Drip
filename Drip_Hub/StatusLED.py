#!/usr/bin/env python3

import os
import RPi.GPIO as GPIO
from neopixel import *
import time

import logging
logger = logging.getLogger(__name__)


class StatusLED():
    def __init__(self, pin = 4):

        # LED strip configuration:
        self.led_count      = 16      # Number of LED pixels.
        self.led_pin        = pin      # GPIO pin connected to the pixels (18 uses PWM!).
        self.led_freq_hz    = 800000  # LED signal frequency in hertz (usually 800khz)
        self.led_dma        = 10      # DMA channel to use for generating signal (try 10)
        self.led_brightness = 255     # Set to 0 for darkest and 255 for brightest
        self.led_invert     = False   # True to invert the signal (when using NPN transistor level shift)
        self.led_channel    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

         
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.led_count, self.led_pin, self.led_freq_hz, 
                                self.led_dma, self.led_invert, self.led_brightness, 
                                self.led_channel)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    
    # Define functions which animate LEDs in various ways.
    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    
    def theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)
    
    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    
    def rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    
    def theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

if __name__ == "__main__":
    LED = StatusLED(4)
    try:
        while True:
            print ('Color wipe animations.')
            LED.colorWipe(Color(255, 0, 0))  # Red wipe
            LED.colorWipe(Color(0, 255, 0))  # Blue wipe
            LED.colorWipe(Color(0, 0, 255))  # Green wipe
            print ('Theater chase animations.')
            LED.theaterChase(Color(127, 127, 127))  # White theater chase
            LED.theaterChase(Color(127,   0,   0))  # Red theater chase
            LED.theaterChase(Color(  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            LED.rainbow()
            LED.rainbowCycle()
            LED.theaterChaseRainbow()

    except KeyboardInterrupt:
     LED.colorWipe(Color(0,0,0), 10)
