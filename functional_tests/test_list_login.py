"""
Functional tests for list operations with pre-created session
跳过登录过程，直接使用预创建的会话测试列表功能
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client
from django.contrib.auth import login
from accounts.models import ListUser


class ListLoginTest(FunctionalTest):
    """
    Test list operations with pre-created session
    使用预创建会话测试列表操作
    """

    def setUp(self):
        """Set up test with pre-created user and session"""
        super().setUp()

        # Create a test user
        self.user_email = 'edith@example.com'
        self.user = ListUser.objects.create_user(email=self.user_email)

        # Create an authenticated session using Django Client
        # This simulates the user being logged in
        from django.contrib.auth import get_user_model

        # Create session and authenticate user
        self.session = SessionStore()

        # Use the correct format for Django session authentication
        self.session['_auth_user_id'] = str(self.user.id)
        self.session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        self.session['_auth_user_hash'] = str(self.user.get_session_auth_hash())
        self.session.save()

        # Now set up the browser with this session
        # First visit the page to set the domain for cookies
        self.browser.get(self.live_server_url + '/')

        # Then add the pre-created session cookie
        self.browser.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': self.session.session_key,
            'path': '/',
            'domain': None,  # Let browser use current domain
        })

    def test_logged_in_user_can_access_lists(self):
        """
        Test that a user with pre-created session can access the homepage
        and see their logged-in status without going through login process
        """
        # Edith has already been authenticated via pre-created session
        # She goes to the home page
        self.browser.get(self.live_server_url)

        # She sees that she is already logged in
        # The login link should show "Sign out" instead of "Sign in"
        # And her email should be displayed
        auth_section = self.browser.find_element(By.ID, 'auth-section')
        self.assertIn('Sign out', auth_section.text)
        self.assertIn(self.user_email, auth_section.text)

        # Verify the login link element exists and shows "Sign out"
        login_link = self.wait_for_element_by_id('login')
        self.assertIn('Sign out', login_link.text)

        # She can see the input box to add items (verifying she can use the app)
        inputbox = self.get_item_input_box()
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

    def tearDown(self):
        """Clean up test data"""
        # Delete the test user
        if hasattr(self, 'user') and self.user:
            self.user.delete()

        # Clean up session
        super().tearDown()
