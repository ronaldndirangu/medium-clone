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
                "username": "jj",
                "email": "jj@andela.com",
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
        self.comment = {
            "comment": {
                "body": "This is Andela EPIC"
            }
        }

        """Initialize client"""
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def create_and_verify_user(self, user):
        """
        Check user has verified account from email
        """
        user_obj = User.objects.create_user(username=user.get('user').get(
            'username'), email=user.get('user').get('email'), password=user.get('user').get('password'))
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(user_obj.email, request)
        request = self.factory.get(
            reverse("authentication:activate", args=[uid, token]))
        force_authenticate(request, user_obj, token=user_obj.token)
        view = Activate.as_view()
        view(request, uidb64=uid, token=token)
        user = User.objects.last()
        return user.is_verified

    def login_verified_user(self, user):
        """
        Logs in created and verified user to get token
        """
        response = self.client.post(
            '/api/users/login/',
            user,
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

    def favorite_article(self, token, slug):
        """
        Favorites an article for testing
        """
        return self.client.post(
            '/api/articles/' + slug + '/favorite/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def follow_user(self, user, token):
        """
        Following another user
        """
        return self.client.post(
            '/api/profiles/'+user['user']['username']+'/follow/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def comment_article(self, token, slug):
        """
        Following another user
        """
        return self.client.post(
            '/api/articles/' + slug + '/comments/',
            self.comment,
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def toggle_notifications(self, token):
        """
        Subscribes and unsubscribes a user from receiving nnotification
        """
        return self.client.put(
            '/api/notifications/toggle/',
            HTTP_AUTHORIZATION='Token ' + token,
            format='json'
        )

    def test_follower_gets_article_notifications(self):
        """
        Test if notification is sent when a user I follow creates an article
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        self.follow_user(self.test_user2, token_user)
        self.create_article(token_user2, self.article)
        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 1)
        self.assertEqual((json.loads(response.content)
                          ['notifications']['unread_list'][0]['verb']), 'was posted')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_favorited_article_comment_notifications(self):
        """
        Testing a user should be able to receive notifications on an article they have favorited
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)

        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 1)
        self.assertEqual((json.loads(response.content)
                          ['notifications']['unread_list'][0]['verb']), 'was commented on')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_ufavorited_article_comment_notifications(self):
        """
        Testing a user should not get notification if they have not favorited an article
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.comment_article(token_user2, slug)

        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 0)
        self.assertEqual((json.loads(response.content)
                          ['notifications']['unread_list']), [])

    def test_unfollowed_user_article_notifications(self):
        """
        Testing if notification is sent when a user I follow creates an article
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        self.create_article(token_user2, self.article)
        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 0)
        self.assertEqual((json.loads(response.content)
                          ['notifications']['unread_list']), [])

    def test_user_cannot_read_notification(self):
        """
        Testing a user reads a favorite article notification
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        id = str(json.loads(res.content)['articles']['id'])
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)
        response = self.client.put(
            '/api/notifications/' + id + '/read/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertIn(
            "The notification with the given id doesn't exist", response.content.decode())
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_user_reads_notification(self):
        """
        Testing a user reads a favorite article notification
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)
        request = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        id = str(json.loads(request.content)[
            'notifications']['unread_list'][0]['id'])
        response = self.client.put(
            '/api/notifications/' + id + '/read/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertIn("Notification marked as read", response.content.decode())
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_deletes_notifications(self):
        """
        Testing that a user can delete a notification
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)

        request = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )

        id = str(json.loads(request.content)[
            'notifications']['unread_list'][0]['id'])

        response = self.client.delete(
            '/api/notifications/' + id + '/delete/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertIn("Notification has been deleted",
                      response.content.decode())
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_toggle(self):
        """
        Testing that a user can toggle
        """
        self.create_and_verify_user(self.test_user)
        token_user = self.login_verified_user(self.test_user)
        response = self.toggle_notifications(token_user)

        self.assertFalse(json.loads(response.content)['user']['get_notified'])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

        response2 = self.toggle_notifications(token_user)

        self.assertFalse(json.loads(response.content)['user']['get_notified'])
        self.assertEqual(response2.status_code,
                         status.HTTP_200_OK)

    def test_toggle_notifications(self):
        """
        Testing that a user can be able to opt in and out of notifications
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        self.toggle_notifications(token_user)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)

        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )

        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 0)
        self.assertEqual((json.loads(response.content)
                          ['notifications']['unread_list']), [])
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

        self.toggle_notifications(token_user)
        self.comment_article(token_user2, slug)

        response = self.client.get(
            '/api/notifications/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertEqual(json.loads(response.content)
                         ['notifications']['unread_count'], 1)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_mark_all_notifications_as_read(self):
        """
        Testing that a user can mark all unread notifications as read
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)
        self.comment_article(token_user2, slug)

        response = self.client.put(
            '/api/notifications/read/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertIn("You have marked all notifications as read",
                      response.content.decode())

    def test_no_unread_notifications(self):
        """
        Testing that a user cannot mark all notifications as read
        """
        self.create_and_verify_user(self.test_user)
        self.create_and_verify_user(self.test_user2)
        token_user = self.login_verified_user(self.test_user)
        token_user2 = self.login_verified_user(self.test_user2)
        res = self.create_article(token_user2, self.article)
        slug = json.loads(res.content)['articles']['slug']
        self.favorite_article(token_user, slug)
        self.comment_article(token_user2, slug)
        self.comment_article(token_user2, slug)

        self.client.put(
            '/api/notifications/read/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        request = self.client.put(
            '/api/notifications/read/',
            HTTP_AUTHORIZATION='Token ' + token_user,
            format='json'
        )
        self.assertIn("You have no unread notifications",
                      request.content.decode())
