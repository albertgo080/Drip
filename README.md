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
sudo apt install git python3-pip -y

sudo reboot

pip3 install requests bs4 netifaces RPi.GPIO

# MQTT needs to be root to not throw errors
sudo -H pip3 install paho-mqtt
```

Clone the repos

```bash

git clone -b master https://github.com/albertgo080/Drip.git

git clone https://github.com/OpenAgricultureFoundation/python-wifi-connect.git

```
