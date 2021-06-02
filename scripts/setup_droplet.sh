#!/bin/bash

# Ubuntu 20.04 LTS
sudo apt-get update
sudo apt-get install git python-virtualenv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind

# add user cowrie to use as we do not want to run cowrie as root
sudo adduser --disabled-password cowrie
sudo su - cowrie

# download cowrie code
git clone http://github.com/cowrie/cowrie
cd cowrie

# setup virtual environment for honeypot (as we use a faked OS)
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# let's modify the configuration
cp /home/cowrie/cowrie/etc/cowrie.cfg.dist /home/cowrie/cowrie/etc/cowrie.cfg

# change everything you want in the cowrie.cfg file
# maybe we should listen on port 22 for SSH
# hostname = Ubuntu_20_04_LTS
# listen_endpoints = tcp:22:interface=0.0.0.0

echo "CHANGING THE CONFIG IN /home/cowrie/cowrie/etc/cowrie.cfg"
echo "Changing hostname to UBUNTU_20_04_LTS"
sed -i '/hostname =/c\hostname = UBUNTU_20_04_LTS' /home/cowrie/cowrie/etc/cowrie.cfg
echo "Changing listening SSH Port to 22"
sed -i '/listen_endpoints =/c\listen_endpoints = tcp:22:interface=0.0.0.0' /home/cowrie/cowrie/etc/cowrie.cfg


echo "[ENTER] if done with all changes, shouldn't need more" $enter

# necessary commands to enable non-root to listen on port 22
sudo apt-get install authbind
sudo touch /etc/authbind/byport/22
sudo chown cowrie:cowrie /etc/authbind/byport/22
sudo chmod 770 /etc/authbind/byport/22

# edit the file /etc/ssh/sshd_config to make REAL SSH port listen on random port
echo "Setting real SSH Port to 2112"
sed -i '/#Port /c\Port 2112' /etc/ssh/sshd_config

# restart ssh service
echo "restarting ssh service.."
service ssh restart


# cowrie under supervisored to be able to daemonize
#apt install supervisor
#cd /etc/supervisor/conf.d/
#touch cowrie.conf
#mkdir -p "/home/cowrie/cowrie/var/log/cowrie" && touch /home/cowrie/cowrie/var/log/cowrie/cowrie.out
#touch /home/cowrie/cowrie/var/log/cowrie/cowrie.err

#echo "[program:cowrie]" >>cowrie.conf 2>&1
#echo "command=/home/cowrie/cowrie/bin/cowrie start" >>cowrie.conf 2>&1
#echo "directory=/home/cowrie/cowrie" >>cowrie.conf 2>&1
#echo "stdout_logfile=/home/cowrie/cowrie/var/log/cowrie/cowrie.out" >>cowrie.conf 2>&1
#echo "stderr_logfile=/home/cowrie/cowrie/var/log/cowrie/cowrie.err" >>cowrie.conf 2>&1
#echo "autostart=true" >>cowrie.conf 2>&1
#echo "autorestart=true" >>cowrie.conf 2>&1
#echo "stopasgroup=true" >>cowrie.conf 2>&1
#echo "killasgroup=true" >>cowrie.conf 2>&1
#echo "user=cowrie" >>cowrie.conf 2>&1

# supervisorctl update

# list tcp connections
netstat -at

# redirect traffic from 22 to 2222
iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223

# log file is in
# /home/cowrie/cowrie/var/log/cowrie/cowrie.log cowrie.json
# check if loggin works
# tail -n 10 /home/cowrie/cowrie/var/log/cowrie/cowrie.json


# Files of interest
# https://cowrie.readthedocs.io/en/latest/README.html
