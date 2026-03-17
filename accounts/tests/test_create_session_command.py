"""
Tests for create_session management command
测试 create_session 管理命令
"""
from django.test import TestCase
from django.core.management import call_command
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from io import StringIO
import sys


User = get_user_model()


class CreateSessionCommandTest(TestCase):
    """
    Test the create_session management command
    测试 create_session 管理命令
    """

    def test_create_session_for_existing_user(self):
        """
        Test that create_session creates a session for existing user
        测试 create_session 为已存在用户创建 session
        """
        # Create a user
        email = 'test@example.com'
        user = User.objects.create_user(email=email)

        # Call the command
        out = StringIO()
        call_command('create_session', email, stdout=out)

        # Check output
        output = out.getvalue()
        self.assertIn('Found existing user', output)
        self.assertIn('Session created successfully', output)
        self.assertIn(email, output)

        # Verify session was created
        session_key = output.split('Session key: ')[1].split('\n')[0]
        session = SessionStore(session_key=session_key)
        self.assertEqual(session['_auth_user_id'], str(user.id))

    def test_create_session_for_new_user(self):
        """
        Test that create_session creates user and session for new email
        测试 create_session 为新邮箱创建用户和 session
        """
        email = 'newuser@example.com'

        # Call the command
        out = StringIO()
        call_command('create_session', email, stdout=out)

        # Check output
        output = out.getvalue()
        self.assertIn('Created new user', output)
        self.assertIn('Session created successfully', output)

        # Verify user was created
        user = User.objects.get(email=email)
        self.assertIsNotNone(user)

    def test_create_session_validates_session_data(self):
        """
        Test that created session has valid authentication data
        测试创建的 session 包含有效的认证数据
        """
        email = 'edith@example.com'
        user = User.objects.create_user(email=email)

        # Call the command
        out = StringIO()
        call_command('create_session', email, stdout=out)

        # Extract session key from output
        output = out.getvalue()
        session_key = output.split('Session key: ')[1].split('\n')[0]

        # Load session and verify data
        session = SessionStore(session_key=session_key)

        # Check all required auth keys are present
        self.assertEqual(session['_auth_user_id'], str(user.id))
        self.assertEqual(session['_auth_user_backend'], 'accounts.views.EmailBackend')
        self.assertEqual(session['_auth_user_hash'], str(user.get_session_auth_hash()))

    def test_create_session_outputs_user_info(self):
        """
        Test that create_session outputs user information
        测试 create_session 输出用户信息
        """
        email = 'info@test.com'
        user = User.objects.create_user(email=email)

        # Call the command
        out = StringIO()
        call_command('create_session', email, stdout=out)

        # Check output contains all expected info
        output = out.getvalue()
        self.assertIn('Session key:', output)
        self.assertIn('User ID:', output)
        self.assertIn(str(user.id), output)
        self.assertIn('Email:', output)
        self.assertIn(email, output)
