from rest_framework import generics, permissions, renderers
from rest_framework import permissions as drf_permissions

from . import permissions


from .models import Sub
from .serializers import SubSerializer


class SubList(generics.ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    
    
class SubDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    permission_classes = (permissions.IsModeratorOrReadOnly,)
