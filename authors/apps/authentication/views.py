from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.http.response import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from requests.exceptions import HTTPError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view, list_route, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.exceptions import MissingBackend
from social_django.utils import load_backend, load_strategy

from .models import User
from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer, NotificationToggleSerializer,
                          PassResetSerializer, RegistrationSerializer,
                          ResetPassSerializer, SocialSerializer,
                          UserSerializer)
from .verification import SendEmail, account_activation_token


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
        SendEmail().send_verification_email(user.get('email', None), request)

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


class Reset(APIView):
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
            user.is_reset = True
            user.save()

            encode_mail = urlsafe_base64_encode(
                force_bytes(user.email)).decode('utf-8')
            return Response({"token": encode_mail})
        else:
            return Response({"msg": "Error"})


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


class ResetPassAPIView(APIView):
    """
        This view class facilitates sending of reset password email
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPassSerializer

    def post(self, request):
        # get user input
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        # If user exists
        if not serializer.data["email"] == "False":
            # Send email
            SendEmail().send_reset_pass_email(user.get('email'), request)
            return Response({"msg": "Success, reset email sent."},
                            status=status.HTTP_200_OK)
        return Response({"msg": "Email doesn't exist, register instead."},
                        status=status.HTTP_404_NOT_FOUND)


class PassResetAPIView(APIView):
    """
        View class that allows user to set a new password upon receiving the reset
        password token
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @list_route(methods=['put'], serializer_class=PassResetSerializer)
    def put(self, request):
        # get user input
        user = request.data.get('user', {})
        serializer = PassResetSerializer(data=user)
        # Check if serializer is valid
        if serializer.is_valid():
            decode_email = force_text(
                urlsafe_base64_decode(serializer.data['reset_token']))
            instance = User.objects.get(email=decode_email)

            # If `is_reset` is false, this means that the link has already
            # been used
            if instance.is_reset is False:
                return Response({
                    "msg": "Sorry, this link has already been used."
                }, status=status.HTTP_403_FORBIDDEN)

            # Set new password
            instance.set_password(serializer.data['new_password'])
            instance.is_reset = False
            instance.save()
            return Response({
                "msg": "Success! Password for '{}' has been changed.".format(
                    decode_email)
            }, status=status.HTTP_201_CREATED)
        # Invalid serializer
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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


class ExchangeToken(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialSerializer
    serializer_class2 = UserSerializer

    def create(self, request, backend):
        serializer = SocialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        strategy = load_strategy(request)

        try:
            backend = load_backend(
                strategy=strategy, name=backend, redirect_uri=None)
        except MissingBackend as e:
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_404_NOT_FOUND)
        try:
            token = serializer.data.get("access_token")
            user = backend.do_auth(token)
        except HTTPError as e:
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user:
            if user.is_active:
                user.is_verified = True
                dt = datetime.now() + timedelta(days=30)
                token = jwt.encode({
                    'username': user.username,
                    'id': user.pk,
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'exp': int(dt.strftime('%s'))
                }, settings.SECRET_KEY, algorithm='HS256')
                token = token.decode('utf-8')
                serializer.instance = user
                user.save()
                return Response({'token': token, 'user': serializer.data})
            else:

                return Response(
                    {'errors': {"user": 'This user account is inactive'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {'errors': {"user": "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,

            )


class NotificationToggleViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = NotificationToggleSerializer
    renderer_classes = (UserJSONRenderer, )

    def update(self, request):
        if request.user.get_notified:
            request.user.get_notified = False
        else:
            request.user.get_notified = True
        request.user.save()
        serializer = self.serializer_class(request.user, partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
