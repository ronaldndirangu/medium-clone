from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, DislikesAPIView, LikesAPIView, RateAPIView

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleViewSet, base_name='articles')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug>/rate/', RateAPIView.as_view()),
    path('articles/<slug>/like/', LikesAPIView.as_view()),
    path('articles/<slug>/dislike/', DislikesAPIView.as_view()),
]
