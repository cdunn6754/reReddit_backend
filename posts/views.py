from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly
from subs.models import Sub
from redditors.models import User

class PostListView(ListAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get_serializer_context(self):
        """
        It will really speed up some vote lookups in the
        serializer if we can turn a username into a user_pk at this point.
        This is only relevant if the consumer provides a get param 'username'
        """
        context = super().get_serializer_context()
        username = self.request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return context
            context['post_user_pk'] = user.pk
        return context
    
class PostDetailView(RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsPosterOrModOrAdminOrReadOnly,)
    
class SubPostListView(ListAPIView):
    """
    For a particular sub return list of all posts.
    Posts can be ordered with optional GET parameter 'orderby'.
    By default they are ordered by most popular.
    """
    serializer_class = PostSerializer
    
    def get_sort_function(self):
        """
        Given an api sort description (e.g. 'popular' or 'new') return
        a key function that can be used in sort based on the acutal
        model attributes nomenclature.
        """
        sort_functions = {
            'popular': (lambda post: -post.upvotes),
            'new': (lambda post: (timezone.now() - post.created))
        }
        api_sort_key = self.request.query_params.get('orderby', 'popular')
        return sort_functions.get(api_sort_key, sort_functions['popular'])
    
    def get_queryset(self):
        order_by = self.request.query_params.get('orderby', 'popular')
        subreddit_title = self.kwargs.get('sub_title', None)
        
        queryset = Post.objects.filter(
            subreddit__title=subreddit_title
        )
        # can't use Queryset.order_by because upvotes isn't in the database
        return sorted(queryset, key=self.get_sort_function())
    
    def get(self, request, *args, **kwargs):
        # Be sure the subreddit exist before anything else
        subreddit_title = self.kwargs.get('sub_title', None)
        try:
            Sub.objects.get(title=subreddit_title)
        except Sub.DoesNotExist:
            return Response({'detail': "This subreddit does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        return self.list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        """
        It will really speed up some vote lookups in the
        serializer if we can turn a username into a user_pk at this point.
        This is only relevant if the consumer provides a get param 'username'
        """
        context = super().get_serializer_context()
        username = self.request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return context
            context['post_user_pk'] = user.pk
        return context
        
