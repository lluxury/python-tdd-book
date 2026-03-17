"""
Tests for Gunicorn configuration
测试 Gunicorn 配置
"""
import os
import sys
from pathlib import Path


class GunicornConfigTest:
    """
    Test that Gunicorn configuration file exists and has correct settings
    测试 Gunicorn 配置文件存在且设置正确
    """

    def test_gunicorn_config_exists(self):
        """
        Test that gunicorn.conf.py file exists
        测试 gunicorn.conf.py 文件存在
        """
        # Add superlists to path
        superlists_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(superlists_dir))

        config_path = superlists_dir / 'gunicorn.conf.py'

        # File should exist
        self.assertion(config_path.exists(),
                      f"Gunicorn config file should exist at {config_path}")

    def test_gunicorn_config_has_access_log(self):
        """
        Test that Gunicorn config has access log configured
        测试 Gunicorn 配置包含访问日志
        """
        superlists_dir = Path(__file__).parent.parent
        config_path = superlists_dir / 'gunicorn.conf.py'

        with open(config_path, 'r') as f:
            content = f.read()

        # Should have accesslog configured
        self.assertion('accesslog' in content,
                      "Gunicorn config should have accesslog setting")

    def test_gunicorn_config_has_error_log(self):
        """
        Test that Gunicorn config has error log configured
        测试 Gunicorn 配置包含错误日志
        """
        superlists_dir = Path(__file__).parent.parent
        config_path = superlists_dir / 'gunicorn.conf.py'

        with open(config_path, 'r') as f:
            content = f.read()

        # Should have errorlog configured
        self.assertion('errorlog' in content,
                      "Gunicorn config should have errorlog setting")

    def test_gunicorn_config_has_workers(self):
        """
        Test that Gunicorn config has workers configured
        测试 Gunicorn 配置包含 workers 设置
        """
        superlists_dir = Path(__file__).parent.parent
        config_path = superlists_dir / 'gunicorn.conf.py'

        with open(config_path, 'r') as f:
            content = f.read()

        # Should have workers configured
        self.assertion('workers' in content,
                      "Gunicorn config should have workers setting")

    def test_gunicorn_config_has_bind(self):
        """
        Test that Gunicorn config has bind address configured
        测试 Gunicorn 配置包含绑定地址
        """
        superlists_dir = Path(__file__).parent.parent
        config_path = superlists_dir / 'gunicorn.conf.py'

        with open(config_path, 'r') as f:
            content = f.read()

        # Should have bind configured
        self.assertion('bind' in content,
                      "Gunicorn config should have bind setting")

    def assertion(self, condition, message):
        """Helper method for assertions"""
        if not condition:
            raise AssertionError(f"Assertion failed: {message}")
        print(f"[OK] {message}")

    @staticmethod
    def run_all_tests():
        """Run all tests"""
        test = GunicornConfigTest()

        print("Running Gunicorn configuration tests...")
        print("=" * 50)

        test.test_gunicorn_config_exists()
        test.test_gunicorn_config_has_access_log()
        test.test_gunicorn_config_has_error_log()
        test.test_gunicorn_config_has_workers()
        test.test_gunicorn_config_has_bind()

        print("=" * 50)
        print("All Gunicorn config tests passed!")


if __name__ == '__main__':
    GunicornConfigTest.run_all_tests()
