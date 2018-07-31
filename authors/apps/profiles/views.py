from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

#my local imports
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist


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
