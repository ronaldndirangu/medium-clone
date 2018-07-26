from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json

from ..apps.authentication.models import User

class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        
        self.user_data = {
            "user":{
                "username": "patrick",
                "email": "boss@gmail.com",
                "password": "qwert@123"
                }
            }
        self.missing_username = {
            "user":{
                "username": "",
                "email": "boss@gmail.com",
                "password": "qwert@123"
                }
            }
        self.missing_email = {
            "user":{
                "username": "patrick",
                "email": "",
                "password": "qwert@123"
                }
            }
        self.missing_password = {
            "user":{
                "username": "patrick",
                "email": "boss@gmail.com",
                "password": ""
                }
            }

        self.login_data = {
            "user":{
                "email": "boss@gmail.com",
                "password": "qwert@123"
                }
            }
        self.login_without_data = {
            "user":{
                "email": "",
                "password": ""
                }
            }
 
        # Initialize client
        self.client = APIClient()


    def test_user_can_signup(self):
        """Test user can signup to get access token"""
        response = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )
        self.assertIn("token",response.content.decode())

    def test_user_cannot_get_tokens_without_username(self):
        """Test user cannot get tokens due to missing data"""
        response = self.client.post(
            '/api/users/',
            self.missing_username,
            format='json'
        )
        self.assertIn("This field may not be blank.",response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)  

    def test_user_cannot_get_tokens_without_email(self):
        """Test user cannot get tokens due to missing data"""
        response = self.client.post(
            '/api/users/',
            self.missing_email,
            format='json'
        )
        self.assertIn("This field may not be blank.",response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)  

    def test_user_cannot_get_tokens_without_password(self):
        """Test user cannot get tokens due to missing data"""
        response = self.client.post(
            '/api/users/',
            self.missing_password,
            format='json'
        )
        self.assertIn("This field may not be blank.",response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST)  

    def test_user_login(self):
        """Test user can login to access tokens"""
        signup = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )

        response = self.client.post(
            '/api/users/login/',
            self.login_data,
            format='json'
        )
        self.assertIn("token",response.content.decode())

    def test_user_cannot_get_tokens(self):
        """Test user cannot get  tokens without data"""
        signup = self.client.post(
            '/api/users/',
            self.user_data,
            format='json'
        )

        response = self.client.post(
            '/api/users/login/',
            self.login_without_data ,
            format='json'
        )
        self.assertIn("This field may not be blank.",response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_400_BAD_REQUEST) 
