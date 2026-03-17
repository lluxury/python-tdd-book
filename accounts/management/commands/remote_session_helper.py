"""
Django management command to manage remote server sessions
使用 subprocess 管理远端服务器 session 的 Django 管理命令

Usage:
    # Create session on remote server
    python manage.py remote_session_helper create_session user@example.com --server staging.example.com

    # Reset remote database
    python manage.py remote_session_helper reset_database --server staging.example.com

    # Get remote database path
    python manage.py remote_session_helper db_path --server staging.example.com
"""
import subprocess
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Manage remote server sessions using subprocess'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['create_session', 'reset_database', 'db_path', 'manage_path'],
            help='Action to perform: create_session, reset_database, db_path, or manage_path',
        )
        parser.add_argument(
            'email',
            type=str,
            nargs='?',
            help='Email address (required for create_session)',
        )
        parser.add_argument(
            '--server',
            type=str,
            default=None,
            help='Remote server address (default: from STAGING_SERVER env var or settings)',
        )
        parser.add_argument(
            '--ssh-user',
            type=str,
            default='root',
            help='SSH user for remote connection',
        )
        parser.add_argument(
            '--remote-path',
            type=str,
            default='/var/www/superlists',
            help='Remote project path',
        )
        parser.add_argument(
            '--venv-path',
            type=str,
            default='/var/www/superlists/venv',
            help='Remote virtual environment path',
        )

    def handle(self, *args, **options):
        action = options['action']
        server = options.get('server') or os.environ.get('STAGING_SERVER') or getattr(settings, 'STAGING_SERVER', 'localhost')

        if action == 'create_session':
            self.create_remote_session(options, server)
        elif action == 'reset_database':
            self.reset_remote_database(options, server)
        elif action == 'db_path':
            self.get_remote_db_path(options, server)
        elif action == 'manage_path':
            self.get_manage_path(options, server)

    def create_remote_session(self, options, server):
        """Create session on remote server"""
        email = options.get('email')
        if not email:
            self.stdout.write(self.style.ERROR('Email is required for create_session action'))
            return

        ssh_user = options['ssh_user']
        remote_path = options['remote_path']
        venv_path = options['venv_path']

        self.stdout.write(f'Creating session for {email} on {server}...')

        # SSH command to create session on remote server
        # SSH 命令在远端服务器上创建 session
        cmd = [
            'ssh',
            f'{ssh_user}@{server}',
            f'cd {remote_path} && {venv_path}/bin/python manage.py create_session {email}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            self.stdout.write(self.style.SUCCESS('Session created successfully on remote server'))
            self.stdout.write(result.stdout)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Failed to create session: {e.stderr}'))
        except subprocess.TimeoutExpired:
            self.stdout.write(self.style.ERROR('Command timed out'))

    def reset_remote_database(self, options, server):
        """Reset remote database"""
        ssh_user = options['ssh_user']
        remote_path = options['remote_path']
        venv_path = options['venv_path']

        self.stdout.write(f'Resetting database on {server}...')

        # SSH command to reset database on remote server
        # SSH 命令在远端服务器上重置数据库
        commands = [
            # Backup current database
            f'cp {remote_path}/db.sqlite3 {remote_path}/db.backup.$(date +%Y%m%d_%H%M%S).sqlite3',
            # Drop all tables
            f'cd {remote_path} && {venv_path}/bin/python manage.py flush --noinput',
            # Run migrations
            f'cd {remote_path} && {venv_path}/bin/python manage.py migrate',
        ]

        cmd = ['ssh', f'{ssh_user}@{server}', '; '.join(commands)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
            self.stdout.write(self.style.SUCCESS('Database reset successfully on remote server'))
            self.stdout.write(result.stdout)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Failed to reset database: {e.stderr}'))
        except subprocess.TimeoutExpired:
            self.stdout.write(self.style.ERROR('Command timed out'))

    def get_remote_db_path(self, options, server):
        """Get remote database path"""
        ssh_user = options['ssh_user']
        remote_path = options['remote_path']

        self.stdout.write(f'Getting database path from {server}...')

        # SSH command to get database path
        # SSH 命令获取数据库路径
        cmd = [
            'ssh',
            f'{ssh_user}@{server}',
            f'test -f {remote_path}/db.sqlite3 && echo {remote_path}/db.sqlite3 || echo "Database file not found"'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            db_path = result.stdout.strip()
            self.stdout.write(self.style.SUCCESS(f'Remote database path: {db_path}'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Failed to get database path: {e.stderr}'))

    def get_manage_path(self, options, server):
        """Get manage.py path"""
        ssh_user = options['ssh_user']
        remote_path = options['remote_path']

        self.stdout.write(f'Getting manage.py path from {server}...')

        # SSH command to get manage.py path
        # SSH 命令获取 manage.py 路径
        cmd = [
            'ssh',
            f'{ssh_user}@{server}',
            f'test -f {remote_path}/manage.py && echo {remote_path}/manage.py || echo "manage.py not found"'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            manage_path = result.stdout.strip()
            self.stdout.write(self.style.SUCCESS(f'Remote manage.py path: {manage_path}'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Failed to get manage.py path: {e.stderr}'))
