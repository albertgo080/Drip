#!/usr/bin/env python3

import os
import time
import board
import neopixel

import logging
logger = logging.getLogger(__name__)


# class StatusLED():
#     def __init__(self, pin = 4):

if __name__=="__main__":
    pixels = neopixel.NeoPixel(board.D18, 2)
    pixels[0] = (255, 0, 0)
    pixels[1] = (255, 255, 0)