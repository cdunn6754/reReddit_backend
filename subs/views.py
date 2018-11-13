from rest_framework import generics, status
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response


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
    lookup_field = 'title'
    
    permission_classes = (IsModeratorOrAdminOrReadOnly,)
    
class SubSubscribeView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    
    def post(self, request, format=None, **kwargs):
        '''
        Users can subscribe or unsubscribe from here
        If they try to unsubscribe from a subreddit to which
        they are not subscibed in the first place or 
        a subreddit that doesnt exist respond with 404
        '''
        action = request.data['action']
        user = request.user
        title = kwargs['title']
        try: 
            sub = Sub.objects.get(title=title)
        except (Sub.DoesNotExist, Sub.MultipleObjectsReturned) as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if action == 'sub':
            UserSubMembership.objects.get_or_create(user=user, sub=sub)
            return Response(status=status.HTTP_201_CREATED)
        
        elif action == 'unsub':
            membership = UserSubMembership.objects.filter(user=user, sub=sub)
            if not membership:
                return Response(status=status.HTTP_404_NOT_FOUND)
            membership.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)