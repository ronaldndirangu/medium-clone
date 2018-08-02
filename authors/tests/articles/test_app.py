from django.apps import apps
from django.test import TestCase
from authors.apps.articles.apps import ArticlesConfig


class ReportsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ArticlesConfig.name, 'articles')
