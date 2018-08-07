from django.db.models import Avg
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import mixins, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Article, Ratings
from .serializers import ArticleSerializer, RatingSerializer
from .renderers import ArticleJSONRenderer, RatingJSONRenderer


class ArticleViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    lookup_field = 'slug'
    queryset = Article.objects.annotate(
        average_rating = Avg("rating__stars")
    )
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def create(self, request):
        """
        Overrides the create method to create a article
        """
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        Overrides the list method to get all articles
        """
        queryset = Article.objects.annotate(
            average_rating = Avg("rating__stars")
            ).all()
        serializer = self.serializer_class(
           queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug):
        """
        Override the retrieve method to get a article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist")

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context

        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        """
        Override the update method to update an article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist.")

        if not serializer_instance.author_id == request.user.profile.id:
            raise PermissionDenied(
                "You are not authorized to edit this article.")

        serializer_data = request.data.get('article', )

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context,
            data=serializer_data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        """
        Override the destroy method to delete an article
        """
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist")

        if article.author_id == request.user.profile.id:
            article.delete()
        else:
            raise PermissionDenied(
                "You are not authorized to delete this article.")

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class RateAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (RatingJSONRenderer,)
    serializer_class = RatingSerializer

    def post(self, request, slug):
        """
        Method that posts users article ratings
        """
        rating = request.data.get("rate", {})
        serializer = self.serializer_class(data=rating)
        serializer.is_valid(raise_exception=True)
        rating = serializer.data.get('rating')
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")
        ratings = Ratings.objects.filter(rater=request.user.profile, article=article).first()
        if not ratings:
            ratings = Ratings(article=article, rater=request.user.profile, stars=rating)
            ratings.save()
            avg = Ratings.objects.filter(article=article).aggregate(Avg('stars'))
            return Response({
                "avg":avg
                }, status=status.HTTP_201_CREATED)

        if ratings.counter >= 5: 
            raise PermissionDenied("You are not allowed to rate this article more than 5 times.")
        ratings.counter += 1
        ratings.stars = rating
        ratings.save()
        avg = Ratings.objects.filter(article=article).aggregate(Avg('stars'))
        return Response({"avg":avg}, status=status.HTTP_201_CREATED)
