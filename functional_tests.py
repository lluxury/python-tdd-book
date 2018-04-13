from selenium import webdriver
import os
import sys
os.environ['MOZ_HEADLESS'] = '1'  # <- this line

browser = webdriver.Firefox()
browser.get('http://localhost:8000')

assert 'Django' in browser.title
