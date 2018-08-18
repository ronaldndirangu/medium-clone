from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (ArticleViewSet,
                    RateAPIView,
                    CommentsListCreateAPIView,
                    CommentsDestroyGetCreateAPIView,
                    DislikesAPIView,
                    LikesAPIView,
                    TagListAPIView,
                    FavoriteAPIView,
                    LikeCommentLikesAPIView,
                    DislikeCommentLikesAPIView,
                    CommentEditHistoryAPIView,
                    FilterAPIView
                    )

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleViewSet, base_name='articles')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug>/rate/', RateAPIView.as_view()),
    path('articles/<article_slug>/comments/',
         CommentsListCreateAPIView.as_view()),
    path('articles/<article_slug>/comments/<comment_pk>/',
         CommentsDestroyGetCreateAPIView.as_view(), name="comment"),
    path('articles/<slug>/like/', LikesAPIView.as_view()),
    path('articles/<slug>/dislike/', DislikesAPIView.as_view()),
    path('tags/', TagListAPIView.as_view()),
    path('articles/<slug>/favorite/', FavoriteAPIView.as_view()),

    path('articles', FilterAPIView.as_view(), name='filter'),
    path('articles/<article_slug>/comments/<comment_pk>/like/',
         LikeCommentLikesAPIView.as_view()),
    path('articles/<article_slug>/comments/<comment_pk>/dislike/',
         DislikeCommentLikesAPIView.as_view()),
    path('articles/<slug>/comments/<comment_pk>/history/',
         CommentEditHistoryAPIView.as_view(), name="comment_history"),
]
