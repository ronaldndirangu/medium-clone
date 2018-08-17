import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
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
                "username": "patrick",
                "email": "patrick.migot@andela.com",
                "password": "Qwert@123"
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
                "title": "tests",
                "body": "lolitas",
                "description": "lolitas quantum physics",
            }
        }

        self.comment = {
            "comment": {
                "body": "lolitas"    
            }
        }

        self.comment_empty = {
             "comment": {
                "body": " "    
            }
        }
        self.comment2 = {
            "comment": {
                "body": "hey there"

            }
        }

        self.comment3 = {
            "comment": {
                "body": "hey there you"

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

        return self.client.post(
            '/api/articles/',
            article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def create_comment(self, token, slug, comment):
        """Create comment"""
       
        return self.client.post(
            '/api/articles/' + slug + '/comments/',
            comment,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def create_thread(self, token, slug, comment, id):
        """Create comment"""
       
        return self.client.post(
            '/api/articles/' + slug + '/comments/' + id + '/',
            comment,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def get_comment(self, token, slug, comment):
        """Create comment"""
        return self.client.get(
            '/api/articles/' + slug + '/comments/',
            comment,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )
    
    def delete_comment(self, token, slug, comment, id):
        """Delete an comment"""
        return self.client.delete(
            '/api/articles/' + slug + '/comments/'+ id +'/',
            HTTP_AUTHORIZATION='Token ' + token,
        )

    def test_can_create_comment(self):
        """Test user can comment on existing article"""
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        response = self.create_comment(token, 'tests', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                      
    def test_cannot_create_empty_comment(self):
        """Test user tries to give an empty comment"""

        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        response = self.create_comment(token, 'tests', self.comment_empty)
        self.assertIn("This field may not be blank.",
                      response.content.decode())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_comment_inexisting_article(self):

        token = self.login_verified_user(self.test_user)
        response = self.create_comment(token, 'tests', self.comment)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("An article with this slug does not exist.",
                      response.content.decode())

    def test_cannot_create_thread_inexisting_comment(self):
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        self.create_comment(token, 'tests', self.comment)
        response = self.create_thread(token, 'tests', self.comment,'1')
        self.assertIn("A comment with this id does not exists",
                      response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_create_thread_from_existing_comment(self):
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        self.create_comment(token, 'tests', self.comment)
        response = self.create_thread(token, 'tests', self.comment3, '2')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_get_comments(self):
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        self.create_comment(token, 'tests', self.comment)
        self.create_comment(token, 'tests', self.comment2)
        response = self.get_comment(token, 'tests', self.comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unverified_user_cannot_create_comment(self):
        """
        Test that a user has to have verified their account for them to create comment
        """
        self.create_user_unverified()
        self.create_article(self.login_unverified_user(), self.article)
        response = self.create_comment(self.login_unverified_user(), 'tests', self.comment)
        self.assertIn("This user has not been verified",
                      response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_comment(self):
        """
        Tests that a user who has no valid token cannot create ancomment
        Tests both a user with an invalid token and without a token
        """
        response = self.create_comment("", 'tests', self.comment)
        self.assertIn("Authentication credentials were not provided.",
                      response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_inexisting_comment(self):
        """Test user cannot  delete inexisting comment """
        token = self.login_verified_user(self.test_user)
        self.create_article(token, self.article)
        self.create_comment(token, 'tests', self.comment)
        response = self.delete_comment(token, 'test', self.comment, '2')
        self.assertIn("A comment with this ID does not exist.",
                      response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_and_retrieve_comment(self):
        """
        Test an authenticated user can edit a comment
        """
        token = self.login_verified_user(self.test_user)
        response = self.client.put('api/articles/tests/comments/1/',
                                   HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.create_article(token, self.article)
        response = self.create_comment(token, 'tests', self.comment)
        # test update comment
        id = json.loads(response.content).get('articles').get('id')
        url = reverse("articles:comment", args=['test', id])
        response = self.client.put(url, {"comment": {"body": "updated comment"}},
                                   format='json', HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test update comment comment similar to existing comment version
        response = self.client.put(url, {"comment": {"body": "updated comment"}},
                                   format='json', HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test retrieve comment edit history non existent comment
        url = reverse("articles:comment_history", args=['test', 1001])
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # test retrieve comment history
        url = reverse("articles:comment_history", args=['tests', id])
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
