import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from authors.apps.authentication.views import Activate


class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""

        """User data for getting token"""
        self.test_user = {
            "user": {
                "username": "janey",
                "email": "janet.wairimu@andela.com",
                "password": "SecretSecret254"
            }
        }
        self.test_user2 = {
            "user": {
                "username": "james",
                "email": "james.wairimu@andela.com",
                "password": "SecretSecret254"
            }
        }

        """Articles data for testing rate feature"""
        self.article = {
            "article": {
                "title": "lolitas",
                "body": "lolitas",
                "description": "lolitas quantum physics",
            }
        }
        """Correct rate data passing all validations"""
        self.rate = {
            "rate": {
                "rating": 3
            }
        }
        """Rate data that is beyond the range 1 - 5"""
        self.rate_beyond_range = {
            "rate": {
                "rating": 6
            }
        }
        """Rate data that is not numeric"""
        self.string_rate = {
            "rate": {
                "rating": "d"
            }
        }
        """An empty value for rate"""
        self.empty_rate = {
            "rate": {
                "rating": " "
            }
        }

        """Initialize client"""
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def create_user_unverified(self):
        """
        Creates a user without verifying them
        """
        self.client.post(
            '/api/users/',
            self.test_user,
            format='json'
        )

    def login_unverified_user(self):
        """
        Logs in and unverified user
        """
        response = self.client.post(
            '/api/users/login/',
            self.test_user,
            format='json'
        )
        json_response = json.loads(response.content)
        return json_response.get('user').get('token')

    def create_and_verify_user(self, test_user):
        """
        Check user has verified account from email
        """
        user_obj = User.objects.create_user(username=test_user.get('user').get(
            'username'), email=test_user.get('user').get('email'), password=test_user.get('user').get('password'))
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(user_obj.email, request)
        request = self.factory.get(
            reverse("authentication:activate", args=[uid, token]))
        force_authenticate(request, user_obj, token=user_obj.token)
        view = Activate.as_view()
        view(request, uidb64=uid, token=token)
        user = User.objects.last()
        return user.is_verified

    def login_verified_user(self, test_user):
        """
        Logs in created and verified user to get token
        """
        if self.create_and_verify_user(test_user) is True:
            response = self.client.post(
                '/api/users/login/',
                test_user,
                format='json'
            )
        json_response = json.loads(response.content)
        return json_response.get('user').get('token')

    def create_article(self, token, article):
        """
        Creates an article for testing
        """

        token = self.login_verified_user(self.test_user)

        return self.client.post(
            '/api/articles/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def test_rating_inexisting_article(self):
        """Test user rating an inexisting article"""

        token = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response = self.client.post('/api/articles/lola/rate/',
                                    self.rate,
                                    HTTP_AUTHORIZATION='Token ' + token,
                                    format='json'
                                    )
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("An article with this slug does not exist",
                      response.content.decode())

    def test_empty_rating(self):
        """Test user tries to give an empty rating"""

        token = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response = self.client.post(
            '/api/articles/lolitas/rate/',
            self.empty_rate,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertIn("A valid integer is required.",
                      response.content.decode())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_not_an_integer(self):
        """Test user cannot give an alphabetic input as rate"""

        token = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response = self.client.post(
            '/api/articles/lolitas/rate/',
            self.string_rate,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertIn("A valid integer is required.",
                      response.content.decode())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_beyond_range(self):
        """Test user cannot give a rate beyond the range of 1-5"""

        token = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response = self.client.post(
            '/api/articles/lolitas/rate/',
            self.rate_beyond_range,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertIn("Rate must be a value between 1 and 5",
                      response.content.decode())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_rate(self):
        """Test user can rate an aticle successfully"""

        token = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response = self.client.post(
            '/api/articles/lolitas/rate/',
            self.rate,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
