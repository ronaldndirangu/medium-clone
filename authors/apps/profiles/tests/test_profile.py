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


def update_user_profile(username=None, email=None,
        bio=None, interests=None, image=None):

    """Updating user profile"""


class ProfileTestcase(TestCase):
    """Test suite for the user profile."""
    
    def setUp(self):
        """Define the test client and other test variables."""

        # Initialize client
        self.client = APIClient()

        self.profile_data = {
            "bio": "Full stack Dev at nerd-tech",
            "interests": "Technology, Nature",
            "image": "https://my-image-url/no-image.jpg"
        }

    def test_profile_retrieve(self):
        """Test api can retrieve a user profile"""
        
        create_a_user()

        response = self.client.get(
            '/api/profiles/nerd/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_update_without_authentication(self):
        """Test api cannot update a user profile without authentication"""

        create_a_user()

        response = self.client.put(
            '/api/user/',
            self.profile_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
