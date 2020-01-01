# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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