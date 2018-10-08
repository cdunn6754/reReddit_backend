from rest_framework import generics
from rest_framework import permissions as drf_permissions


from .models import Post
from .serializers import PostSerializer

class PostListView(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (drf_permissions.AllowAny,)
