Follow this guide to get the raspiberry pi example script running.  Refer to the driver library [README](https://github.com/SpaceTeddy/CC1101) for details, and also for building the arduino code.


## First Remove WiringPi if it exists

```bash
sudo apt purge wiringpi
hash -r

# Update pi
sudo apt update
sudo apt upgrade
```

There may be 'upgrade' errors due to Ubuntu MATE, if so try
```bash
sudo dpkg -i --force-all /var/cache/apt/archives/linux-firmware-raspi2_1.20190215-0ubuntu0.18.04.1_armhf.deb

sudo apt -f install
```

## Turn on SPI and GPIO

```bash
sudo raspi-config
```

Interfacing Options -> I2C On (Actually changes SPI on MATE), Remote GPIO On

```bash
sudo reboot
```

## Install Wiring Pi

```bash
cd
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
./build
```

This should build WiringPi successfully and place the header files in `\usr\local\include\`

## Build Raspberry Pi example for CC1101 (refer to [CC1101 README](https:\\github.com/SpaceTeddy/CC1101) for more info)

Copy `cc1100_raspi.cpp` and `cc1100_raspi.h` into the raspi example folder.

```bash
sudo g++ TX_Demo.cpp cc1100_raspi.cpp -o TX_Demo -lwiringPi -lrt -lcrypt
```

## Running

```bash
# Get the user inputs by running with no arguments
./TX_Demo

# Apply arguments to match arduino code
sudo ./TX_Demo -v -a1 -r2 -i1000 -t0 -c1 -f434 -m250
```

# Note on Arduino Install

Not explicit in README, but to include the driver library for arduino, navigate to `~/Arduino/libraries` and make a folder `CC1100`.  Copy in the `cc1100_arduino.*` files, and you should be good to go with the rest of the README.
