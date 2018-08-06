from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
import os

class ViewTestCase(TestCase):
    """Test suite for the api  social login api view."""

    def setUp(self):
        """Define the test client and other test variables."""

        client = APIClient()

class Testsocial(ViewTestCase, APITestCase):
    """This class defines the test suite all social auth."""


    def test_only_allowed_backends_work(self):
        """
        Test for yahoo for instance which is not defined at the moment
        """
        access_token = "EAAH9vlgjWYgBAJzlomW4fMBofoCKwZDZD"
        response = self.client.post('/api/users/auth/yahoo',
            data={'access_token':access_token})

        self.assertEqual(response.status_code, 404)

    def test_invalid_token(self):
        """
        Test for an invalid token
        """
        access_token = "d8s9ns8dnt98fnsy98dy"
        response = self.client.post('/api/users/auth/facebook',
            data ={'access_token':access_token})

        data = response.data.get('errors')
        
        self.assertIn('Invalid token', data["token"])

        self.assertEqual(response.status_code, 400)

    def test_no_token(self):
        """
        Test for an empty token
        """
        access_token = ""
        response = self.client.post('/api/users/auth/facebook',
            data ={'access_token':access_token})

        data = response.data.get('errors')
        self.assertIn("This field may not be blank.", data['access_token'])

        self.assertEqual(response.status_code, 400)

    def test_bad_json(self):
        """
        Test for bad json format
        """
        access_token = None
        response = self.client.post('/api/users/auth/facebook',
            data ={'access_token':access_token})


        self.assertEqual(response.status_code, 400)


        


