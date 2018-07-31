from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

#my local imports
from authors.apps.authentication.models import User
from ..models import Profile


def create_a_user(username="nerd", email="nerd@nerd.com", password="Secret123456"):
    """Creating a test user"""

    user = User.objects.create_user(username, email, password)
    user.save()
    return user


class ProfileModelTestCase(TestCase):
    """This class defines the test suite for the profile model."""

    def test_model_can_create_a_user_profile(self):
        """
        Test the profile model can create a user profile
        when a user signs up.
        """

        response = create_a_user()
        self.assertTrue(isinstance(response.profile, Profile))
    
    def test_model_returns_readable_representation(self):
        """
        Test a readable string is returned for the profile 
        model instance.
        """

        response = create_a_user()
        self.assertIn("nerd@nerd.com", str(response.profile))
    
    def test_timestamp_added(self):
        """
        Test that Profile model adds a timestamp 
        on profile creation. 
        """

        response = create_a_user()
        self.assertIsNotNone(response.profile.created_at)
