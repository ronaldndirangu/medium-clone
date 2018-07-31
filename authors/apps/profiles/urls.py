from django.urls import path

#my local imports
from .views import ProfileRetrieveAPIView

app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>/',
        ProfileRetrieveAPIView.as_view(), name='profile'),
]
