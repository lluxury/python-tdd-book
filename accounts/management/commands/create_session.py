"""
Django management command to create a session for a user
创建用户 session 的 Django 管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.backends.db import SessionStore
from accounts.models import ListUser


class Command(BaseCommand):
    help = 'Create a session for a user with given email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the user to create session for',
        )

    def handle(self, *args, **options):
        email = options['email']

        # Get or create user
        try:
            user = ListUser.objects.get(email=email)
            self.stdout.write(f'Found existing user: {email}')
        except ListUser.DoesNotExist:
            user = ListUser.objects.create_user(email=email)
            self.stdout.write(f'Created new user: {email}')

        # Create session
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'accounts.views.EmailBackend'
        session['_auth_user_hash'] = str(user.get_session_auth_hash())
        session.save()

        self.stdout.write(self.style.SUCCESS(
            f'Session created successfully!\n'
            f'Session key: {session.session_key}\n'
            f'User ID: {user.id}\n'
            f'Email: {email}'
        ))
