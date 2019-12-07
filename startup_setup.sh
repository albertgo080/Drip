#!/bin/bash

# Keep track of user that called script for when using root commands
export BASEUSR=$USER

cd

# Make Triton startup script
echo "#!/bin/bash
/home/$BASEUSR/python-wifi-connect/scripts/run.sh
/home/$BASEUSR/Drip/Drip_Hub/run.sh" > triton

chmod +x ./triton

echo 'Created hub start up script'

# Install Prequisites

# MQTT needs to be root to not throw errors
# sudo -H pip3 install paho-mqtt

# Make run file

echo "#!/bin/bash
echo 'Must be run with sudo'
python3 /home/$BASEUSR/Drip/Drip_Hub/main.py
" > /home/$BASEUSR/Drip/Drip_Hub/run.sh

chmod +x /home/$BASEUSR/Drip/Drip_Hub/run.sh

# Make system start up file

sudo -E sh -c 'echo "[Unit]
Description=the triton system
After=network.target network-online.target NetworkManager.service
Wants=network-online.target

[Service]
WorkingDirectory=/home/$BASEUSR

Type=simple
ExecStart=/home/$BASEUSR/triton

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/triton.service'

sudo systemctl daemon-reload

sudo systemctl enable triton


echo 'Created and enabled Triton start up service'

echo 'Run sudo systemctl start triton to start the hub without restarting'
