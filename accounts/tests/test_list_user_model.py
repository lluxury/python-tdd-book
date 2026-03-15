"""
Tests for ListUser model
"""
from django.test import TestCase
from accounts.models import ListUser


class ListUserModelTest(TestCase):
    """
    Test the ListUser model only stores email
    """

    def test_user_model_only_has_email(self):
        """
        Test that ListUser model only stores email, not first name or last name
        """
        # Arrange & Act
        user = ListUser.objects.create_user(email='test@example.com')

        # Assert
        self.assertEqual(user.email, 'test@example.com')
        # Verify that first_name and last_name are not used
        if hasattr(user, 'first_name'):
            self.assertEqual(user.first_name, '')
        if hasattr(user, 'last_name'):
            self.assertEqual(user.last_name, '')

    def test_user_email_is_unique(self):
        """
        Test that email field is unique
        """
        # Arrange
        ListUser.objects.create_user(email='test@example.com')

        # Act & Assert
        with self.assertRaises(Exception):  # Django raises IntegrityError
            ListUser.objects.create_user(email='test@example.com')

    def test_user_has_is_authenticated_property(self):
        """
        Test that user has is_authenticated property and it returns True
        """
        # Arrange & Act
        user = ListUser.objects.create_user(email='test@example.com')

        # Assert
        self.assertTrue(user.is_authenticated)
