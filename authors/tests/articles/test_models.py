
from django.test import TestCase
from authors.apps.authentication.models import User

from ...apps.articles.models import Article
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User


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

    def favorite_article(self):
        """
        Favorite article.
        """

        user = self.create_a_user(
            username='manud4', email='emachep@gmail.com')
        article = self.create_article()
        user.profile.favorite(article)
        favoriting = user.profile.favorites.all()[0]
        return favoriting

    def unfavorite_article(self):
        """
        Unfavorite article.
        """

        user = self.create_a_user(
            username='manud4', email='emachep@gmail.com')
        article1 = self.create_article()
        article2 = Article.objects.create(
            title="Iam a bull",
            description=self.description,
            body=self.body, author=user.profile)
        article2.save()
        user.profile.favorite(article1)
        user.profile.favorite(article2)
        user.profile.unfavorite(article1)
        unfavoriting = user.profile.favorites.count()
        return unfavoriting

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

    def test_model_favorite_article(self):
        """
        Favorite an article.
        """
        response = CreateArticle().favorite_article()
        self.assertIn(str(response), "Django is life")

    def test_model_unfavorite_article(self):
        """
        Unfavorite an article.
        """
        response = CreateArticle().unfavorite_article()
        self.assertEqual(response, 1)
