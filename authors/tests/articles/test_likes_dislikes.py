import json

import jwt
from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from authors.apps.authentication.views import Activate
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (APIClient, APIRequestFactory,
                                 force_authenticate)


class ViewTestCase(TestCase):
    """
    Test case for the api views.
    """

    def setUp(self):
        self.testUser1 = {
            "user": {
                "username": "Jacob",
                "email": "jake@jake.jake",
                "password": "Pass123$"
            }
        }

        self.testUser2 = {
            "user": {
                "username": "Jane",
                "email": "jane@jane.jane",
                "password": "Pass123$"
            }
        }

        self.testArticle = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }

        self.factory = APIRequestFactory()
        self.client = APIClient()

    def create_unverified_user(self):
        """
        Creates a user without verifying them
        """
        self.client.post(
            '/api/users/',
            self.testUser2,
            format='json'
        )

    def login_unverified_user(self):
        """
        Creates a user
        """
        response = self.client.post(
            '/api/users/login/',
            self.testUser2,
            format='json'
        )
        json_response = json.loads(response.content)
        return json_response.get('user').get('token')

    def create_and_verify_user(self, user_profile):
        """
        Verify user email
        """
        user_obj = User.objects.create_user(username=user_profile.get('user').get('username'),
                                            email=user_profile.get('user').get('email'),
                                            password=user_profile.get('user').get('password'))
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(user_obj.email, request)
        request = self.factory.get(reverse("authentication:activate", args=[uid, token]))
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

    def like_article(self, token, slug):
        """
        Likes an article
        """
        return self.client.put(
            '/api/articles/'+slug+'/like/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def dislike_article(self, token, slug):
        """
        Dislike an article
        """
        return self.client.put(
            '/api/articles/'+slug+'/dislike/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def test_verified_user_can_like_article(self):
        """
        Test verified user can like article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that user id in likes field after liking article
        self.assertEqual(jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')['id'],
                         json.loads(response.content).get('articles').get('likes')[0])
        # Assert that likes count is one
        self.assertEqual(json.loads(response.content).get('articles').get('likes_count'), 1)
        # Assert that dislikes count is zero
        self.assertEqual(json.loads(response.content).get('articles').get('dislikes_count'), 0)

    def test_verified_user_can_dislike_article(self):
        """
        Test verified user can like article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.dislike_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that user id in dislikes field after disliking article
        self.assertEqual(jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')['id'],
                         json.loads(response.content).get('articles').get('dislikes')[0])
        # Assert that dislikes count is one
        self.assertEqual(json.loads(response.content).get('articles').get('dislikes_count'), 1)
        # Assert that likes count is zero
        self.assertEqual(json.loads(response.content).get('articles').get('likes_count'), 0)

    def test_unverified_user_cannot_like_article(self):
        """
        Test unverified user cannot like article
        """
        self.create_unverified_user()
        token = self.login_unverified_user()
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.like_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_cannot_dislike_article(self):
        """
        Test unverified user cannot like article
        """
        self.create_unverified_user()
        token = self.login_unverified_user()
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.dislike_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_like_article(self):
        """
        Test unauthenticated user cannot like article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_article("", 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_dislike_article(self):
        """
        Test unauthenticated user cannot like article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.dislike_article("", 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verified_user_cannot_like_and_dislike_article(self):
        """
        Test verified user cannot like and dislike article at the same time
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.like_article(token, 'how-to-train-your-dragon')
        response = self.dislike_article(token, 'how-to-train-your-dragon')
        self.assertNotEqual(json.loads(response.content).get('articles').get('likes'),
                            json.loads(response.content).get('articles').get('dislikes'))

    def test_verified_user_cannot_like_unexisting_article(self):
        """
        Test verified user cannot like unexisting article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.like_article(token, 'unexisting-article')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verified_user_cannot_dislike_unexisting_article(self):
        """
        Test verified user cannot dislike unexisting article
        """
        token = self.login_verified_user(self.testUser1)
        response = self.dislike_article(token, 'unexisting-article')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
