#!/bin/bash

#Donwloads and sets up wallet
wget http://cryptopowered.club/glt/setup.sh
chmod 777 setup.sh
./setup.sh %s
sleep 10
/root/globaltoken/bin/globaltoken-cli -getinfo | grep [b]locks
systemctl start globaltoken.service
