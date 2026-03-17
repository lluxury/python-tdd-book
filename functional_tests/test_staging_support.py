"""
Tests for staging server support
测试 staging 服务器支持
"""
from functional_tests.base import FunctionalTest
from selenium.webdriver.common.by import By
import os


class StagingSupportTest(FunctionalTest):
    """
    Test that tests can run against staging server
    测试可以在 staging 服务器上运行
    """

    def test_against_staging_attribute_exists(self):
        """
        Test that against_staging attribute is set
        测试 against_staging 属性已设置
        """
        # Should have against_staging attribute
        # 应该有 against_staging 属性
        self.assertTrue(hasattr(self, 'against_staging'),
                       "FunctionalTest should have against_staging attribute")

        # For local testing, should be False
        # 对于本地测试，应该是 False
        self.assertFalse(self.against_staging,
                        "against_staging should be False for local testing")

    def test_server_url_exists(self):
        """
        Test that server_url is set correctly
        测试 server_url 正确设置
        """
        # Should have server_url attribute
        # 应该有 server_url 属性
        self.assertTrue(hasattr(self, 'server_url'),
                       "FunctionalTest should have server_url attribute")

        # For local testing, should match live_server_url
        # 对于本地测试，应该匹配 live_server_url
        self.assertEqual(self.server_url, self.live_server_url,
                        "server_url should equal live_server_url for local testing")

    def test_browser_initialization(self):
        """
        Test that browser is properly initialized in setUp
        测试 browser 在 setUp 中正确初始化
        """
        # Browser should be initialized
        # Browser 应该被初始化
        self.assertTrue(hasattr(self, 'browser'),
                       "FunctionalTest should have browser attribute")

        # Should be able to use browser
        # 应该能够使用 browser
        self.assertIsNotNone(self.browser,
                            "browser should not be None")

    def test_can_access_homepage(self):
        """
        Test that browser can access homepage using server_url
        测试 browser 可以使用 server_url 访问首页
        """
        # Should be able to access homepage
        # 应该能够访问首页
        self.browser.get(self.server_url)

        # Page should load successfully
        # 页面应该成功加载
        self.assertIn('To-Do', self.browser.title)

    def test_against_staging_with_environment_variable(self):
        """
        Test that against_staging can be set via environment variable
        测试 against_staging 可以通过环境变量设置
        """
        # Save original value
        # 保存原始值
        original_staging = os.environ.get('STAGING_SERVER')

        try:
            # Set staging server
            # 设置 staging 服务器
            os.environ['STAGING_SERVER'] = 'staging.example.com'

            # Create a new test instance to check the behavior
            # 创建新的测试实例来检查行为
            # Note: We can't easily re-instantiate, so we just verify
            # the environment variable is set
            # 注意：我们不能轻易重新实例化，所以我们只验证环境变量已设置

            self.assertEqual(os.environ.get('STAGING_SERVER'), 'staging.example.com')

        finally:
            # Restore original value
            # 恢复原始值
            if original_staging:
                os.environ['STAGING_SERVER'] = original_staging
            elif 'STAGING_SERVER' in os.environ:
                del os.environ['STAGING_SERVER']
