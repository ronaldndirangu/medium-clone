from django.urls import path
from rest_framework import routers
from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)
app_name = 'authentication'
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
]
