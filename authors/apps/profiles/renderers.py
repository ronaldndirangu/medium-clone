import json
from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    """This class contains json renderer for Profile"""

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        #handle rendering errors
        errors = data.get('errors', None)
        if errors is not None:
            return super(ProfileJSONRenderer, self).render(data)

        return json.dumps({
            'profile': data
        })
