import json
from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    """This class contains json renderer for Profile"""

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if data is not None:
            if len(data) <= 1:
                return json.dumps({
                    'profile': data
                })
            return json.dumps({
                'profiles': data
            })


class FollowersJSONRenderer(JSONRenderer):
    """This class contains json renderer for Profile"""

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps({
            'followers': data
        })


class FollowingJSONRenderer(JSONRenderer):
    """This class contains json renderer for Profile"""

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps({
            'following': data
        })
