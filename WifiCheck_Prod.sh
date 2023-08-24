#!/usr/bin/bash

ping -c4 8.8.8.8 > /dev/null


if [ $? != 0 ]
then
  echo "Internet is down, restarting wlan0"
  sudo systemctl stop Data_Logger.service # Replace with the name of your service. If you're on ethernet you probably don't need this, but with wifi being so unreliable in my environment this was necessary. 
  sudo ip link set wlan0 down
  echo "Data Logger Stopped"
  sleep 15
  sudo ip link set wlan0 up
  sudo systemctl start Data_Logger.service
  echo "Data Logger Started"

else
    echo "Internet is up, Data Logger Running."

fi
