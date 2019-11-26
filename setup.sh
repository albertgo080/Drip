#!/bin/sh

# This script will setup that pi as a drip hub and install the necessary
# prerequistes. There may be some additional manual configuration at the end.

# Keep track of user that called script for when using root commands
export BASEUSR=$USER

# Start relative to location of script 
TOPDIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
cd TOPDIR

echo "Top dir: $TOPDIR"


# Installing dependencies
sudo apt install git python3-pip python3-venv libdbus-1-dev libglib2.0-dev
virtualenv -y


# Removing previous virtual env if it exists
echo "Removing "rm -r $TOPDIR/drip_env""

#rm -rf $TOPDIR/drip_env

echo 'Setting up virtual environment for Drip Hub'

python3 -m drip_env $TOPDIR/drip_env

source $TOPDIR/drip_env/bin/activate

echo "Installing Drip Hub dependencies"
pip3 install requests bs4 netifaces RPi.GPIO

pip3 install paho-mqtt
# MQTT needs to be root to not throw errors
# sudo -H pip3 install paho-mqtt

deactivate

echo "Finished creating environment"

echo "Continue hub setup by installing network-manager in the next step"
