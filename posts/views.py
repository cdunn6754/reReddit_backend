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
        """
        Custom get method to filter out requests for the posts of
        `home` and `popular` as well as to perform a check that
        otherwise the requested subreddit exists.
        """
        subreddit_title = self.kwargs.get('sub_title', None)
        if subreddit_title.lower() == 'popular':
            return self.get_popular(request, *args, **kwargs)
        elif subreddit_title.lower() == 'home':
            return self.get_home(request, *args, **kwargs)
        elif subreddit_title.lower() == 'all':
            return self.get_all(request, *args, **kwargs)
        else:
            try:
                Sub.objects.get(title=subreddit_title)
            except Sub.DoesNotExist:
                return Response({'detail': "This subreddit does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
            return self.list(request, *args, **kwargs)
            
    def get_home(self, request, *args, **kwargs):
        """
        Create a list of posts for a 'home' subreddit on the fly.
        This will depend on whether the user is signed in or not.
        If they are authenticated then only select posts from
        thier subscribed subreddits. Otherwise just return a list
        of all posts.
        """
        if not request.auth:
            posts = Post.objects.all()
            serializer = self.get_serializer(
                Post.objects.all(),
                many=True
            )
            return Response(serializer.data)
            
        user_subreddit_posts = Post.objects.filter(
            subreddit__in=request.user.subs.all()
        )
        sorted_posts = sorted(user_subreddit_posts, key=self.get_sort_function())
        serializer = self.get_serializer(
            sorted_posts,
            many=True
        )
        return Response(serializer.data)
        
            
    def get_popular(self, request, *args, **kwargs):
        """
        Create a list of posts popular posts on the fly, there is
        no 'popular' subreddit.
        TODO: create a celery task to make this happen behind the scenes
        """
        popularity_limit = 1
        popular_posts = [
            post for post in Post.objects.all()
            if post.upvotes >= popularity_limit
        ]
        serializer = self.get_serializer(
            sorted(popular_posts, key=self.get_sort_function()),
            many=True
        )
        return Response(serializer.data)
        
    def get_all(self, request, *args, **kwargs):
        """
        Get the list of posts on the fly for the psuedo-subreddit 'all'.
        NOTE: At this point I'm not really sure what the actual reddit
        difference is between all and popular so I am just going to
        use popular for now.
        """
        return self.get_popular(request, *args, **kwargs)
    
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
        
