"""
Tests for Django logging configuration
测试 Django 日志配置
"""
import os
import sys
from pathlib import Path


class LoggingConfigTest:
    """
    Test that Django settings has proper logging configuration
    测试 Django settings 有正确的日志配置
    """

    def test_logging_config_exists(self):
        """
        Test that LOGGING config exists in settings.py
        测试 settings.py 中存在 LOGGING 配置
        """
        # Add superlists to path
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        # Should have LOGGING configured
        self.assertion(hasattr(settings, 'LOGGING'),
                      "Settings should have LOGGING configuration")

    def test_logging_config_has_handlers(self):
        """
        Test that LOGGING config has handlers
        测试 LOGGING 配置包含 handlers
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        logging_config = settings.LOGGING
        self.assertion('handlers' in logging_config,
                      "LOGGING config should have handlers")

    def test_logging_config_has_loggers(self):
        """
        Test that LOGGING config has loggers
        测试 LOGGING 配置包含 loggers
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        logging_config = settings.LOGGING
        self.assertion('loggers' in logging_config,
                      "LOGGING config should have loggers")

    def test_logging_config_has_accounts_logger(self):
        """
        Test that accounts app has logger configured
        测试 accounts 应用有配置的 logger
        """
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        from superlists import settings

        logging_config = settings.LOGGING
        loggers = logging_config.get('loggers', {})
        self.assertion('accounts' in loggers,
                      "LOGGING config should have accounts logger")

    def test_logs_directory_exists(self):
        """
        Test that logs directory exists or can be created
        测试 logs 目录存在或可以被创建
        """
        superlists_dir = Path(__file__).parent.parent
        logs_dir = superlists_dir / 'logs'

        # Create if doesn't exist
        if not logs_dir.exists():
            logs_dir.mkdir(exist_ok=True)

        self.assertion(logs_dir.exists(),
                      f"Logs directory should exist at {logs_dir}")

    def assertion(self, condition, message):
        """Helper method for assertions"""
        if not condition:
            raise AssertionError(f"Assertion failed: {message}")
        print(f"[OK] {message}")

    @staticmethod
    def run_all_tests():
        """Run all tests"""
        test = LoggingConfigTest()

        print("Running Django logging configuration tests...")
        print("=" * 50)

        test.test_logging_config_exists()
        test.test_logging_config_has_handlers()
        test.test_logging_config_has_loggers()
        test.test_logging_config_has_accounts_logger()
        test.test_logs_directory_exists()

        print("=" * 50)
        print("All logging config tests passed!")


if __name__ == '__main__':
    LoggingConfigTest.run_all_tests()
