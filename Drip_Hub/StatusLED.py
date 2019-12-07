#!/usr/bin/env python3

import os
import time
import board
import neopixel

import logging
logger = logging.getLogger(__name__)


class StatusLED():
    def __init__(self, pin = 6):
        self.pixels = neopixel.NeoPixel(board.D18, 4)

    def color1(self):
        color=(0,0,255) #blue
        #logger.info("color 1")
        self.pixels[0] = color
        self.pixels[1] = color
        self.pixels[2] = color
        self.pixels[3] = color
    
    def color2(self):
        color=(255,0,255) #purple
        #logger.info("color 2")
        self.pixels[0] = color
        self.pixels[1] = color
        self.pixels[2] = color
        self.pixels[3] = color
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
