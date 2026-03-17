"""
Functional tests for authenticated list operations
支持本地和 staging 服务器运行
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time
from accounts.models import ListUser


class MyListsTest(FunctionalTest):
    """
    Test list operations with pre-created session
    可以在本地或 staging 服务器上运行
    """

    def setUp(self):
        """Create a user before each test"""
        # Call parent setUp to initialize browser and server_url
        # 调用父类 setUp 来初始化 browser 和 server_url
        super().setUp()

        # Create a test user (only for local testing)
        # 创建测试用户（仅用于本地测试）
        if not self.against_staging:
            self.user_email = 'test@example.com'
            self.user = ListUser.objects.create_user(email=self.user_email)
        else:
            # On staging, use a pre-existing test user
            # 在 staging 上，使用已存在的测试用户
            self.user_email = 'staging-test@example.com'
            self.user = None  # Don't create/delete users on staging

    def test_login_and_access_homepage(self):
        """
        Test that user can login and access homepage
        测试用户可以登录并访问首页
        """
        # Edith goes to the home page
        # 使用 server_url 而不是 live_server_url，支持 staging 服务器
        self.browser.get(self.server_url)

        # She clicks sign in
        login_link = self.browser.find_element(By.ID, 'login')
        self.assertIn('Sign in', login_link.text)
        login_link.click()

        # Login modal appears
        modal = WebDriverWait(self.browser, 10).until(
            lambda d: d.find_element(By.ID, 'login-modal') or
                       d.find_element(By.ID, 'login-modal')  # Try both
        )

        # Wait for modal to be visible
        WebDriverWait(self.browser, 10).until(
            lambda d: d.find_element(By.ID, 'email').is_displayed()
        )

        # She enters her email
        email_input = self.browser.find_element(By.ID, 'email')
        email_input.clear()
        email_input.send_keys(self.user_email)

        # Submits to send magic link
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for success message
        WebDriverWait(self.browser, 10).until(
            lambda d: '登录链接已发送' in d.find_element(By.ID, 'login-message').text
        )

    def test_user_displays_logged_in_status(self):
        """
        Test that user can see they are logged in
        测试用户可以看到他们已经登录
        """
        # Edith has already logged in (via magic link)
        # She refreshes the page
        # 使用 server_url 而不是 live_server_url，支持 staging 服务器
        self.browser.get(self.server_url)

        # She sees that the login link now shows "Sign out" with her email
        logout_link = self.wait_for_element_by_id('login')
        self.assertIn('Sign out', logout_link.text)
        self.assertIn(self.user_email, logout_link.text)

    def tearDown(self):
        """Clean up after test"""
        # Delete the test user (only for local testing)
        # 删除测试用户（仅用于本地测试）
        if not self.against_staging and hasattr(self, 'user') and self.user:
            self.user.delete()

        # Then quit browser (from parent class)
        # 然后退出浏览器（来自父类）
        super().tearDown()
