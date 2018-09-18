from rest_framework import serializers

# my local imports
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """This class contains a serializer for the Profile model"""

    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.CharField(allow_blank=True, required=False)
    interests = serializers.CharField(allow_blank=True, required=False)
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'interests', 'following')
        read_only_fields = ('username',)

    def get_following(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated:
            return False

        follower = request.user.profile
        followed = instance

        return follower.is_following(followed)
