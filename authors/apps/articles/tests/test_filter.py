import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.authentication.verification import SendEmail
from authors.apps.authentication.views import Activate
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVector, TrigramSimilarity, TrigramDistance
)


class TestFilter(TestCase):
    """
    This class defines the test suite for the filtering articles.
    """

    def setUp(self):
        """Define the test client and other test variables."""

        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.article_data = {
            "article": {
                "title": "Django",
                "description": "Django",
                "body": "You have to believe",
                "tagList": ["trial", "life"]
            }
        }
        self.user_data = {
            "user": {
                "username": "Nerd",
                "email": "nerd@nerd.com",
                "password": "Secret123456"
            }
        }

    def create_and_verify_user(self, user_profile):
        """
        Verify user email
        """
        user_obj = User.objects.create_user(username=user_profile.get('user').get('username'),
                                            email=user_profile.get(
                                                'user').get('email'),
                                            password=user_profile.get('user').get('password'))
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(user_obj.email, request)
        request = self.factory.get(
            reverse("authentication:activate", args=[uid, token]))
        force_authenticate(request, user_obj, token=user_obj.token)
        view = Activate.as_view()
        view(request, uidb64=uid, token=token)
        user = User.objects.last()
        return user.is_verified

    def login_verified_user(self, user_profile):
        """
        Logs in created and verified user to get token
        :return token
        """
        if self.create_and_verify_user(user_profile) is True:
            response = self.client.post(
                '/api/users/login/',
                user_profile,
                format='json'
            )
            json_response = json.loads(response.content)
            return json_response.get('user').get('token')

    def create_article(self, token, article):
        """
        Creates an article
        """
        return self.client.post(
            '/api/articles/',
            article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
    
    def test_filter_by_title(self):
        """Test a user can filter articles by title"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)
        
        response = self.client.get(
            '/api/articles?title=Django'
        )
        self.assertIn("Django", response.content.decode())

    def test_filter_by_wrong_title(self):
        """Test a user cannot filter articles by wrong title"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)

        response = self.client.get(
            '/api/articles?title=Wrong'
        )
        self.assertNotIn("Django", response.content.decode())
    
    def test_filter_by_tags(self):
        """Test a user can filter articles by tags"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)

        response = self.client.get(
            '/api/articles?tags=trial'
        )
        self.assertIn("Django", response.content.decode())
        self.assertIn("trial", response.content.decode())

    def test_filter_by_wrong_tags(self):
        """Test a user cannot filter articles by wrong tags"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)

        response = self.client.get(
            '/api/articles?tag=Wrong'
        )
        self.assertNotIn("Django", response.content.decode())
        self.assertNotIn("trial", response.content.decode())
    
    def test_filter_by_author(self):
        """Test a user can filter articles by author"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)

        response = self.client.get(
            '/api/articles?author=Nerd'
        )
        self.assertIn("Django", response.content.decode())
        self.assertIn("Nerd", response.content.decode())

    def test_filter_by_wrong_author(self):
        """Test a user cannot filter articles by wrong author"""

        response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)

        response = self.client.get(
            '/api/articles?author=Wrong'
        )
        self.assertNotIn("Django", response.content.decode())
        self.assertNotIn("Nerd", response.content.decode())
