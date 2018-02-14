# InstagramAnalytics
**CURRENTLY UNDER DEVELOPMENT** <br>
Gets analytics from user's Instagram account.

## Setup Instructions
You must have `python3` and `pip` installed (`pip` is usually automatically installed with newer versions of python)<br>
### Install Selenium
http://www.seleniumhq.org/download/ <br>
Run this in a command window:
```
sudo pip install -U selenium
```
### Install BeautifulSoup4
https://pypi.python.org/pypi/beautifulsoup4 <br>
Run this in a command window:
```
sudo pip install beautifulsoup4
```
### Install Chromedriver
Using Node's package manager (https://nodejs.org/) run this in a command window:
```
npm install chromedriver
```
OR using HomeBrew (https://brew.sh/):
```
brew install chromedriver
```
OR you can download it from https://sites.google.com/a/chromium.org/chromedriver/ <br>
Put the `chromedriver.exe` into your `user/local` folder or follow the instructions below to add it into `user_config.ini`

### Add information into user_config.ini
In `user_config.ini` add your Instagram username, password, and location of chromedriver.exe on your computer if it's not in PATH.
