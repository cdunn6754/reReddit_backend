from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly
from subs.models import Sub

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
        
        # A little change in nomenclature
        ordering = {'popular': 'upvotes',
                         'new': '-created',}
        order_by = ordering.get(order_by, None)
        
        queryset = Post.objects.filter(sub__title__exact=sub_title).order_by(order_by)
        return queryset
        
