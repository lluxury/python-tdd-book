"""
Remote server helper script for functional tests
功能测试的远端服务器辅助脚本

This script provides helper functions to manage remote server sessions
and database for functional testing.

使用方法:
    from scripts.remote_helper import RemoteServerHelper

    helper = RemoteServerHelper('staging.example.com')

    # Create session
    session_key = helper.create_session('user@example.com')

    # Get database path
    db_path = helper.get_db_path()

    # Reset database after tests
    helper.reset_database()
"""
import subprocess
import os
from pathlib import Path


class RemoteServerHelper:
    """
    Helper class to manage remote server operations for functional testing
    辅助类来管理功能测试的远端服务器操作
    """

    def __init__(self, server, ssh_user='root', remote_path='/var/www/superlists',
                 venv_path='/var/www/superlists/venv'):
        """
        Initialize remote server helper

        Args:
            server: Remote server address
            ssh_user: SSH user for connection
            remote_path: Remote project path
            venv_path: Remote virtual environment path
        """
        self.server = server
        self.ssh_user = ssh_user
        self.remote_path = remote_path
        self.venv_path = venv_path

    def _run_ssh_command(self, command, timeout=30):
        """
        Run command on remote server via SSH

        Args:
            command: Command to run
            timeout: Command timeout in seconds

        Returns:
            tuple: (returncode, stdout, stderr)
        """
        full_command = f'ssh {self.ssh_user}@{self.server} "{command}"'

        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except subprocess.TimeoutExpired:
            return -1, '', 'Command timed out'

    def create_session(self, email):
        """
        Create session for user on remote server

        Args:
            email: User email address

        Returns:
            str: Session key if successful, None otherwise
        """
        command = f'cd {self.remote_path} && {self.venv_path}/bin/python manage.py create_session {email}'

        returncode, stdout, stderr = self._run_ssh_command(command, timeout=30)

        if returncode == 0:
            # Extract session key from output
            for line in stdout.split('\n'):
                if 'Session key:' in line:
                    session_key = line.split('Session key: ')[1].strip()
                    return session_key
            return None
        else:
            print(f"Error creating session: {stderr}")
            return None

    def get_db_path(self):
        """
        Get remote database path

        Returns:
            str: Database path if exists, None otherwise
        """
        command = f'test -f {self.remote_path}/db.sqlite3 && echo {self.remote_path}/db.sqlite3'

        returncode, stdout, stderr = self._run_ssh_command(command, timeout=10)

        if returncode == 0:
            return stdout.strip()
        else:
            print(f"Database not found at {self.remote_path}/db.sqlite3")
            return None

    def get_manage_path(self):
        """
        Get manage.py path on remote server

        Returns:
            str: manage.py path if exists, None otherwise
        """
        command = f'test -f {self.remote_path}/manage.py && echo {self.remote_path}/manage.py'

        returncode, stdout, stderr = self._run_ssh_command(command, timeout=10)

        if returncode == 0:
            return stdout.strip()
        else:
            print(f"manage.py not found at {self.remote_path}/manage.py")
            return None

    def backup_database(self):
        """
        Backup remote database before tests

        Returns:
            str: Backup file path if successful, None otherwise
        """
        timestamp = subprocess.check_output('date +%Y%m%d_%H%M%S', shell=True).decode().strip()
        backup_path = f'{self.remote_path}/db.backup.{timestamp}.sqlite3'

        command = f'cp {self.remote_path}/db.sqlite3 {backup_path}'

        returncode, stdout, stderr = self._run_ssh_command(command, timeout=30)

        if returncode == 0:
            return backup_path
        else:
            print(f"Error backing up database: {stderr}")
            return None

    def reset_database(self):
        """
        Reset remote database after tests

        Returns:
            bool: True if successful, False otherwise
        """
        commands = [
            f'cd {self.remote_path} && {self.venv_path}/bin/python manage.py flush --noinput',
            f'cd {self.remote_path} && {self.venv_path}/bin/python manage.py migrate',
        ]

        for cmd in commands:
            returncode, stdout, stderr = self._run_ssh_command(cmd, timeout=60)
            if returncode != 0:
                print(f"Error resetting database: {stderr}")
                return False

        return True

    def restore_database(self, backup_path):
        """
        Restore database from backup

        Args:
            backup_path: Path to backup file

        Returns:
            bool: True if successful, False otherwise
        """
        command = f'cp {backup_path} {self.remote_path}/db.sqlite3'

        returncode, stdout, stderr = self._run_ssh_command(command, timeout=30)

        if returncode == 0:
            return True
        else:
            print(f"Error restoring database: {stderr}")
            return False


# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python remote_helper.py <server_address> [ssh_user] [remote_path] [venv_path]")
        sys.exit(1)

    server = sys.argv[1]
    ssh_user = sys.argv[2] if len(sys.argv) > 2 else 'root'
    remote_path = sys.argv[3] if len(sys.argv) > 3 else '/var/www/superlists'
    venv_path = sys.argv[4] if len(sys.argv) > 4 else '/var/www/superlists/venv'

    helper = RemoteServerHelper(server, ssh_user, remote_path, venv_path)

    print(f"Testing connection to {server}...")

    # Test connection by getting manage.py path
    manage_path = helper.get_manage_path()
    if manage_path:
        print(f"✓ Connected successfully")
        print(f"  manage.py: {manage_path}")

        # Get database path
        db_path = helper.get_db_path()
        if db_path:
            print(f"  Database: {db_path}")
    else:
        print("✗ Failed to connect")
        sys.exit(1)
