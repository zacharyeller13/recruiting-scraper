# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 14:07:02 2021

@author: zacharye
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import date
import pandas as pd
import os
from time import sleep

import keyring

today = date.today()

# set working directory
os.chdir('C:/Users/zacharye/Documents/PythonScripts/recruiting-scraper')

# login information; using keyring to avoid hard coding username and password
credentials = keyring.get_credential("BigBiller", None)
username = credentials.username
password = credentials.password
website = 'https://bigbiller.topechelon.com/login'

# set profile for downloads
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", "C:\\Users\\zacharye\\Documents\\PythonScripts\\recruiting-scraper")
profile.set_preference("app.update.auto", False)
profile.set_preference("app.update.enabled", False)
profile.set_preference("app.udpate.silent", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/x-msexcel,application/excel,application/x-excel,application/vnd.ms-excel,image/png,image/jpeg,text/html,text/plain,application/msword,application/xml")
profile.update_preferences()

# set headless option
opts = Options()
opts.add_argument('--headless')

# webdriver with profile, headless option, and website
driver = webdriver.Firefox(firefox_profile=profile, options=opts)
driver.implicitly_wait(15)
driver.get(website)

# login
driver.find_element(By.ID, 'email').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_element(By.NAME, 'commit').click()

# check that total count element is loaded on the page
try:
    element_present = EC.presence_of_element_located((By.ID, 'e2e-all-people-total-count'))
    WebDriverWait(driver, 5).until(element_present)
except TimeoutException:
    print("Timed out")
    driver.quit()

# check that total count is loaded and is not '-'
total_techs = driver.find_element(By.ID, 'e2e-all-people-total-count').get_attribute('text')
while '-' in total_techs:
    sleep(1)
    total_techs = driver.find_element(By.ID, 'e2e-all-people-total-count').get_attribute('text')

driver.quit()

df = pd.DataFrame(
    {
         'date': pd.Series(today),
         'techs': pd.Series(total_techs),
    }  
)

df.to_csv('tech_network.csv', mode='a', index=None, header=False)
