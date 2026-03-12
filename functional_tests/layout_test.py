import time
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class LayoutTest(FunctionalTest):
    """测试布局和样式"""

    def test_layout_and_styling(self):
        """测试布局和样式：输入框在1024x768窗口中居中显示"""
        # 用户访问主页
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # 用户看到输入框完美居中
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            512,
            delta=10
        )

        # 用户输入清单项
        inputbox.send_keys("testing")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 输入框仍然完美居中
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            512,
            delta=10
        )

        # 表格也完美居中显示
        table = self.browser.find_element(By.ID, "id_list_table")
        self.assertAlmostEqual(
            table.location["x"] + table.size["width"] / 2,
            512,
            delta=10
        )

        # 检查表格内容格式：数字冒号空格
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn("1: testing", rows[0].text)
