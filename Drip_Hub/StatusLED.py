#!/usr/bin/env python3

import os
import time
import board
import neopixel

import logging
logger = logging.getLogger(__name__)


class StatusLED():
    def __init__(self, pin = 6):
        self.num_pixels = 6
        self.pixels = neopixel.NeoPixel(board.D18, self.num_pixels)

    def color1(self):
        brightness = 0.5
        color=(0,0,127) #blue
        #logger.info("color 1")
        self.pixels.fill(color)
        #self.pixels[0] = color
        #self.pixels[1] = color
        #self.pixels[2] = color
        #self.pixels[3] = color
    
    def color2(self):
        brightness = 0.5
        color=(127,0,127) #purple
        #logger.info("color 2")
        self.pixels.fill(color)
        #self.pixels[0] = color
        #self.pixels[1] = color
        #self.pixels[2] = color
        #self.pixels[3] = color
'''
if __name__=="__main__":
    pixels = neopixel.NeoPixel(board.D10, 2)

    try:
        while True:
            pixels[0] = (255, 0, 0)
            pixels[1] = (255, 255, 0)
            time.sleep(0.4)
            pixels[0] = (255, 255, 0)
            pixels[1] = (255, 0, 0)
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("Exiting")
'''
