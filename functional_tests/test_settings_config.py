"""
Tests for Django settings configuration for functional tests
测试功能测试的 Django settings 配置
"""
import os
import sys
from pathlib import Path


class SettingsConfigTest:
    """
    Test that Django settings has proper functional test configuration
    测试 Django settings 有正确的功能测试配置
    """

    def test_test_runner_configured(self):
        """
        Test that TEST_RUNNER is configured
        测试 TEST_RUNNER 已配置
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        self.assertion(hasattr(settings, 'TEST_RUNNER'),
                      "Settings should have TEST_RUNNER configured")
        self.assertion(settings.TEST_RUNNER == 'django.test.runner.DiscoverRunner',
                      "TEST_RUNNER should be DiscoverRunner")

    def test_functional_tests_configured(self):
        """
        Test that FUNCTIONAL_TESTS setting exists
        测试 FUNCTIONAL_TESTS 设置存在
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        self.assertion(hasattr(settings, 'FUNCTIONAL_TESTS'),
                      "Settings should have FUNCTIONAL_TESTS configuration")

        functional_tests = settings.FUNCTIONAL_TESTS
        self.assertion('DEFAULT_TIMEOUT' in functional_tests,
                      "FUNCTIONAL_TESTS should have DEFAULT_TIMEOUT")
        self.assertion('SELENIUM_DRIVER' in functional_tests,
                      "FUNCTIONAL_TESTS should have SELENIUM_DRIVER")

    def test_staging_server_configured(self):
        """
        Test that STAGING_SERVER setting exists
        测试 STAGING_SERVER 设置存在
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        self.assertion(hasattr(settings, 'STAGING_SERVER'),
                      "Settings should have STAGING_SERVER configuration")

        # Default should be localhost
        self.assertion(settings.STAGING_SERVER is not None,
                      "STAGING_SERVER should not be None")

    def test_logging_configured(self):
        """
        Test that LOGGING is configured
        测试 LOGGING 已配置
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        self.assertion(hasattr(settings, 'LOGGING'),
                      "Settings should have LOGGING configuration")

        logging_config = settings.LOGGING
        self.assertion('loggers' in logging_config,
                      "LOGGING should have loggers")
        self.assertion('accounts' in logging_config['loggers'],
                      "LOGGING should have accounts logger")

    def test_database_test_configured(self):
        """
        Test that database has TEST configuration
        测试数据库有 TEST 配置
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        databases = settings.DATABASES
        self.assertion('default' in databases,
                      "Should have default database")

        default_db = databases['default']
        self.assertion('TEST' in default_db,
                      "Default database should have TEST configuration")

    def assertion(self, condition, message):
        """Helper method for assertions"""
        if not condition:
            raise AssertionError(f"Assertion failed: {message}")
        print(f"[OK] {message}")

    @staticmethod
    def run_all_tests():
        """Run all tests"""
        test = SettingsConfigTest()

        print("Running Django settings configuration tests...")
        print("=" * 50)

        test.test_test_runner_configured()
        test.test_functional_tests_configured()
        test.test_staging_server_configured()
        test.test_logging_configured()
        test.test_database_test_configured()

        print("=" * 50)
        print("All settings config tests passed!")


if __name__ == '__main__':
    SettingsConfigTest.run_all_tests()
