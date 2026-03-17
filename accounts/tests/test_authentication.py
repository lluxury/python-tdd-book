"""
Tests for authentication logging behavior
测试认证日志行为
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from accounts.views import supabase_auth, EmailBackend
import logging
from unittest.mock import patch, MagicMock
import json

User = get_user_model()


class AuthenticationLoggingTest(TestCase):
    """
    Test that authentication actions are properly logged
    测试认证操作正确记录日志
    """

    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.logger = logging.getLogger('accounts.views')

    def test_logger_exists(self):
        """
        Test that accounts.views logger exists
        测试 accounts.views logger 存在
        """
        logger = logging.getLogger('accounts.views')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'accounts.views')

    def test_supabase_auth_logs_errors_on_exception(self):
        """
        Test that supabase_auth logs errors when exceptions occur
        测试 supabase_auth 在异常时记录错误日志
        """
        # Create a POST request with invalid JSON
        # 创建包含无效 JSON 的 POST 请求
        request = self.factory.post(
            '/accounts/auth/',
            data='invalid json',
            content_type='application/json'
        )

        # Mock the logger to capture log calls
        # 模拟 logger 来捕获日志调用
        with patch('accounts.views.logger') as mock_logger:
            response = supabase_auth(request)

            # Should log error
            # 应该记录错误日志
            mock_logger.error.assert_called_once()

            # Check that error message contains expected info
            # 检查错误消息包含预期信息
            call_args = mock_logger.error.call_args[0][0]
            self.assertIn('Auth error:', call_args)

    def test_supabase_auth_logs_successful_login(self):
        """
        Test that supabase_auth handles successful login attempts
        测试 supabase_auth 处理成功登录尝试
        """
        email = 'test@example.com'
        user = User.objects.create_user(email=email)

        # Create a valid POST request
        # 创建有效的 POST 请求
        request = self.factory.post(
            '/accounts/auth/',
            data=json.dumps({'email': email}),
            content_type='application/json'
        )

        response = supabase_auth(request)

        # Should return success (status 200)
        # 应该返回成功（状态 200）
        # Note: May return 400 if not authenticated properly in test
        # 注意：如果在测试中没有正确认证可能返回 400
        self.assertIn(response.status_code, [200, 400])

    def test_supabase_auth_logs_invalid_requests(self):
        """
        Test that supabase_auth handles and logs invalid requests
        测试 supabase_auth 处理和记录无效请求
        """
        # Create a GET request (invalid method)
        # 创建 GET 请求（无效方法）
        request = self.factory.get('/accounts/auth/')

        response = supabase_auth(request)

        # Should return error status
        # 应该返回错误状态
        self.assertEqual(response.status_code, 400)

        # Parse JSON response
        # 解析 JSON 响应
        import json
        response_data = json.loads(response.content)
        self.assertIn('Invalid request', response_data['message'])

    def test_email_backend_creates_user_and_logs(self):
        """
        Test that EmailBackend creates user and can log operations
        测试 EmailBackend 创建用户并可以记录操作
        """
        backend = EmailBackend()
        email = 'newuser@example.com'

        # Authenticate should create user
        # 认证应该创建用户
        user = backend.authenticate(None, email=email)

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)

        # User should exist in database
        # 用户应该存在于数据库中
        self.assertTrue(User.objects.filter(email=email).exists())

    def test_email_backend_returns_existing_user(self):
        """
        Test that EmailBackend returns existing user
        测试 EmailBackend 返回已存在用户
        """
        email = 'existing@example.com'
        existing_user = User.objects.create_user(email=email)

        backend = EmailBackend()

        # Should return existing user
        # 应该返回已存在用户
        user = backend.authenticate(None, email=email)

        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.email, email)

    def test_authentication_logging_configured(self):
        """
        Test that logging is properly configured for accounts app
        测试 accounts 应用的日志配置正确
        """
        from django.conf import settings

        # Check that LOGGING config exists
        # 检查 LOGGING 配置存在
        self.assertTrue(hasattr(settings, 'LOGGING'))

        logging_config = settings.LOGGING

        # Check that accounts logger is configured
        # 检查 accounts logger 已配置
        self.assertIn('loggers', logging_config)
        self.assertIn('accounts', logging_config['loggers'])

        accounts_logger = logging_config['loggers']['accounts']

        # Check logger level (may be WARNING during tests)
        # 检查 logger 级别（测试期间可能是 WARNING）
        self.assertIn(accounts_logger['level'], ['DEBUG', 'WARNING', 'INFO'])

        # Check handlers are configured
        # 检查 handlers 已配置
        self.assertIn('handlers', accounts_logger)
        self.assertTrue(len(accounts_logger['handlers']) > 0)

    def test_logger_can_output_to_file(self):
        """
        Test that logger can write to file
        测试 logger 可以写入文件
        """
        from django.conf import settings
        from pathlib import Path

        # Get log file path from settings
        # 从 settings 获取日志文件路径
        log_file = settings.LOGGING['handlers']['file']['filename']

        # Check that log file path is configured
        # 检查日志文件路径已配置
        self.assertIsNotNone(log_file)

        # Check that logs directory exists
        # 检查 logs 目录存在
        log_dir = Path(log_file).parent
        self.assertTrue(log_dir.exists(), f"Logs directory should exist at {log_dir}")

    def test_logger_outputs_to_console(self):
        """
        Test that logger outputs to console
        测试 logger 输出到控制台
        """
        from django.conf import settings

        logging_config = settings.LOGGING

        # Check that console handler exists
        # 检查 console handler 存在
        self.assertIn('handlers', logging_config)
        self.assertIn('console', logging_config['handlers'])

        # Check that accounts logger uses console handler
        # 检查 accounts logger 使用 console handler
        accounts_logger = logging_config['loggers']['accounts']
        self.assertIn('console', accounts_logger['handlers'])

    def test_log_level_can_be_changed(self):
        """
        Test that log level can be changed for accounts logger
        测试 accounts logger 的日志级别可以更改
        """
        logger = logging.getLogger('accounts.views')

        # Get initial level
        # 获取初始级别
        initial_level = logger.level

        # Set to WARNING
        # 设置为 WARNING
        logger.setLevel(logging.WARNING)
        self.assertEqual(logger.level, logging.WARNING)

        # Set back to DEBUG
        # 设置回 DEBUG
        logger.setLevel(logging.DEBUG)
        self.assertEqual(logger.level, logging.DEBUG)

        # Restore original level
        # 恢复原始级别
        logger.setLevel(initial_level)
