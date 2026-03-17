"""
Functional tests for list sharing feature
清单分享功能的功能测试
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from accounts.models import ListUser


class ListSharingTest(FunctionalTest):
    """
    Test list sharing functionality between users
    测试用户之间的清单分享功能
    """

    def test_logged_in_users_can_save_lists(self):
        """
        测试已登录用户可以保存清单
        Test 1: 用户A已登录，访问首页，新建清单
        """
        # User A 创建一个邮箱
        user_a_email = 'a@example.com'
        user_a = ListUser.objects.create_user(email=user_a_email)

        # 创建 session 并设置 cookie（模拟登录）
        self.create_pre_authenticated_session(user_a.email)
        self.addCleanup(lambda: self.cleanup_user(user_a_email))

        # User A 访问首页
        self.browser.get(self.server_url)

        # User A 创建一个新清单
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # 等待重定向到清单页面
        import time
        time.sleep(1)

        # User A 看到清单页面，并且 URL 是特定于这个清单的
        list_url = self.browser.current_url
        self.assertRegex(list_url, '/lists/.+')
        self.wait_for_text('Buy peacock feathers')

    def test_list_owner_can_see_share_option(self):
        """
        测试清单所有者可以看到分享选项
        Test 1: 用户A新建清单后看到分享清单选项
        """
        # User A 创建并登录
        user_a_email = 'edith@example.com'
        user_a = ListUser.objects.create_user(email=user_a_email)
        self.create_pre_authenticated_session(user_a.email)
        self.addCleanup(lambda: self.cleanup_user(user_a_email))

        # User A 访问首页，创建一个新清单
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # User A 看到清单页面
        self.wait_for_text('Buy peacock feathers')

        # User A 看到有一个分享框
        # 这个框让用户输入要分享给的邮箱地址
        share_box = self.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

    def test_shared_list_visible_to_shared_user(self):
        """
        测试分享的清单对被分享用户可见
        Test 3: 用户B访问清单，看到了A分享的清单
        """
        # User A 创建并登录
        user_a_email = 'a@example.com'
        user_a = ListUser.objects.create_user(email=user_a_email)
        self.create_pre_authenticated_session(user_a.email)
        self.addCleanup(lambda: self.cleanup_user(user_a_email))

        # User A 创建一个清单
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # 等待重定向到清单页面
        import time
        time.sleep(1)

        # User A 看到清单页面
        list_url = self.browser.current_url
        self.assertRegex(list_url, r'/lists/\d+/')
        self.wait_for_text('Buy peacock feathers')

        # User A 分享清单给 User B（通过表单UI）
        user_b_email = 'b@example.com'
        user_b = ListUser.objects.create_user(email=user_b_email)
        self.addCleanup(lambda: self.cleanup_user(user_b_email))

        # 通过表单分享：填写b的邮件地址，点击分享按钮
        share_box = self.get_share_box()
        share_box.send_keys(user_b_email)

        share_button = self.browser.find_element(By.CSS_SELECTOR, 'button[name="share"]')
        share_button.click()

        time.sleep(1)  # 等待分享完成

        # 现在 User B 登录（使用新的浏览器会话）
        user_b_browser = self.create_new_browser_session()
        self.create_pre_authenticated_session(user_b_email, browser=user_b_browser)

        # User B 访问 User A 分享的清单 URL
        user_b_browser.get(list_url)

        # 等待页面加载
        self.wait_for_text('Buy peacock feathers', browser=user_b_browser)

        # User B 看到了 User A 的清单
        body_text = user_b_browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Buy peacock feathers', body_text)

        # 清理：关闭 User B 的浏览器
        user_b_browser.quit()

    def test_shared_list_appears_in_my_lists(self):
        """
        测试分享的清单出现在"我的清单"页面
        Test 4: 用户B到"我的清单"页面，看到A的清单
        """
        # User A 创建并登录
        user_a_email = 'edith@example.com'
        user_a = ListUser.objects.create_user(email=user_a_email)
        self.create_pre_authenticated_session(user_a.email)
        self.addCleanup(lambda: self.cleanup_user(user_a_email))

        # User A 创建一个清单
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # 等待重定向到清单页面
        import time
        time.sleep(1)

        list_url = self.browser.current_url
        self.wait_for_text('Buy peacock feathers')

        # User A 分享清单给 User B
        user_b_email = 'francis@example.com'
        ListUser.objects.create_user(email=user_b_email)
        self.addCleanup(lambda: self.cleanup_user(user_b_email))
        self.share_list_with(user_b_email)

        # User B 登录
        user_b_browser = self.create_new_browser_session()
        self.create_pre_authenticated_session(user_b_email, browser=user_b_browser)

        # User B 去到"我的清单"页面
        user_b_browser.get(self.server_url + '/my-lists/')

        # User B 看到了 User A 的清单
        body_text = user_b_browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Buy peacock feathers', body_text)

        # 清理
        user_b_browser.quit()

    def test_both_users_can_add_items_to_shared_list(self):
        """
        测试两个用户都可以向共享清单添加项目
        Test 5: 用户B添加项目，用户A刷新后能看到
        """
        # User A 创建并登录
        user_a_email = 'a@example.com'
        user_a = ListUser.objects.create_user(email=user_a_email)
        self.create_pre_authenticated_session(user_a.email)
        self.addCleanup(lambda: self.cleanup_user(user_a_email))

        # User A 创建一个清单
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # 等待重定向到清单页面
        import time
        time.sleep(1)

        list_url = self.browser.current_url
        self.wait_for_text('Buy peacock feathers')

        # User A 分享清单给 User B
        user_b_email = 'b@example.com'
        ListUser.objects.create_user(email=user_b_email)
        self.addCleanup(lambda: self.cleanup_user(user_b_email))
        self.share_list_with(user_b_email)

        # User B 登录（使用新的浏览器会话）
        user_b_browser = self.create_new_browser_session()
        self.create_pre_authenticated_session(user_b_email, browser=user_b_browser)

        # User B 访问分享的清单
        user_b_browser.get(list_url)

        # 等待页面加载
        self.wait_for_text('Buy peacock feathers', browser=user_b_browser)

        body_text = user_b_browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Buy peacock feathers', body_text)

        # User B 向清单添加一个项目
        inputbox_b = user_b_browser.find_element(By.ID, 'id_new_item')
        inputbox_b.send_keys('Buy milk')
        inputbox_b.send_keys(Keys.ENTER)

        # User B 等待新项目出现
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(user_b_browser, 10).until(
            lambda d: 'Buy milk' in d.find_element(By.TAG_NAME, 'body').text
        )

        # 清理 User B 的浏览器
        user_b_browser.quit()

        # User A 刷新清单页面
        self.browser.get(list_url)

        # User A 看到 User B 添加的项目
        self.wait_for_text('Buy milk')

    # 辅助方法
    def create_pre_authenticated_session(self, email, browser=None):
        """创建预先认证的 session"""
        if browser is None:
            browser = self.browser

        # 创建用户
        user = ListUser.objects.get(email=email)

        # 创建 session
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user.get_session_auth_hash())
        session.save()

        # 设置 cookie
        browser.get(self.server_url + '/')
        browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

    def cleanup_user(self, email):
        """清理测试用户"""
        try:
            user = ListUser.objects.get(email=email)
            user.delete()
        except ListUser.DoesNotExist:
            pass

    def create_new_browser_session(self):
        """创建新的浏览器会话"""
        from selenium import webdriver
        browser = webdriver.Firefox()
        browser.implicitly_wait(3)
        return browser

    def get_share_box(self, browser=None):
        """获取分享输入框"""
        if browser is None:
            browser = self.browser

        # TODO: 分享功能还未实现，这个元素还不存在
        # 先返回一个 mock，等实现后再修改
        share_box = browser.find_element(By.ID, 'id_share_email')
        return share_box

    def share_list_with(self, email, browser=None):
        """分享清单给指定用户 - 通过表单UI"""
        if browser is None:
            browser = self.browser

        # 通过表单UI分享清单
        share_box = self.get_share_box(browser=browser)
        share_box.send_keys(email)

        # 点击分享按钮
        share_button = browser.find_element(By.CSS_SELECTOR, 'button[name="share"]')
        share_button.click()

        # 等待分享完成（页面刷新）
        import time
        time.sleep(1)


class ListPage:
    """
    Page Object for List Page
    清单页面的页面对象模式实现

    Test 2: 使用页面模式重构辅助代码
    """

    def __init__(self, test, list_url):
        """初始化页面对象"""
        self.test = test
        self.browser = test.browser
        self.url = list_url

    def go_to(self):
        """访问清单页面"""
        self.browser.get(self.url)

    def add_item(self, item_text):
        """向清单添加项目"""
        input_box = self.browser.find_element(By.ID, 'id_new_item')
        input_box.send_keys(item_text)
        input_box.send_keys(Keys.ENTER)

    def get_share_box(self):
        """获取分享输入框"""
        share_box = self.browser.find_element(By.ID, 'id_share_email')
        return share_box

    def share_list_with(self, email):
        """分享清单给指定用户"""
        share_box = self.get_share_box()
        share_box.send_keys(email)

        # 找到分享按钮并点击
        share_button = self.browser.find_element(By.CSS_SELECTOR, 'button[name="share"]')
        share_button.send_keys(Keys.ENTER)

    def wait_for_item_in_list(self, item_text):
        """等待项目出现在清单中"""
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.browser, 10).until(
            lambda d: item_text in d.find_element(By.TAG_NAME, 'body').text
        )

    def get_list_owner(self):
        """获取清单所有者信息"""
        try:
            owner_element = self.browser.find_element(By.ID, 'id_list_owner')
            return owner_element.text
        except:
            return None

    def get_shared_with_users(self):
        """获取分享的用户列表"""
        try:
            shared_users = self.browser.find_elements(By.CSS_SELECTOR, '.list-shared-with')
            return [user.text for user in shared_users]
        except:
            return []

    def wait_until_list_updated(self):
        """等待清单页面更新"""
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.browser, 10).until(
            lambda d: d.find_element(By.ID, 'id_list_table')
        )
