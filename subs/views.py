from rest_framework import generics
from rest_framework.permissions import AllowAny

from .permissions import IsModeratorOrReadOnly
from .models import Sub
from .serializers import SubSerializer


class SubListView(generics.ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    
class SubDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    permission_classes = (IsModeratorOrReadOnly,)
