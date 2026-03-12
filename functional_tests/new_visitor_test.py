import time
from functional_tests.base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class NewVisitorTest(FunctionalTest):
    """测试新用户的待办事项列表体验"""

    def test_can_start_a_list_and_retrieve_it_later(self):
        """用户可以开始一个待办事项列表并在之后查看"""
        # 用户访问主页
        self.browser.get(self.live_server_url)

        # 用户注意到页面标题和头部都包含"To-Do"
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do", header_text)

        # 用户看到一个输入框，提示输入待办事项
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a to-do item")

        # 用户输入"买羽毛"
        inputbox.send_keys("买羽毛")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # 等待页面加载

        # URL发生变化，变成唯一的清单URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        self.assertNotEqual(edith_list_url, self.live_server_url + '/')

        # 页面更新，表格中显示"1: 买羽毛"
        self.check_for_row_in_list_table("1: 买羽毛")

        # 用户输入第二个待办事项
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Use peacock")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # 等待页面加载

        # 页面再次更新，显示两个待办事项
        self.check_for_row_in_list_table("1: 买羽毛")
        self.check_for_row_in_list_table("2: Use peacock")

        # Edith好奇她的清单是否会被记住，她看到网站为此生成了一个唯一的URL
        # 页面上有文字说明这个URL

        # 她访问那个URL，她的待办事项列表还在

        # 满意后，她去睡觉了

        # 现在一个新用户Francis来到网站

        # 我们使用一个新的浏览器session来确保Edith的信息不会从cookies中泄露出来
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis访问首页
        # Edith的清单不会显示
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("买羽毛", page_text)
        self.assertNotIn("Use peacock", page_text)

        # Francis输入一个新的待办事项
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # Francis获得了他自己的唯一URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 再次确认Edith的清单不在页面上
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("买羽毛", page_text)
        self.assertIn("Buy milk", page_text)

        # 满意后，他们也去睡觉了
