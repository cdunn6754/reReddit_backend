from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsModeratorOrAdminOrReadOnly
from .models import Sub
from .serializers import SubSerializer

from redditors.models import UserSubMembership


class SubListView(generics.ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    def perform_create(self, serializer):
        """ 
        Whomever creates this sub will be the sole inital moderator.
        Also make them a sub member.
        """
        user = self.request.user        
        new_sub = serializer.save()
        new_sub.moderators.add(user)
        UserSubMembership.objects.create(user=user, sub=new_sub)

    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    
class SubDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    
    permission_classes = (IsModeratorOrAdminOrReadOnly,)
