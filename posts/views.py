from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly
from subs.models import Sub
from utilities.reddit_orderby import ordering

class PostListView(ListAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
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
    
    def get_queryset(self):
        order_by = self.request.query_params.get('orderby', 'popular')
        sub_title = self.kwargs.get('sub_title', None)
        
        order_by = ordering.get(order_by, None)
        
        queryset = Post.objects.filter(sub__title__exact=sub_title).order_by(order_by)
        return queryset
    
    def get(self, request, *args, **kwargs):
        # Be sure the sub exist before anything else
        sub_title = self.kwargs.get('sub_title', None)
        try:
            Sub.objects.get(title=sub_title)
        except Sub.DoesNotExist:
            return Response({'detail': "This subreddit does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        return self.list(request, *args, **kwargs)
        
