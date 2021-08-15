#!/bin/bash


# RAM Disk
RAMDISK_LOCATION="/tmp/ramdisk"
INSTALL_SCRIPT_LOCATION="codebase/install.sh"


# Update if needed.
echo " [+] Checking for updates..."
git pull
sudo apt-get -y install python3-pip
pip3 --version

echo " [+] Installing deps..."
pip3 install -r requirements.txt

script_running=$(ps -ef | grep "driver.py" | grep -v "grep")
var_length=`expr length "${script_running}"`

# Check if another instace of the script is running.
if [ $var_length == 0 ]; then
    if [ -d "$RAMDISK_LOCATION" ]; then
        # Since there is no other instance running, start.
        python3 setupAndRun.py

        # Sleep for 10 mins, this is used as a cool down
        sleep 600
    else
        # Couldnt find the tmpfs ramdisk location, there was an issue with setting up the environment.
        echo " [+] No RamDisk found, attempting to fix by running install, if this error keeps occuring please manually make a tmpfs folder called 'ramdisk' with the following path: '$RAMDISK_LOCATION'"
        if [ -d "$INSTALL_SCRIPT_LOCATION" ]; then
            echo " [+] Starting install."
            sh INSTALL_SCRIPT_LOCATION
        else
            echo " [+] Could not find install script, trying clean install."
            python3 setupAndRun.py
        fi
    fi
else
echo " [+] Already running. Quiting."
fi
