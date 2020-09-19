#!/bin/bash

apt-get -y update
apt-get -y update; apt-get -y install gnupg
apt-get --assume-yes install wget
apt-get -y install xvfb
apt-get install -y libxkbcommon-x11-0
apt-get -y install x11-utils
apt-get install -yqq unzip
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get -y update
apt-get install -y google-chrome-stable
wget -q https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chown root:root /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
mkdir /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
chown root /tmp/.X11-unix/