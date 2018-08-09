from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
import json
from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from authors.apps.authentication.views import Activate
from ..models import Profile


class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""

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

        self.factory = APIRequestFactory()
        self.client = APIClient()

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

    def test_follow_and_unfollow_existing_user(self):
        """
        Test authenticated user can follow and un-follow other users
        """
        token = self.login_verified_user(self.testUser1)
        self.create_and_verify_user(self.testUser2)

        response = self.client.post('/api/profiles/Jane/follow/',
                                    HTTP_AUTHORIZATION='Token ' + token,)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete('/api/profiles/Jane/follow/',
                                      HTTP_AUTHORIZATION='Token ' + token,)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_and_unfollow_non_existent_user(self):
        """
        Test authenticated user can follow and un-follow other users
        """
        token = self.login_verified_user(self.testUser1)

        response = self.client.post('/api/profiles/Jane/follow/',
                                    HTTP_AUTHORIZATION='Token ' + token, )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete('/api/profiles/Jane/follow/',
                                      HTTP_AUTHORIZATION='Token ' + token, )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_and_unfollow_without_token(self):
        """
        Test unauthenticated user cannot follow and un-follow
        """
        response = self.client.post('/api/profiles/Jane/follow/',
                                    HTTP_AUTHORIZATION='Token ')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follow_and_unfollow_yourself(self):
        """
        Test authenticated user cannot follow and un-follow themselves
        """
        token = self.login_verified_user(self.testUser1)

        response = self.client.post('/api/profiles/Jacob/follow/',
                                    HTTP_AUTHORIZATION='Token ' + token, )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete('/api/profiles/Jacob/follow/',
                                      HTTP_AUTHORIZATION='Token ' + token, )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_followers(self):
        """
        Test user can retrieve a list of their followers
        """
        token = self.login_verified_user(self.testUser1)
        token2 = self.login_verified_user(self.testUser2)
        # test no followers
        response = self.client.get('/api/followers/',
                                   HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.data.get('results'), [])

        # add one follower
        response = self.client.post('/api/profiles/Jane/follow/',
                                    HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test one follower can be retrieved for user
        response = self.client.get('/api/followers/',
                                   HTTP_AUTHORIZATION='Token ' + token2)
        self.assertEqual(1, json.loads(response.content).get('followers').get('count'))

    def test_retrieve_following(self):
        """
        Test user can retrieve a list of users they are following
        """
        token = self.login_verified_user(self.testUser1)
        self.login_verified_user(self.testUser2)
        # test no followed users
        response = self.client.get('/api/following/',
                                   HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.data.get('results'), [])
        # add one following
        response = self.client.post('/api/profiles/Jane/follow/',
                                    HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test one follower can be retrieved for user
        response = self.client.get('/api/following/',
                                   HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(1, json.loads(response.content).get('following').get('count'))
