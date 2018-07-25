from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from ..apps.authentication.models import User

class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        
        self.user_data = {
            "user":{
                "username": "nerd",
                "email": "nerd@nerd.com",
                "password": "secret123456"
                }
            }

        self.login_data = {
            "user":{
                "email": "nerd@nerd.com",
                "password": "secret123456"
                }
            }

        # Initialize client
        self.client = APIClient()

    def test_api_can_create_a_user(self):
        """Test the api can successfully create a user."""

        response = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_create_a_user_that_exists(self):
        """Test the api cannot create a user already exists."""

        response = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        response = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_create_a_user_without_username(self):
        """
        Test the api cannot create a user without 
        a password field.
        """

        user_data = {
            "user": {
                "email": "nerd@nerd.com",
                "password": "secret123456"
            }
        }
        response = self.client.post(
            '/api/users/',
            user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_create_a_user_without_email(self):
        """
        Test the api cannot create a user without 
        an email field.
        """

        user_data = {
            "user": {
                "username": "nerd",
                "password": "secret123456"
            }
        }
        response = self.client.post(
            '/api/users/',
            user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_can_login_a_user(self):
        """Test the api can successfuly login a user."""

        self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        response = self.client.post(
            '/api/users/login',
            self.login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_login_with_wrong_password(self):
        """Test the api cannot login a user with a wrong password."""

        login_data = {
            "user":{
                "email":"nerd@nerd.com",
                "password":"wrong123456"
            }
            }
        self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )   
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_login_with_wrong_email(self):
        """Test the api cannot login a user with a wrong email."""

        login_data = {
            "user":{
                "email":"wrong@nerd.com",
                "password":"secret123456"
            }
            }

        self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_login_with_short_password(self):
        """
        Test the api cannot login a user with a password
        of less than 8 characters.
        """

        login_data = {
            "user": {
                "email": "wrong@nerd.com",
                "password": "short"
            }
        }

        self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
