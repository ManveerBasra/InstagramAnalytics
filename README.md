# InstagramAnalytics
**IN DEVELOPMENT STILL** <br>
Gets analytics from user's Instagram account.

## Setup Instructions
### Install python3

If python3 is not installed <br>
Run this in a command window:
```
sudo apt-get install python3
```
### Install pip
If pip3 is not installed <br>
Run this in a command window:
```
sudo apt-get install python3-setuptools
sudo easy_install3 pip
sudo mv /usr/local/bin/pip /usr/local/bin/pip-3
```
### Install Selenium
Run this in a command window:
```
sudo pip3 install -U selenium
```
### Install Chromedriver
Make sure you have NodeJS installed (https://nodejs.org/)<br>
Using Node's package manager run this in a command window (Or you can download it from https://sites.google.com/a/chromium.org/chromedriver/):
```
npm install chromedriver
```
Put the `chromedriver.exe` into your `user/local` folder or follow the instructions below to add it into `user_config.ini`


### Add information into ig_access.py
In `user_config.ini` add your Instagram username, password, and location of chromedriver.exe on your computer if it's not in PATH.
