#!/usr/bin/env python3

import os
import time
import board
import neopixel

import logging
logger = logging.getLogger(__name__)


class StatusLED():
    def __init__(self, pin = 4):
        self.pixels = neopixel.NeoPixel(board.D18, 2)

    def color1(self):
        self.pixels[0] = (255, 0, 0)
        self.pixels[1] = (255, 255, 0)
    
    def color2(self):
        self.pixels[0] = (255, 255, 0)
        self.pixels[1] = (255, 0, 0)

if __name__=="__main__":
    pixels = neopixel.NeoPixel(board.D18, 2)

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
        break