from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly

class PostListView(ListAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
class PostDetailView(RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsPosterOrModOrAdminOrReadOnly,)
