from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.authentication.verification import SendEmail
from django.core import mail
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import force_authenticate
from authors.apps.authentication.views import Activate


class VerifyTestCase(TestCase):
    """Test suite for registration verification."""

    def setUp(self):
        """Define the test client and other test variables."""

        self.first_user = {
             "user":{
                "username": "janey",
                "email": "janet.wairimu@andela.com",
                "password": "Secretsecret254"
                }
            }
        self.second_user = {
            "user":{
            "username": "jojo",
            "email": "jojo@.com",
            "password": "jojojojo254"
            }
        }

        self.factory = APIRequestFactory()
        self.client = APIClient()

    def test_email_sent(self):
        """Test if email has been sent and has verification content"""

        response = self.client.post(
            '/api/users/',
            self.first_user,
            format='json'
        )

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Verify your Authors Haven account')

    def test_account_is_verified(self):
        """Test if registered user has verified their account from link sent in tge email"""

        obj = User.objects.create_user(username="janet", email="janet.wairimu@andela.com", password="janet2565637")
        request = self.factory.get(reverse("authentication:register"))
        token, uid = SendEmail().send_verification_email(obj.email, request)
        request = self.factory.get(reverse("authentication:activate", args=[uid, token]))
        force_authenticate(request, obj, token=obj.token)
        view = Activate.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertTrue(response.status_code, 200)
        user = User.objects.get()
        self.assertTrue(user.is_verified)
        self.assertTrue("Thank you for your email confirmation. Now you can login your account.")

