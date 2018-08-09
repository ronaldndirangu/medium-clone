import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

#my local imports
from .exceptions import ProfileDoesNotExist
from .models import Profile
from .renderers import ProfileJSONRenderer, FollowersJSONRenderer, FollowingJSONRenderer
from .serializers import ProfileSerializer


class ProfileRetrieveAPIView(RetrieveAPIView):
    """
    This class contains view to retrieve a profile instance.
    Any user is allowed to retrieve a profile
    """

    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related('user')

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist(
                'A profile for user {} does not exist.'.format(username))

        serializer = self.serializer_class(profile,)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('A profile for user {} does not exist.'.format(username))

        if follower.pk is followed.pk:
            raise serializers.ValidationError('You can not unfollow yourself.')

        follower.unfollow(followed)

        serializer = self.serializer_class(followed, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('A profile for user {} does not exist.'.format(username))

        if follower.pk is followed.pk:
            raise serializers.ValidationError('You can not follow yourself.')

        follower.follow(followed)

        serializer = self.serializer_class(followed, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowingRetrieve(ListAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowingJSONRenderer,)
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return self.request.user.profile.follows.all()


class FollowersRetrieve(ListAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FollowersJSONRenderer,)
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return self.request.user.profile.follower.all()
