from rest_framework import serializers
from .models import Article, Ratings
from authors.apps.profiles.serializers import ProfileSerializer

import re


class ArticleSerializer(serializers.ModelSerializer):
    """
    Defines the article serializer
    """
    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    slug = serializers.SlugField(required=False)
    image_url = serializers.URLField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    author = ProfileSerializer(read_only=True)
    average_rating = serializers.FloatField(required=False, read_only=True)


    class Meta:
        model = Article
        fields = ['title', 'slug', 'body',
                  'description', 'image_url', 'created_at', 'updated_at', 'author', 'average_rating']

    def create(self, validated_data):
        return Article.objects.create(**validated_data)

    def validate(self, data):
        # The `validate` method is used to validate the title,
        # description and body
        title = data.get('title', None)
        description = data.get('description', None)
        # Validate title is not a series of symbols or non-alphanumeric characters
        if re.match(r"[!@#$%^&*~\{\}()][!@#$%^&*~\{\}()]{2,}", title):
            raise serializers.ValidationError(
                "A title must not contain two symbols/foreign characters following each other"
            )
        # Validate the description is not a series of symbols or
        # non-alphanumeric characters
        if re.match(r"[!@#$%^&*~\{\}()][!@#$%^&*~\{\}()]{2,}", description):
            raise serializers.ValidationError(
                """
                A description must not contain two symbols/foreign characters following each other
                """
            )
        return data


class RatingSerializer(serializers.Serializer):
    """
    Defines the article rating serializer
    """

    rating = serializers.IntegerField(required=True)


    def validate(self, data):
        # The `validate` method is used to validate the title, description and body
        # provided by the user during creating or updating an article
        rate = data.get('rating')

        # validate the rate is not a string but an integer or an empty value
        if isinstance(rate, str) or rate is None:
            raise serializers.ValidationError(
                """A valid integer is required."""
            )

        # validate the rate is within range
        if rate > 5 or rate < 1:
            raise serializers.ValidationError(
                """Rate must be a value between 1 and 5"""
            )


        return {"rating": rate}
