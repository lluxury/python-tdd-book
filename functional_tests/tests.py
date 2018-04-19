from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
MAX_WAIT = 10

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")

import time
# import unittest
# import os
# import sys
# os.environ['MOZ_HEADLESS'] = '1'  # <- this line

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):  
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='/home/yann/chromedriver')
        #  self.browser = webdriver.Firefox()

    def tearDown(self):  
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:

                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows  = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self): 
        # check out it's homepage
        self.browser.get(self.live_server_url)
        # self.browser.get_screenshot_as_file('home_page.png')

        # notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)  
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # enter a to-do item straight away 
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # types "Buy peacock feathers"
        inputbox.send_keys("Buy peacock feathers")
        inputbox.send_keys(Keys.ENTER)
        # inputbox.send_keys(Keys.Enter)

        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        # self.browser.get_screenshot_as_file('home_page.png')

        # table = self.browser.find_element_by_id('id_list_table')
        # rows = table.find_elements_by_tag_name('tr')
        # rows = table.find_element_by_tag_name('tr') 
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('1: Buy peacock feathers')


        self.fail('Finish the test!')


