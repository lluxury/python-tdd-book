"""
Debug test for sharing functionality
分享功能调试测试
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from accounts.models import ListUser


class SharingDebugTest(FunctionalTest):
    """调试分享功能的测试"""

    def test_simple_share(self):
        """简单的分享测试"""
        # 创建用户A和B
        user_a = ListUser.objects.create_user(email='a@debug.com')
        user_b = ListUser.objects.create_user(email='b@debug.com')

        # 为用户A创建session
        session = SessionStore()
        session['_auth_user_id'] = str(user_a.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user_a.get_session_auth_hash())
        session.save()

        # 设置cookie
        self.browser.get(self.server_url + '/')
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

        # 用户A访问首页并创建清单
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Debug item')
        inputbox.send_keys(Keys.ENTER)

        # 获取清单URL
        list_url = self.browser.current_url
        print(f"List URL: {list_url}")

        # 通过数据库直接分享给用户B
        from lists.models import List
        match = __import__('re').search(r'/lists/(\d+)/', list_url)
        if match:
            list_id = match.group(1)
            list_ = List.objects.get(id=list_id)
            list_.shared_with.add(user_b)
            print(f"Shared list {list_id} with user {user_b.email}")

        # 创建用户B的浏览器
        user_b_browser = self.create_new_browser_session()

        # 为用户B创建session
        session_b = SessionStore()
        session_b['_auth_user_id'] = str(user_b.id)
        session_b['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session_b['_auth_user_hash'] = str(user_b.get_session_auth_hash())
        session_b.save()

        # 设置用户B的cookie
        user_b_browser.get(self.server_url + '/')
        user_b_browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session_b.session_key,
            'path': '/',
        })

        # 用户B访问清单
        print(f"User B visiting: {list_url}")
        user_b_browser.get(list_url)

        # 打印页面内容用于调试
        body_text = user_b_browser.find_element(By.TAG_NAME, 'body').text
        print(f"Page content: {body_text[:500]}")

        # 检查是否能看到清单内容
        self.assertIn('Debug item', body_text)

        # 清理
        user_b_browser.quit()
        user_a.delete()
        user_b.delete()

    def create_new_browser_session(self):
        """创建新的浏览器会话"""
        from selenium import webdriver
        browser = webdriver.Firefox()
        browser.implicitly_wait(3)
        return browser
