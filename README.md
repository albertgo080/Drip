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


Install needed software

```bash
sudo apt update
sudo apt upgrade
sudo apt install git python3-pip python3-venv libdbus-1-dev libglib2.0-dev virtualenv -y

pip3 install requests bs4 netifaces RPi.GPIO

# MQTT needs to be root to not throw errors
sudo -H pip3 install paho-mqtt


sudo apt install -d -y network-manager
sudo systemctl stop dhcpcd
sudo system disable dhcpcd
sudo apt install network-manager -y

sudo service network-manager restart

# Now NetworkManager should be running
# Connect to wifi via this

nmcli dev wifi

nmcli con add con-name <CONNECTION NAME> ifname wlan0 type wifi ssid <WIFI NAME>


# Turning on this connection
sudo nmcli con up <CONNECTION NAME>
```

Clone the repos

```bash

git clone -b master https://github.com/albertgo080/Drip.git

git clone https://github.com/OpenAgricultureFoundation/python-wifi-connect.git

```

## Install Python-Wifi-Connect

```bash
cd python-wifi-connect
sudo ./scripts/optional_install_NetworkManager_on_Linux.sh
sudo ./scripts/install.sh
```



## Setting up hub to start on boot

```bash
cd Drip\Drip_Hub
sh setup.sh
```
