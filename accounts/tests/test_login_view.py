"""
Tests for the login view using mocks
"""
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from accounts.views import supabase_auth, EmailBackend
from django.contrib.sessions.middleware import SessionMiddleware


class LoginViewTest(TestCase):
    """
    Test the login view using mocked authentication
    """

    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()

    @patch('accounts.views.authenticate')
    def test_calls_authenticate_with_email(self, mock_authenticate):
        """
        Test that supabase_auth view calls authenticate with email from POST
        """
        # Arrange
        import json
        mock_authenticate.return_value = Mock()
        data = json.dumps({'email': 'test@example.com'})
        request = self.factory.post('/accounts/auth/',
                                    data=data,
                                    content_type='application/json')

        # Add session support
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Act
        response = supabase_auth(request)

        # Assert
        mock_authenticate.assert_called_once()

    @patch('accounts.views.authenticate')
    def test_returns_ok_when_user_found(self, mock_authenticate):
        """
        Test that view returns OK status when user is found
        """
        # Arrange
        import json
        from django.contrib.sessions.middleware import SessionMiddleware

        # Mock authenticate to return a user
        mock_user = Mock()
        mock_user.email = 'test@example.com'
        mock_user.is_authenticated = True
        mock_authenticate.return_value = mock_user

        data = json.dumps({'email': 'test@example.com'})
        request = self.factory.post('/accounts/auth/',
                                    data=data,
                                    content_type='application/json')

        # Add session support
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Act
        response = supabase_auth(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        import json
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['email'], 'test@example.com')

    @patch('accounts.views.authenticate')
    @patch('accounts.views.login')
    def test_logs_in_user_if_authenticate_returns_user(self, mock_login, mock_authenticate):
        """
        Test that user gets logged into session when authenticate returns a user
        """
        # Arrange
        import json
        from django.contrib.sessions.middleware import SessionMiddleware

        # Mock authenticate to return a user
        mock_user = Mock()
        mock_user.email = 'test@example.com'
        mock_user.is_authenticated = True
        mock_authenticate.return_value = mock_user

        data = json.dumps({'email': 'test@example.com'})
        request = self.factory.post('/accounts/auth/',
                                    data=data,
                                    content_type='application/json')

        # Add session support
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Act
        response = supabase_auth(request)

        # Assert
        mock_authenticate.assert_called_once()
        mock_login.assert_called_once_with(request, mock_user, backend='accounts.views.EmailBackend')
        self.assertEqual(response.status_code, 200)

    @patch('accounts.views.authenticate')
    @patch('accounts.views.login')
    def test_does_not_login_if_authenticate_returns_none(self, mock_login, mock_authenticate):
        """
        Test that user is NOT logged in if authenticate returns None
        """
        # Arrange
        import json
        from django.contrib.sessions.middleware import SessionMiddleware

        # Mock authenticate to return None (authentication fails)
        mock_authenticate.return_value = None

        data = json.dumps({'email': 'nonexistent@example.com'})
        request = self.factory.post('/accounts/auth/',
                                    data=data,
                                    content_type='application/json')

        # Add session support
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Act
        response = supabase_auth(request)

        # Assert
        mock_authenticate.assert_called_once()
        mock_login.assert_not_called()
        self.assertEqual(response.status_code, 400)
