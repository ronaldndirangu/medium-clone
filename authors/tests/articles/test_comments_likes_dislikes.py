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
                "title": "dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }

        self.comment = {
            "comment": {
                "body": "That is fine"
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
        user_obj = User.objects.create_user(
                        username=user_profile.get('user').get('username'),
                        email=user_profile.get('user').get('email'),
                        password=user_profile.get('user').get('password')
                        )
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(
                                                        user_obj.email, request
                                                        )
        request = self.factory.get(
                        reverse("authentication:activate", args=[uid, token])
                        )
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

    def create_comment(self, token, slug, comment,):
        """Create comment"""

        return self.client.post(
            '/api/articles/' + slug + '/comments/',
            comment,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def like_comment(self, token, slug, id):
        """
        Like a comment.
        """
        return self.client.post(
            '/api/articles/' + slug + '/comments/' + id + '/like/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def undo_like(self, token, slug, id):
        """
        Undo a like made on a comment.
        """
        results = self.like_comment(token, slug, id)
        results = self.like_comment(token, slug, id)
        return results

    def dislike_comment(self, token, slug, id):
        """
        Undo a dislike made on  a comment.
        """
        return self.client.post(
            '/api/articles/' + slug + '/comments/' + id + '/dislike/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def undo_dislike(self, token, slug, id):
        """
        Undo a dislike.
        """
        results = self.dislike_comment(token, slug, id)
        results = self.dislike_comment(token, slug, id)
        return results

    def like_comment_by_two_users(self, slug, id, token=None, token2=None):
        """
        Two users liking a comment.
        """
        results = self.like_comment(token, slug, id)
        results = self.like_comment(token2, slug, id)
        return results

    def dislike_comment_by_two_users(self, slug, id, token=None, token2=None):
        """
        Two users disliking a comment.
        """
        results = self.dislike_comment(token, slug, id)
        results = self.dislike_comment(token2, slug, id)
        return results

    def test_verified_user_can_like_comment(self):
        """
        Test verified user can like comment.
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment(token, 'dragon', str(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 1)
        self.assertEqual(response.data['comment_dislikes'], 0)

    def test_verified_user_can_dislike_comment(self):
        """
        Test verified user can dislike comment
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment(token, 'dragon', str(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 1)
        self.assertEqual(response.data['comment_dislikes'], 0)
        response = self.dislike_comment(token,
                                        'dragon', str(response.data['id'])
                                        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 0)
        self.assertEqual(response.data['comment_dislikes'], 1)

    def test_wrong_comment_id(self):
        """
        Test wrong comment id.
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment(token, 'dragon', '3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],
                         'A comment with this id does not exist'
                         )

    def test_wrong_article_slug(self):
        """
        Test wrong article slug.
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment(token, 'me', '3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
                    'An article with this slug does not exist',
                    response.data['detail']
                    )

    def test_unverified_user_cannot_like_comment(self):
        """
        Test unverified user cannot like comment.
        """
        self.create_unverified_user()
        token = self.login_unverified_user()
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.like_comment(token, 'dragon', '9')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)    

    def test_unverified_user_cannot_dislike_comment(self):
        """
        Test unverified user cannot dislike comment.
        """
        self.create_unverified_user()
        token = self.login_unverified_user()
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response1 = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        response2 = self.dislike_comment(token, 'dragon', '9')
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_likes_count_increases(self):
        """
        Test the count increases after several likes by different users.
        """
        token = self.login_verified_user(self.testUser1)
        token2 = self.login_verified_user(self.testUser2)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment_by_two_users(
                                                'dragon',
                                                str(response.data['id']),
                                                token,
                                                token2
                                                )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 2)
        self.assertEqual(response.data['comment_dislikes'], 0)

    def test_likes_count_decreases(self):
        """
        Test the count decreases after a  dislike.
        """
        token = self.login_verified_user(self.testUser1)
        token2 = self.login_verified_user(self.testUser2)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response1 = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment_by_two_users(
                                                'dragon',
                                                str(response1.data['id']),
                                                token,
                                                token2
                                                )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 2)
        response = self.dislike_comment_by_two_users(
                                                    'dragon',
                                                    str(response1.data['id']),
                                                    token,
                                                    token2
                                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_dislikes'], 2)
        self.assertEqual(response.data['comment_likes'], 0)

    def test_undo_like(self):
        """
        Test the likes count does not increase after liking twice by same user.
        Unlikes intead.
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.undo_like(token, 'dragon', str(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 0)
        self.assertNotEqual(response.data['comment_likes'], 1)

    def test_likes_count_decreases_once_for_a_user(self):
        """
        Test the dislikes count does not increase after disliking twice.
        """
        token = self.login_verified_user(self.testUser1)
        token2 = self.login_verified_user(self.testUser2)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.like_comment_by_two_users(
                                                'dragon',
                                                str(response.data['id']),
                                                token,
                                                token2
                                                )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_likes'], 2)
        self.assertEqual(response.data['comment_dislikes'], 0)
        response = self.undo_dislike(token, 'dragon', str(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_dislikes'], 0)
        self.assertNotEqual(response.data['comment_dislikes'], 1)

    def test_undo_dislike(self):
        """
        Test to see if the second dislike undoes the dislike.
        """
        token = self.login_verified_user(self.testUser1)
        response = self.create_article(token, self.testArticle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_comment(token, 'dragon', self.comment)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.undo_dislike(token, 'dragon', str(response.data['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_dislikes'], 0)
