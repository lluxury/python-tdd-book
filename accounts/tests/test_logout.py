"""
Tests for logout functionality
"""
from unittest.mock import patch
from django.test import TestCase, RequestFactory, Client
from accounts.views import supabase_logout
from accounts.models import ListUser


class LogoutViewTest(TestCase):
    """
    Test user logout functionality
    """

    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.client = Client()

    def test_logout_view_exists(self):
        """
        Test that logout view exists and is accessible
        """
        # Arrange
        from django.contrib.sessions.middleware import SessionMiddleware
        request = self.factory.get('/accounts/logout/')

        # Add session support
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Act
        response = supabase_logout(request)

        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response.url, '/')

    def test_user_can_logout(self):
        """
        Test that logged in user can log out
        """
        # Arrange - create and login user
        user = ListUser.objects.create_user(email='test@example.com')
        self.client.force_login(user, backend='accounts.views.EmailBackend')

        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        # Act - logout
        response = self.client.get('/accounts/logout/')

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_user_session_is_cleared_after_logout(self):
        """
        Test that user session is cleared after logout and stays logged out after refresh
        """
        # Arrange - create and login user
        user = ListUser.objects.create_user(email='test@example.com')
        self.client.force_login(user, backend='accounts.views.EmailBackend')

        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

        # Act - logout
        response = self.client.get('/accounts/logout/')

        # Assert - session should be cleared
        self.assertFalse('_auth_user_id' in self.client.session)

        # Simulate refresh - access another page
        response = self.client.get('/')

        # User should still be logged out
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_button_works(self):
        """
        Test that clicking logout button successfully logs out user
        """
        # Arrange - create and login user
        user = ListUser.objects.create_user(email='test@example.com')
        self.client.force_login(user, backend='accounts.views.EmailBackend')

        # Act - access logout endpoint (simulating button click)
        response = self.client.get('/accounts/logout/')

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        # Verify redirect happens to home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
