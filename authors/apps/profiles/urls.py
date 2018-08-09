from django.urls import path

#my local imports
from .views import ProfileRetrieveAPIView, UserFollowAPIView, \
    FollowersRetrieve, FollowingRetrieve


app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>/',
        ProfileRetrieveAPIView.as_view(), name='profile'),
    path('profiles/<username>/follow/', UserFollowAPIView.as_view()),
    path('followers/', FollowersRetrieve.as_view()),
    path('following/', FollowingRetrieve.as_view()),
]
