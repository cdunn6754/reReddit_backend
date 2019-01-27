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
    serializer_class = SubSerializer
    lookup_field = 'title'
    permission_classes = (IsModeratorOrAdminOrReadOnly,)
    
    def get(self, request, *args, **kwargs):
        """
        Need to filter out requests to the pseudo-subreddits like
        'popular', 'all' and 'home'.
        """
        subreddit_title = kwargs['title']
        print(subreddit_title)
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
        
class SubPostView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names=['post']

    def post(self, request, format=None, **kwargs):
        '''
        Allow users to post to this subreddit. Users must be
        authenticated and need to be a member of the subreddit to post.
        '''
        user = request.user
        sub_title = kwargs['title']

        try:
            sub = Sub.objects.get(title=sub_title)
        except Sub.DoesNotExist:
            data = {"detail": "That subreddit does not exist."}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
        
        # Check on user membership
        membership = UserSubMembership.objects.filter(user=user, sub=sub)
        if not membership:
            data_message = ("You are not subscribed to this subreddit.")
            data = {"detail": data_message}
            return Response(status=status.HTTP_403_FORBIDDEN, data=data)
        
        # If it all has worked out then create the post
        post_data = {'title': request.data['title'],
                     'body': request.data['body'],
                     'subreddit': sub,
                     'poster': user}
        Post.objects.create(**post_data)
        
        return Response(status=status.HTTP_201_CREATED)
