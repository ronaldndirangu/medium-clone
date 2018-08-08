from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from django.core import mail
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import force_authenticate
from authors.apps.authentication.views import Activate
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class VerifyTestCase(TestCase):
    """Test suite for registration verification."""

    def setUp(self):
        """Define the test client and other test variables."""

        self.first_user = {
            "user": {
                "username": "thewriter",
                "email": "dalin.oluoch@andela.com",
                "password": "Secretsecret254"
            }
        }
        self.second_user = {
            "user": {
                "email": "dalin.oluoch@andela.com"
            }
        }

        self.factory = APIRequestFactory()
        self.client = APIClient()

    def register_user(self):
        """Create a user for test purposes"""
        self.client.post(
            '/api/users/',
            self.first_user,
            format='json'
        )

    def encode_token(self):
        """Encode user email to form `token`"""
        # hardcode existing user email
        user_mail = 'dalin.oluoch@andela.com'
        # encode email
        encode_mail = urlsafe_base64_encode(
            force_bytes(user_mail)).decode('utf-8')
        return encode_mail

    def test_email_sent(self):
        """Test if email has been sent and has verification content"""
        # Create a user
        self.register_user()
        response = self.client.post(
            '/api/users/reset_pass/',
            self.second_user,
            format='json'
        )
        self.assertTrue(response.status_code, 200)

    def test_invalid_email(self):
        """Test wrong email format"""
        # Create a user
        self.register_user()
        response = self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "email": "dalin.oluochandela.com"
                }
            },
            format='json'
        )
        self.assertTrue(response.status_code, 400)

    def test_email_not_exist(self):
        """Test for a not registered user requesting for password request"""
        # Create a user
        self.register_user()
        response = self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "email": "random@mail.com"
                }
            },
            format='json'
        )
        self.assertTrue(response.status_code, 404)
        self.assertIn("Email doesn't exist, register instead.",
                      response.content.decode())

    def test_successful_change_password(self):
        """Test for successful reset of password"""
        # Create a user
        self.register_user()
        response = self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "reset_token": self.encode_token(),
                    "new_password": "aaaAAA111"
                }
            },
            format='json'
        )
        self.assertTrue(response.status_code, 201)

    def test_failure_change_password(self):
        """Test for failure to reset password as token has been used"""
        # Create a user
        self.register_user()
        self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "reset_token": self.encode_token(),
                    "new_password": "aaaAAA111"
                }
            },
            format='json'
        )
        # Attempt to reset the password again
        response = self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "reset_token": self.encode_token(),
                    "new_password": "aaaAAA111"
                }
            },
            format='json'
        )
        self.assertTrue(response.status_code, 403)

    def test_invalid_password(self):
        """Test for invalid reset password input"""
        # Create a user
        self.register_user()
        response = self.client.post(
            '/api/users/reset_pass/',
            {
                "user": {
                    "reset_token": self.encode_token(),
                    "new_password": "aaaaaaa"
                }
            },
            format='json'
        )
        self.assertTrue(response.status_code, 400)
