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
