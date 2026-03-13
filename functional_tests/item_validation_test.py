import time
import unittest
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class ItemValidationTest(FunctionalTest):
    """测试待办事项验证"""

    def test_cannot_add_empty_list_items(self):
        """测试不能提交空的待办事项"""
        # Edith访问首页
        self.browser.get(self.live_server_url)

        # 禁用HTML5验证以测试服务器端验证
        self.browser.execute_script("document.getElementById('id_new_item').removeAttribute('required')")

        # 输入框为空时她按下了回车
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 页面刷新，显示错误消息
        # .has-error 表示错误状态
        error = self.browser.find_element(By.CSS_SELECTOR, ".has-error")
        self.assertEqual(error.text, "You can't have an empty list item")

        # Edith输入文字，提交成功
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)
        self.check_for_row_in_list_table("1: Buy milk")

        # Edith再次提交空事项
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        # 再次禁用HTML5验证（新页面）
        self.browser.execute_script("document.getElementById('id_new_item').removeAttribute('required')")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 再次显示错误消息
        self.check_for_row_in_list_table("1: Buy milk")
        error = self.browser.find_element(By.CSS_SELECTOR, ".has-error")
        self.assertEqual(error.text, "You can't have an empty list item")

        # Edith输入文字，提交成功
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Make tea")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)
        self.check_for_row_in_list_table("1: Buy milk")
        self.check_for_row_in_list_table("2: Make tea")

    def test_cannot_add_duplicate_items(self):
        """测试不能添加重复的待办事项"""
        # Edith访问首页并添加一个待办事项
        self.browser.get(self.live_server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys("Buy wellies")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)
        self.check_for_row_in_list_table("1: Buy wellies")

        # 她不小心输入了相同的待办事项
        inputbox = self.get_item_input_box()
        inputbox.send_keys("Buy wellies")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 她看到一个有用的错误消息
        error = self.browser.find_element(By.CSS_SELECTOR, ".has-error")
        self.assertEqual(error.text, "You've already got this in your list")

    def test_error_messages_are_cleared_on_input(self):
        """测试错误消息在输入内容时消失"""
        # Edith访问首页
        self.browser.get(self.live_server_url)

        # 禁用HTML5验证
        self.browser.execute_script("document.getElementById('id_new_item').removeAttribute('required')")

        # 输入空内容并提交
        inputbox = self.get_item_input_box()
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 应该看到错误消息
        error = self.get_error_element()
        self.assertEqual(error.text, "You can't have an empty list item")

        # 她输入内容后，错误消息应该消失
        inputbox = self.get_item_input_box()
        inputbox.send_keys("Go shopping")
        time.sleep(1)

        # 错误消息应该不再显示
        errors = self.browser.find_elements(By.CSS_SELECTOR, ".has-error")
        self.assertEqual(len(errors), 0)
