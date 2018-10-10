from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from .models import Post
from .serializers import PostSerializer
from .permissions import IsPosterOrModOrAdminOrReadOnly, IsMemberOfSubOrReadOnly

class PostListView(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsAuthenticatedOrReadOnly, IsMemberOfSubOrReadOnly)  
    
    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)  
    
    
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    
    permission_classes = (IsPosterOrModOrAdminOrReadOnly,)