#!/bin/bash
TOPDIR=~/Drip
source $TOPDIR/drip_env/bin/activate
python3 $TOPDIR/Drip_Hub/main.py
deactivate
