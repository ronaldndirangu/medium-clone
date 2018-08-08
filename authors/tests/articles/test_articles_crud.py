import json

from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from authors.apps.authentication.views import Activate
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (APIClient, APIRequestFactory,
                                 force_authenticate)


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

        self.testArticle1 = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }

        self.testArticle2 = {
            "article": {
                "title": "How to feed your dragon",
                "description": "Wanna know how?",
                "body": "You don't believe?",
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

    def update_article(self, token, slug, article):
        """Update an article"""
        return self.client.put(
            '/api/articles/' + slug + '/',
            article,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def delete_article(self, token, slug):
        """Update an article"""
        return self.client.delete(
            '/api/articles/' + slug + '/',
            HTTP_AUTHORIZATION='Token ' + token,
        )

    # tests for field validations
    def test_create_article_missing_required_field(self):
        """Test article cannot be created with missing fields"""
        token = self.login_verified_user(self.testUser1)
        # test missing title
        article = {
            "article": {
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test missing description
        article = {
            "article": {
                "title": "How to train your dragon",
                "body": "You have to believe",
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test missing body
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_empty_required_field(self):
        """Test article cannot be created with missing fields"""
        token = self.login_verified_user(self.testUser1)
        # test empty title
        article = {
            "article": {
                "title": "",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test empty description
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "",
                "body": "You have to believe",
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test empty body
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": ""
            }
        }
        response = self.create_article(token, article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_invalid_title(self):
        """
        Test article cannot be created with invalid title
        for instance plain symbols
        """
        article = {
            "article": {
                "title": "!@#$%^&*()",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        response = self.create_article(self.login_verified_user(self.testUser1), article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_invalid_description(self):
        """Test article description is invalid
        for instance not plain symbols
        """
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "*&^#(!&^#^*(#(#(",
                "body": "You have to believe",
            }
        }
        response = self.create_article(self.login_verified_user(self.testUser1), article)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # end tests for field validations

    # tests for authenticated user
    def test_authenticated_user_can_create_article(self):
        """
        Test that a verified and authenticated user can create an article
        """
        response = self.create_article(self.login_verified_user(self.testUser1), self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_user_can_update_article(self):
        """
        Test that a verified and authenticated user can update an article
        """
        token = self.login_verified_user(self.testUser1)
        # test cannot update nonexistent article
        response = self.update_article(token, 'how-to-train-your-dragon', self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # create article
        response = self.create_article(token, self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the added article
        response = self.update_article(token, 'how-to-train-your-dragon', self.testArticle2)
        self.assertIn('how-to-train-your-dragon', response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_delete_article(self):
        """
        Test that a verified and authenticated user can delete an article
        """
        token = self.login_verified_user(self.testUser1)
        # test cannot delete nonexistent article
        response = self.delete_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # create article
        response = self.create_article(token, self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # delete the added article
        response = self.delete_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure it is deleted
        response = self.delete_article(token, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    # end tests for authenticated user

    # tests for an unverified user
    def test_unverified_user_cannot_create_article(self):
        """
        Test that a user has to have verified their account for them to create an article
        """
        self.create_user_unverified()
        response = self.create_article(self.login_unverified_user(), self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # end tests for an unverified user

    # tests for unauthorised access
    def test_unauthenticated_user_cannot_create_article(self):
        """
        Tests that a user who has no valid token cannot create an article
        Tests both a user with an invalid token and without a token
        """
        response = self.create_article("", self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_article(self):
        """
        Tests that a user who has no valid token cannot update/edit an article
        Tests both a user with an invalid token and without a token
        """
        response = self.update_article("", "how-to-train-your-dragon", self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_article(self):
        """
        Tests that a user who has no valid token cannot delete an article
        Tests both a user with an invalid token and without a token
        """
        response = self.delete_article("", "how-to-train-your-dragon")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    # end tests for unauthorized access

    # tests for get articles
    def test_any_user_can_get_articles(self):
        """
        Tests that any user whether authenticated or not can get a list of
        all articles
        """
        # user gets relevant message when no articles found
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # create 2 articles
        token = self.login_verified_user(self.testUser1)
        self.create_article(token, self.testArticle1)
        self.create_article(token, self.testArticle2)

        response = self.client.get('/api/articles/')
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response.get('articles')), 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_any_user_can_get_article_by_slug(self):
        """
        Test that any user whether verified or not can get an article by slug
        """
        # check user gets relevant message when no articles found with slug provided
        response = self.client.get('/api/articles/how-to-train-your-dragon/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # sign in user and create article with slug:how-to-train-your-dragon
        self.create_article(self.login_verified_user(self.testUser1), self.testArticle1)

        response = self.client.get('/api/articles/how-to-train-your-dragon/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('how-to-train-your-dragon', response.content.decode())
    # end tests for get articles

    def test_user_cannot_edit_others_article(self):
        """Test that any verified user cannot edit tests that they did not create"""
        token_user1 = self.login_verified_user(self.testUser1)
        token_user2 = self.login_verified_user(self.testUser2)

        # user 1 creates an article
        response = self.create_article(token_user1, self.testArticle1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.update_article(token_user2, 'how-to-train-your-dragon', self.testArticle2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_others_article(self):
        """Test that any verified user cannot edit tests that they did not create"""
        token_user1 = self.login_verified_user(self.testUser1)
        token_user2 = self.login_verified_user(self.testUser2)

        # user 1 creates an article
        self.create_article(token_user1, self.testArticle1)

        response = self.delete_article(token_user2, 'how-to-train-your-dragon')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        """
        clear db after each test
        """
