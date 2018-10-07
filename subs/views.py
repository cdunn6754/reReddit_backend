from rest_framework import generics, permissions, renderers

from .models import Sub
from .serializers import SubSerializer


class SubList(generics.ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    
class SubDetail(generics.RetrieveAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer    
