from django.test import TestCase
from authors.apps.authentication.models import User

from ...apps.articles.models import Article


class CreateArticle():
    def __init__(self):
        self.title = "Django is life"
        self.body = """Try it today. Lorem ipsum dolor sit amet, 
                consectetur adipiscing elit, sed do eiusmod tempor 
                incididunt ut labore et dolore magna aliqua. Ut enim 
                ad minim veniam, quis nostrud exercitation ullamco laboris"""
        self.description = "Django"

    def create_a_user(self, username="nerd", email="nerd@nerd.com", password="secret"):
        """Creating a test user"""
        user = User.objects.create_user(username, email, password)
        user.save()
        return user

    def create_article(self):
        """Creating a test article"""
        user = self.create_a_user()
        article = Article.objects.create(
            title=self.title, 
            description=self.description, 
            body=self.body, author=user.profile)
        article.save()
        return article


class ModelTestCase(TestCase):
    """
    This class defines the test suite for the article model.
    """

    def test_model_can_create_an_article(self):
        """Test the user model can create an article."""

        response = CreateArticle().create_article()
        self.assertTrue(isinstance(response, Article))

    def test_model_returns_readable_representation(self):
        """
        Test a readable string is returned for the model instance.
        """
        response = CreateArticle().create_article()
        self.assertIn(str(response), "Django is life")

    def test_timestamp_added(self):
        """
        Test that article model adds a `created_at` timestamp 
        on user creation. 
        """
        response = CreateArticle().create_article()
        self.assertIsNotNone(response.created_at)
