from django.urls import path
from rest_framework import routers
from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, Activate
)
app_name = 'authentication'
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name="register"),
    path('users/login/', LoginAPIView.as_view()),
    path('activate/<uidb64>/<token>/', Activate.as_view(), name="activate"),
]
