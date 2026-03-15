import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from functional_tests.base import FunctionalTest


class LoginTest(FunctionalTest):
    """测试Supabase登录功能"""

    def test_login_with_supabase(self):
        """测试用户可以使用Supabase登录"""
        # Edith 访问网站
        self.browser.get(self.live_server_url)

        # 她看到登录按钮显示"Sign in"
        login_link = self.browser.find_element(By.ID, 'login')
        self.assertEqual(login_link.text, 'Sign in')

        # 她点击登录按钮
        login_link.click()

        # Supabase 会弹出OAuth登录窗口
        # 等待新窗口打开
        self.wait_for_new_window()

        # 切换到新窗口（Supabase OAuth页面）
        self.browser.switch_to.window(self.browser.window_handles[-1])

        # 等待登录框加载
        self.wait_for_element_with_id('email')  # Supabase 的邮箱输入框

        # Edith 输入她的邮箱地址
        email_input = self.browser.find_element(By.ID, 'email')
        email_input.send_keys('test@mockmyid.com')

        # 她点击登录按钮
        sign_in_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        sign_in_button.click()

        # 等待窗口关闭，她回到主窗口
        self.wait_for_window_to_close()
        self.browser.switch_to.window(self.browser.window_handles[0])

        # 她看到登录成功
        # 由于 Supabase OAuth 会重定向，我们等待一下
        time.sleep(2)

    def wait_for_new_window(self, timeout=10):
        """辅助函数：等待新窗口打开"""
        start_time = time.time()
        while len(self.browser.window_handles) < 2:
            if time.time() - start_time > timeout:
                raise Exception('Timeout waiting for new window')
            time.sleep(0.3)

    def wait_for_window_to_close(self, timeout=10):
        """辅助函数：等待窗口关闭"""
        start_time = time.time()
        initial_handles = set(self.browser.window_handles)

        while True:
            current_handles = set(self.browser.window_handles)
            if len(current_handles) < len(initial_handles):
                return  # 窗口已关闭
            if time.time() - start_time > timeout:
                raise Exception('Timeout waiting for window to close')
            time.sleep(0.3)

    def wait_for_element_with_id(self, element_id, timeout=10):
        """辅助函数：显式等待元素出现"""
        WebDriverWait(self.browser, timeout).until(
            lambda d: d.find_element(By.ID, element_id)
        )
