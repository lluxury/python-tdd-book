from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from django.test import LiveServerTestCase
from django.conf import settings
import unittest
import time
import os


class FunctionalTest(LiveServerTestCase):
    """功能测试基类"""

    def setUp(self):
        # Check if running against staging server
        # 检查是否在 staging 服务器上运行
        staging_server = os.environ.get('STAGING_SERVER') or getattr(settings, 'STAGING_SERVER', None)

        if staging_server and staging_server != 'localhost':
            # Running against staging server
            # 在 staging 服务器上运行
            self.against_staging = True
            # Use staging server URL instead of live_server_url
            # 使用 staging 服务器 URL 而不是 live_server_url
            self.server_url = f'http://{staging_server}'
        else:
            # Running locally
            # 本地运行
            self.against_staging = False
            self.server_url = self.live_server_url

        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        """辅助方法：检查表格中是否包含指定文本的行"""
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertTrue(any(row.text == row_text for row in rows))

    def get_item_input_box(self):
        """辅助方法：获取待办事项输入框"""
        return self.browser.find_element(By.ID, "id_new_item")

    def get_error_element(self):
        """辅助方法：获取错误消息元素"""
        return self.browser.find_element(By.CSS_SELECTOR, ".has-error")

    def wait_for_element(self, locator, timeout=10):
        """辅助函数：等待元素出现"""
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.presence_of_element_located(locator)
        )

    def wait_for_element_by_id(self, element_id, timeout=10):
        """辅助函数：等待ID元素出现"""
        return WebDriverWait(self.browser, timeout).until(
            lambda d: d.find_element(By.ID, element_id)
        )

    def wait_for_text(self, text, timeout=10):
        """辅助函数：等待文本出现在页面中"""
        return WebDriverWait(self.browser, timeout).until(
            lambda d: text in d.find_element(By.TAG_NAME, 'body').text
        )

    def login(self, email):
        """辅助函数：使用给定邮箱登录"""
        # Go to home page
        self.browser.get(self.live_server_url)

        # Click sign in
        login_link = self.wait_for_element_by_id('login')
        login_link.click()

        # Wait for modal and enter email
        self.wait_for_element_by_id('email')
        email_input = self.browser.find_element(By.ID, 'email')
        email_input.clear()
        email_input.send_keys(email)

        # Submit form
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for success message
        self.wait_for_text('登录链接已发送')

    def logout(self):
        """辅助函数：退出登录"""
        # Find and click logout link
        try:
            logout_link = self.wait_for_element(By.XPATH, "//a[contains(text(), 'Sign out')]", timeout=5)
            logout_link.click()
        except:
            pass  # No logout link found, user might already be logged out
