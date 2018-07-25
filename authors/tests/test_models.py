from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

#my local imports
from ..apps.authentication.models import User


def create_a_user(username="nerd", email="nerd@nerd.com", password="secret"):
    """Creating a test user"""
    user = User.objects.create_user(username, email, password)
    user.save()
    return user


class ModelTestCase(TestCase):
    """This class defines the test suite for the user model."""

    def test_model_can_create_a_user(self):
        """Test the user model can create a user."""

        response = create_a_user()
        self.assertTrue(isinstance(response, User))

    def test_model_returns_readable_representation(self):
        """Test a readable string is returned for the model instance."""

        response = create_a_user()
        self.assertEqual(str(response), "nerd@nerd.com")

    def test_create_superuser(self):
        """ Test that user model can create a super_user. """

        response = User.objects.create_superuser(
            username="supernerd",
            email="supernerd@nerd.com",
            password="secret"
        )

        self.assertTrue(response.is_superuser)

    def test_timestamp_added(self):
        """
        Test that user model adds a timestamp 
        on user creation. 
        """

        response = create_a_user()
        self.assertIsNotNone(response.created_at)

    def test_get_short_name(self):
        """
        Test that user model can return users short name. 
        """

        response = create_a_user()
        self.assertEqual(response.username, response.get_short_name())

    def test_get_full_name(self):
        """
        Test that user model can return users full name. 
        """

        response = create_a_user()
        self.assertEqual(response.username, response.get_full_name)
