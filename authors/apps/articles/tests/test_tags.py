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

class TestTags(TestCase):
    """
    This class defines the test suite for the tags of an article.
    """

    def setUp(self):
        """Define the test client and other test variables."""

        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.article_data = {
            "article": {
                "title": "Django is life",
                "description": "Django",
                "body": "You have to believe",
                "tagList": ["Django-rest", "Django-taggit"]
            }
        }
        self.bad_tag_list = {
            "article": {
                "title": "Django is life",
                "description": "Django",
                "body": "You have to believe",
                "tagList": "Django-rest, Django-taggit"
            }
        }
        self.tag_tuple = {
            "article": {
                "title": "Django is life",
                "description": "Django",
                "body": "You have to believe",
                "tagList": ("Django-rest, Django-taggit")
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
    
    def test_tagList_added(self):
        """Test a tagList is added when an article is created"""

        response = response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)
        self.assertIn("Django-rest", response.content.decode()),
        self.assertIn("Django-taggit", response.content.decode())
    
    def test_tagList_returned(self):
        """Test api can return a taglist with an article"""

        response = response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)
        response = self.client.get(
            '/api/articles/'
        )
        self.assertIn("Django-rest", response.content.decode()),
        self.assertIn("Django-taggit", response.content.decode())

    def test_get_tagList(self):
        """ Test api can get a tagList"""

        response = response = self.create_article(
            self.login_verified_user(self.user_data), self.article_data)
        response = self.client.get(
            '/api/tags/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tagList_object(self):
        """Test a tagList cannot be a string"""

        response = response = self.create_article(
            self.login_verified_user(self.user_data), self.bad_tag_list)
        self.assertNotIn("Django-rest", response.content.decode()),
        self.assertNotIn("Django-taggit", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_tagList_data_structure(self):
        """Test a tagList cannot be a tuple"""

        response = response = self.create_article(
            self.login_verified_user(self.user_data), self.tag_tuple)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
