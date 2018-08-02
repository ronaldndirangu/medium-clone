from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleViewSet, base_name='articles')

urlpatterns = [
    path('', include(router.urls)),
]
