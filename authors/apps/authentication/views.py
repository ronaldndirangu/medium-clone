from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http.response import HttpResponse
from .verification import SendEmail, account_activation_token
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # calls function that sends verification email once user is registered
        SendEmail().send_verification_email(user.get('email'), request)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Activate(APIView):
    # Gets uidb64 and token from the send_verification_email function and
    # if valid, changes the status of user in is_verified to True and is_active
    # to True. The user is then redirected to a html page once the verification
    # link is clicked

    permission_classes = (AllowAny, )
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            return HttpResponse('Thank you for your email confirmation. Now you can login your account')
        else:
            return HttpResponse('Activation link is invalid!')


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.user.is_verified:
            user_data = request.data.get('user', {})

            serializer_data = {
                'username': user_data.get('username', request.user.username),
                'email': user_data.get('email', request.user.email),
                
                'profile': {
                    'bio': user_data.get('bio', request.user.profile.bio),
                    'interests': user_data.get('interests', 
                        request.user.profile.interests),
                    'image': user_data.get('image', request.user.profile.image)
                }
            }

            # Here is that serialize, validate, save pattern we talked about
            # before.
            serializer = self.serializer_class(
                request.user, data=serializer_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        message = {"Error": "Email for this user is not verified"}
        return Response(message, status=status.HTTP_403_FORBIDDEN)
