from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Sum

from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly
from .pagination import PostListPagination
from subs.models import Sub
from redditors.models import User

class PostListView(ListAPIView):
    """
    Standard list view for posts
    
    query parameter: username
    """
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
    queryset = Post.objects.all()
    serializer_class=PostSerializer
    permission_classes = (IsPosterOrModOrAdminOrReadOnly,)
    
class PostToSubredditView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = ( IsAuthenticatedOrReadOnly, )
    
    def create(self, request, *args, **kwargs):
        """
        Need to grab the subreddit from the url and the authenticated
        user from the request and add them to the serializer data
        NOTE: I wonder if there is a better way to do this, copying data
        is a bummer but dont want these to be read_only
        """
        subreddit_title = kwargs["sub_title"]
        if subreddit_title.lower() in Sub.pseudo_subreddits.keys():
            message = _((
                "You can't create a post to the "
                "'{}' subreddit".format(subreddit_title)
            ))
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            subreddit = Sub.objects.get(title=subreddit_title)
        user = self.request.user
        data = request.data.copy()
        data["subreddit"] = subreddit.pk
        data["poster"] = user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
class SubPostListView(ListAPIView):
    """
    For a particular sub return list of all posts.
    Posts can be ordered with optional GET parameter 'orderby'.
    By default they are ordered by most popular.
    
    query parameter: orderby
    """
    serializer_class = PostSerializer
    pagination_class = PostListPagination
    
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
        """
        Check if posts are requested from a psuedo-subreddit
        or ensure that the requested subreddit exists.
        Either way order the subreddit too.
        NOTE: At this point can't sort with qs.order_by because
        upvotes are not a column of the post table in db.
        """
        order_by = self.request.query_params.get('orderby', 'popular')
        subreddit_title = self.kwargs.get('sub_title', None)
        
        if subreddit_title.lower() in Sub.pseudo_subreddits:
            qs = getattr(
                self,
                "get_{}_queryset".format(subreddit_title.lower())
            )()
        else:
            # make sure the subreddit exists
            try:
                subreddit = Sub.objects.get(title=subreddit_title)
            except Sub.DoesNotExist:
                message = _("The '{}' subreddit does not exist".format(
                    subreddit_title
                ))
                raise exceptions.NotFound(message)
            qs = subreddit.posts.all()
        return sorted(qs, key=self.get_sort_function())
        
    def get_home_queryset(self):
        """
        Create a list of posts for a 'home' subreddit on the fly.
        This will depend on whether the user is signed in or not.
        If they are authenticated then only select posts from
        thier subscribed subreddits. Otherwise just return a list
        of all posts.
        """
        if self.request.user and self.request.user.is_authenticated:
            return Post.objects.filter(
                subreddit__in=self.request.user.subs.all()
            )
            
        # return all posts if unauthed
        return Post.objects.all()
    
    def get_popular_queryset(self):
        """
        Create a list of posts popular posts on the fly that serves as the
        'Popular' psuedo subreddit.
        """
        # Arbitrary popularity limit
        popularity_limit = 1
        
        return Post.objects.annotate(
            custom_upvotes=Sum("votes__vote_type")
        ).filter(custom_upvotes__gt=popularity_limit)
    
    def get_all_queryset(self):
        """
        Get the list of posts on the fly for the psuedo-subreddit 'All'.
        NOTE: At this point I'm not really sure what the actual reddit
        difference is between all and popular so I am just going to
        use popular for now.
        """
        return self.get_popular_queryset()
