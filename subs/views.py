from rest_framework import generics, status
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


from .permissions import IsModeratorOrAdminOrReadOnly
from .models import Sub
from .serializers import SubSerializer, SubredditSubscribeSerializer
from redditors.models import UserSubMembership
from posts.models import Post


class SubListView(generics.ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def perform_create(self, serializer):
        """
        Whomever creates this sub will be the sole inital moderator.
        Also make them a sub member.
        """
        user = self.request.user
        new_sub = serializer.save()
        new_sub.moderators.add(user)
        UserSubMembership.objects.create(user=user, sub=new_sub)
    
    
class SubDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class = SubSerializer
    lookup_field = 'title'
    permission_classes = (IsModeratorOrAdminOrReadOnly,)
    
    def get(self, request, *args, **kwargs):
        """
        Need to filter out requests to the pseudo-subreddits like
        'popular', 'all' and 'home'.
        """
        subreddit_title = kwargs['title']
        if subreddit_title.lower() in Sub.pseudo_subreddits:
            data = {
                'title': subreddit_title.title(),
                'description': Sub.pseudo_subreddits.get(subreddit_title.lower()),
            }
            return Response(data)
        else:
            return super().get(request, *args, **kwargs)
    
    
class SubredditSubscribeView(generics.CreateAPIView):
        '''
        Users can subscribe or unsubscribe from here
        If they try to unsubscribe from a subreddit to which
        they are not subscibed in the first place or
        a subreddit that doesnt exist respond with 404.
        Resubscribing to a subreddit that they are already
        subscribed to does nothing and returns no error.
        '''
        serializer_class=SubredditSubscribeSerializer
        
        def get_serializer_context(self):
            context = super().get_serializer_context()
            context["subreddit_title"] = self.kwargs["title"]
            return context

        def create(self, request, *args, **kwargs):
            '''
            Need to customize since we are abusing the
            'create' funcitonality in the serializer.
            Don't want to send a 201 when we delete a subscription.
            '''
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            if serializer.validated_data["action"] == "unsub":
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
