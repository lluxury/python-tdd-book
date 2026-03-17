"""
Functional tests for My Lists feature
My Lists 功能的功能测试
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from accounts.models import ListUser


class MyListsFeatureTest(FunctionalTest):
    """
    Test that logged-in users can see their saved lists
    测试已登录用户可以查看保存的列表
    """

    def test_logged_in_user_can_see_my_lists_link(self):
        """
        Test that a logged-in user sees "My Lists" link after creating a list
        测试已登录用户在创建列表后看到 "My Lists" 链接
        """
        # Create a logged-in user
        email = 'edith@example.com'
        user = ListUser.objects.create_user(email=email)

        # Create session for the user
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user.get_session_auth_hash())
        session.save()

        # Set up browser with the session
        self.browser.get(self.server_url + '/')
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

        # Edith is a logged-in user
        self.browser.get(self.server_url)

        # She creates a new list
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # She notices that her list has a unique URL
        # She also sees a "My Lists" link
        my_lists_link = self.wait_for_element_by_id('my-lists')
        self.assertIsNotNone(my_lists_link)

        # The link should exist with "My Lists" text
        self.assertIn('My Lists', my_lists_link.text)

    def test_logged_in_user_can_create_multiple_lists(self):
        """
        Test that logged-in user can create multiple lists and see them all
        测试已登录用户可以创建多个列表并看到所有列表
        """
        import time

        # Create a logged-in user
        email = 'edith@example.com'
        user = ListUser.objects.create_user(email=email)

        # Create session for the user
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user.get_session_auth_hash())
        session.save()

        # Set up browser with the session
        self.browser.get(self.server_url + '/')
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

        # Edith creates her first list
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # Wait for redirect

        # She returns to home and creates another list
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # Wait for redirect

        # She visits "My Lists" page
        my_lists_link = self.wait_for_element_by_id('my-lists')
        my_lists_link.click()

        # She sees both of her lists displayed
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)

    def test_logged_out_user_does_not_see_my_lists_link(self):
        """
        Test that logged-out user does not see "My Lists" link
        测试未登录用户看不到 "My Lists" 链接
        """
        # Francis visits the site (not logged in)
        self.browser.get(self.server_url)

        # He should not see "My Lists" link
        # Check that the element doesn't exist
        from selenium.common.exceptions import NoSuchElementException
        try:
            my_lists_link = self.browser.find_element(By.ID, 'my-lists')
            # If found, this is a failure
            self.fail("My Lists link should not be visible for logged-out users")
        except NoSuchElementException:
            # This is expected - link should not exist
            pass

    def test_my_lists_link_disappears_after_logout(self):
        """
        Test that "My Lists" link disappears after user logs out
        测试登出后 "My Lists" 链接消失
        """
        # Create a logged-in user
        email = 'edith@example.com'
        user = ListUser.objects.create_user(email=email)

        # Create session for the user
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user.get_session_auth_hash())
        session.save()

        # Set up browser with the session
        self.browser.get(self.server_url + '/')
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
        })

        # Edith logs in and creates a list
        self.browser.get(self.server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        # She sees "My Lists" link
        my_lists_link = self.wait_for_element_by_id('my-lists')
        self.assertIsNotNone(my_lists_link)

        # She logs out
        logout_link = self.browser.find_element(By.ID, 'login')
        logout_link.click()

        # Refresh the page
        self.browser.get(self.server_url)

        # "My Lists" link should not be visible anymore
        from selenium.common.exceptions import NoSuchElementException
        try:
            my_lists_link = self.browser.find_element(By.ID, 'my-lists')
            # If found, this is a failure
            self.fail("My Lists link should not be visible after logout")
        except NoSuchElementException:
            # This is expected - link should not exist
            pass
