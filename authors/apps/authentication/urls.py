from django.urls import path
from rest_framework import routers
from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, Activate, ExchangeToken,
    ResetPassAPIView, Reset, PassResetAPIView, NotificationToggleViewSet
)
app_name = 'authentication'
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name="register"),
    path('users/login/', LoginAPIView.as_view()),
    path('activate/<uidb64>/<token>/', Activate.as_view(), name="activate"),
    path('users/auth/<backend>', ExchangeToken.as_view()),
    path('users/reset_pass/', ResetPassAPIView.as_view()),
    path('reset/<uidb64>/<token>/', Reset.as_view(), name="reset"),
    path('users/pass_reset/', PassResetAPIView.as_view()),
    path('notifications/toggle/',
         NotificationToggleViewSet.as_view({'put': 'update'})),
]
