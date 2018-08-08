
from django.db.models import Avg
from rest_framework import mixins, status, viewsets,generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied

from .serializers import ArticleSerializer, RatingSerializer, TagSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import mixins, status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Article, Ratings, Comment, Tag
from .serializers import ArticleSerializer, RatingSerializer
from .renderers import ArticleJSONRenderer, RatingJSONRenderer,CommentJSONRenderer



class LargeResultsSetPagination(PageNumberPagination):
    """
    Set pagination results settings
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10



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
    pagination_class = LargeResultsSetPagination

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
        queryset = Article.objects.all()
        serializer_context = {'request': request}
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )
        output = self.get_paginated_response(serializer.data)
        return output


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

    def get_queryset(self):
        queryset = self.queryset

        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        return queryset


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


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.root_nodes().select_related(
        'article', 'article__author', 'article__author__user',
        'author', 'author__user'
    )
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def filter_queryset(self, queryset):
        # The built-in list function calls `filter_queryset`. Since we only
        # want comments for a specific article, this is a good place to do
        # that filtering.
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}

        return queryset.filter(**filters)

    def create(self, request, article_slug=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentsDestroyGetCreateAPIView(generics.DestroyAPIView, generics.RetrieveAPIView, generics.CreateAPIView):
    lookup_url_kwarg = 'comment_pk'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def destroy(self, request, article_slug=None, comment_pk=None):
        try:
            comment = Comment.objects.get(pk=comment_pk,)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        comment.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    # def retrieve(self, request, article_slug=None, comment_pk=None):
    #     comment = Comment.objects.get(pk=comment_pk)
    #     print(comment)
    #     serializer = self.serializer_class(comment)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def create(self, request,  article_slug=None, comment_pk=None):
        
        data = request.data.get('comment',None)
        context = {'author': request.user.profile}
        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')
        try:
            context['parent'] = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this id does not exists')
            
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(dislikes=request.user):
            serializer_instance.dislikes.remove(request.user)
        serializer_instance.likes.add(request.user)

        serializer = self.serializer_class(serializer_instance, context=serializer_context,
                                           partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DislikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(likes=request.user):
            serializer_instance.likes.remove(request.user)

        serializer_instance.dislikes.add(request.user)

        serializer = self.serializer_class(serializer_instance, context=serializer_context,
                                           partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)
