## Raspi Zero Install Instructions

Flash Raspbian Lite to SD card as noted here (add link)

Load up Pi

Note that a lot of these commands take that time as the Pi Zero is slower than the normal Pi.  Try to have some more patience before trying to kill a command.

```
sudo raspi-config
```

Go to localization settings and adjust keyboard to US version as here (link).

Change password to non-default pi password

Connect to wifi under networking.

Enable ssh

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

Set up AWS certifcations and IOT (albert add here)


## Automatic Setup

Once the above steps are done, we can run a few scripts to finish the process

```bash
sudo apt update
sudo apt upgrade

# These will take some time on the Pi Zero

# Clone the repos
git clone -b master https://github.com/albertgo080/Drip.git

git clone https://github.com/OpenAgricultureFoundation/python-wifi-connect.git

# Setup python environment and prereqs for Drip
cd Drip
./setup.sh

sudo apt install -d -y network-manager
sudo systemctl stop dhcpcd && sudo system disable dhcpcd
sudo apt install network-manager -y

sudo service network-manager restart

nmcli con add con-name MIT ifname wlan0 type wifi ssid MIT

cd ~/python-wifi-connect

sudo ./scripts/install.sh

cd ~/Drip

./startup_setup.sh

```



## Manual Process

Clone the repos

```bash

git clone -b master https://github.com/albertgo080/Drip.git

git clone https://github.com/OpenAgricultureFoundation/python-wifi-connect.git

```

Install needed software

```bash

# This will take a while on the Pi Zero
sudo apt update
sudo apt upgrade

sudo apt install git python3-pip python3-venv libdbus-1-dev libglib2.0-dev virtualenv -y

# Set up virtual environment

cd ~/Drip
python3 -m venv drip_env
source drip_env/bin/activate
pip3 install requests bs4 netifaces RPi.GPIO paho-mqtt

# MQTT needs to be root to not throw errors
# sudo -H pip3 install paho-mqtt
```

Now install network-manager seperately to work with the wifi client

```bash

sudo apt install -d -y network-manager
sudo systemctl stop dhcpcd
sudo system disable dhcpcd
sudo apt install network-manager -y

sudo service network-manager restart

# Now NetworkManager should be running
# Connect to wifi via this

nmcli dev wifi

nmcli con add con-name <CONNECTION NAME> ifname wlan0 type wifi ssid <WIFI NAME>
# i.e  nmcli con add con-name MIT ifname wlan0 type wifi ssid MIT


# Turning on this connection
sudo nmcli con up <CONNECTION NAME>
# i.e. sudo nmcli con up MIT
```

## Install Python-Wifi-Connect

```bash
cd python-wifi-connect

# We just did this script manually as the script doesn't work with latest Debian
# sudo ./scripts/optional_install_NetworkManager_on_Linux.sh


sudo ./scripts/install.sh
```

## Setting up hub to start on boot

```bash
cd Drip
sh startup_setup.sh
```
