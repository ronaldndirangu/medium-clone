import json

from rest_framework.renderers import JSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render the articles in a structured manner for the end user.
        """
        if data is not None:
            if len(data) <= 1:
                return json.dumps({
                    'article': data
                })
            return json.dumps({
                'articles': data
            })
        return json.dumps({
            'article': 'No article found.'
        })


class RatingJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render the ratings in a structured manner for the end user.
        """
        return json.dumps({
            'rate': data,
        })

class CommentJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render the articles in a structured manner for the end user.
        """
        if data is not None:
            if len(data) <= 1:
                return json.dumps({
                    'article': data
                })
            return json.dumps({
                'articles': data
            })
        return json.dumps({
            'article': 'No article found.'
        })


class FavoriteJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    """
        Render the favorited articles in a structured manner for the user.
    """

    def render(self, data, media_type=None, renderer_context=None):
        
        return json.dumps({
            'articles': data
        })


class CommentEditHistoryJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    """
        Render the comment edit history in a structured manner for the user.
    """
    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps({
            'comment_history': data
        })


class CommentLikeJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    """
        Render the favorited articles in a structured manner for the user.
    """

    def render(self, data, media_type=None, renderer_context=None):
        
        return json.dumps({
            'comment':data
        })
