from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, RateAPIView

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleViewSet, base_name='articles')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug>/rate/', RateAPIView.as_view()),
]
