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
                "username": "manu100",
                "email": "emmanuelchepsire33@gmail.com",
                "password": "Manuchep23password"
            }
        }
        self.test_user2 = {
            "user": {
                "username": "manu150",
                "email": "emmanuelchepsire@andela.com",
                "password": "Manu150password"
            }
        }
        self.test_user3 = {
            "user": {
                "username": "manu200",
                "email": "emmanuel33@gmail.com",
                "password": "Manuchep23password"
            }
        }

        """Articles data for testing rate feature"""
        self.article = {
            "article": {
                "title": "getters",
                "body": "we are the people with a mission",
                "description": "Let not failure define you.",
            }

        }

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
        Logs in an unverified user
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
        
        return self.client.post(
            '/api/articles/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def test_favorite_article(self):
        """
        Test article can be favorited
        """
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data.get('favorites')
        self.assertEqual(True, response.data['favorited'])
        self.assertEqual(1, response.data['favoriteCount'])

    def test_unfavorite_article(self):
        """
        Test article can be unfavorited
        """
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data.get('favorites')
        self.assertEqual(True, response.data['favorited'])
        self.assertEqual(1, response.data['favoriteCount'])

        self.create_article(token, self.article)

        response =  self.client.delete(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK )

        data = response.data.get('favorites')
        self.assertEqual(False, response.data['favorited'])
        self.assertEqual(0, response.data['favoriteCount'])

    def test_favourite_count(self):
        
        """ 
        Test favourite count 
        """
        token = self.login_verified_user(self.test_user)
        token2 = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        response1 =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token2,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(True, response.data['favorited'])
        self.assertEqual(1, response.data['favoriteCount'])
        self.assertEqual(2, response1.data['favoriteCount'])

    def test_favourite_count_decrement(self):
        
        """ 
        Test favourite count can decrement after unfavoriting
        """
        token = self.login_verified_user(self.test_user)
        token2 = self.login_verified_user(self.test_user2)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        response1 =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token2,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(True, response.data['favorited'])
        self.assertEqual(1, response.data['favoriteCount'])
        self.assertEqual(2, response1.data['favoriteCount'])

        response1 =  self.client.delete(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token2,
            format='json'
        )
        self.assertEqual(1, response1.data['favoriteCount'])

    def test_can_favorite_once(self):
        """
        Test that one can only favorite an article once
        """
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

        self.assertEqual(1, response.data['favoriteCount'])

    def test_wrong_article_slug(self):
        """
        Test for an non-existent article
        """
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters1/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        self.assertIn('An article with this slug does not exist', response.data['detail'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favourite_count_increase(self):
        
        """ 
        Test favourite count 
        """
        token = self.login_verified_user(self.test_user)
        token2 = self.login_verified_user(self.test_user2)
        token3 = self.login_verified_user(self.test_user3)
        self.create_article(token, self.article)

        response =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
        response1 =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token2,
            format='json'
        )

        response2 =  self.client.post(
            '/api/articles/getters/favorite/',
            self.article,
            HTTP_AUTHORIZATION='Token ' + token3,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(True, response.data['favorited'])
        self.assertEqual(1, response.data['favoriteCount'])
        self.assertEqual(2, response1.data['favoriteCount'])
        self.assertEqual(3, response2.data['favoriteCount'])
