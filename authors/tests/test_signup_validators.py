from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


from ..apps.authentication.models import User


class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""

        """User data with password shorter than 8"""
        self.short_password = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "1234"
            }
        }

        """User data with no number in password"""
        self.number_password = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "abcdefgh"
            }
        }

        """User data with no small letter in password"""
        self.small_letter_password = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "1234ABCD"
            }
        }

        """User data with no capital letter in password"""
        self.capital_letter_password = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "1234abcd"
            }
        }

        """User data with invalid email"""
        self.invalid_password = {
            "user": {
                "username": "test",
                "email": "testgmail.com",
                "password": "1234abcD"
            }
        }

        """Valid user data"""
        self.user = self.user = User.objects.create(
            username="newtest", email="newtest@gmail.com")

        """Initialize client"""
        self.client = APIClient()

    def test_short_password(self):
        """Test user cannot signup using password less than 8 characters"""
        response = self.client.post(
            '/api/users/',
            self.short_password,
            format='json'
        )

        self.assertIn("Ensure this field has at least 8 characters.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)

    def test_for_small_letter(self):
        """Test user cannot signup if password lacks small letter"""
        response = self.client.post(
            '/api/users/',
            self.small_letter_password,
            format='json'
        )

        self.assertIn("A password must contain atleast one small letter and one capital letter.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)

    def test_for_capital_letter(self):
        """Test user cannot signup if password lacks capital letter"""
        response = self.client.post(
            '/api/users/',
            self.capital_letter_password,
            format='json'
        )

        self.assertIn("A password must contain atleast one small letter and one capital letter.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """Test user cannot signup with invalid email"""
        response = self.client.post(
            '/api/users/',
            self.invalid_password,
            format='json'
        )
        self.assertIn("Enter a valid email address.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)

    def test_email_exists(self):
        """Test user cannot register if email exists"""
        self.new_user = {
            "user": {
                "username": "test2",
                "email": "newtest@gmail.com",
                "password": "Test1234"
            }
        }

        response = self.client.post(
            '/api/users/',
            self.new_user,
            format='json'
        )

        self.assertIn("user with this email already exists.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)

    def test_user_exists(self):
        """Test user cannot register if username exists"""
        self.new_user = {
            "user": {
                "username": "newtest",
                "email": "test2@gmail.com",
                "password": "Test1234"
            }
        }

        response = self.client.post(
            '/api/users/',
            self.new_user,
            format='json'
        )

        self.assertIn("user with this username already exists.",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)
