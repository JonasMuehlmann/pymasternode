#!/bin/bash

#Creates swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

#Updates packages and installs fail2ban
apt update
apt full-upgrade -y
apt install fail2ban -y

#Activate persistent storage for logs
sed -n -i 's/#Storage=auto/Storage=persistent/g' /etc/systemd/journald.conf