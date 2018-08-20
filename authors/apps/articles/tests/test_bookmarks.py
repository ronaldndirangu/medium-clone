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


class TestBookmarks(TestCase):
    """
    This class defines the test suite for the bookmarking articles.
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

    def test_bookmark_article(self):
        """Test a user bookmark an article"""
        token = self.login_verified_user(self.user_data)

        self.create_article(token, self.article_data)
        response = self.client.post(
            '/api/articles/django/bookmark/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        self.assertEquals(response.status_code,
                          status.HTTP_201_CREATED)

    def test_remove_missing_bookmark(self):
        """Test a user can not remove a non existing bookmarked article"""
        token = self.login_verified_user(self.user_data)

        self.create_article(token, self.article_data)
        response = self.client.delete(
            '/api/articles/django/bookmark/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        self.assertEquals(response.status_code,
                          status.HTTP_404_NOT_FOUND)

    def test_remove_bookmarked_article(self):
        """Test a user can remove from bookmark"""
        token = self.login_verified_user(self.user_data)

        self.create_article(token, self.article_data)
        # add article to bookmarks
        self.client.post(
            '/api/articles/django/bookmark/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        response = self.client.delete(
            '/api/articles/django/bookmark/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK)

    def test_bookmark_invalid_slug(self):
        """Test a user can not bookmark an invalid slug"""
        token = self.login_verified_user(self.user_data)

        self.create_article(token, self.article_data)
        response = self.client.delete(
            '/api/articles/wrong-slug/bookmark/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        self.assertIn("An article with this slug does not exist",
                      response.content.decode())
        self.assertEquals(response.status_code,
                          status.HTTP_404_NOT_FOUND)
