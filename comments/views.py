from rest_framework.generics import (
    ListCreateAPIView, ListAPIView, CreateAPIView, UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from collections import defaultdict
from django.utils import timezone

from .models import Comment
from .serializers import (
    CommentSerializer, CommentTreeSerializer, DeleteCommentSerializer,
)
from redditors.models import User

class CommentListView(ListCreateAPIView):
    """
    Standard list and create view for comments. The user must
    be authenticated to post/create a comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def perform_create(self, serializer):
        """
        You need to be authenticated to post a comment.
        Take that authenticated user and make them the poster
        """
        serializer.save(poster=self.request.user)
        

class PostCommentView(ListAPIView):
    """
    For a particular post returns all comments, paginated and in a nested,
    hierarchichal fashion.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    
    def get_sort_function(self):
        """
        Given an api sort description (e.g. 'popular' or 'new') return
        a key function that can be used in sort based on the acutal
        model attributes nomenclature.
        """
        sort_functions = {
            'popular': (lambda comment: -comment.upvotes),
            'new' : (lambda comment: (timezone.now() - comment.created)),
        }
        api_sort_key = self.request.query_params.get('orderby', 'popular')
        return sort_functions.get(api_sort_key, sort_functions['popular'])
    
    def get_queryset(self):
        """
        Narrows queryset to root comments on this post. Also
        orders depending on get parameter, default to popular.
        """
        post_pk = self.kwargs.get('post_pk', None)
        queryset = Comment.objects.filter(
            post__pk=post_pk,
            parent=None
        )
        # Can't use .order_by() in get_queryset because upvotes is not a db field
        # so wait until now to sort since we have a list
        # can't use inplace .sort either
        queryset = sorted(queryset,key=self.get_sort_function())
        return queryset
    
    def get_serializer_context(self):
        """
        It will really speed up some vote lookups in the
        serializer if we can turn a username into a user_pk at this point.
        This is only relevant if the consumer provides a get param 'username'
        """
        context = super().get_serializer_context()
        username = self.request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return context
            context['comment_user_pk'] = user.pk
        return context
        
    
    def list(self, request, *args, **kwargs):
        root_comments = self.filter_queryset(self.get_queryset())
        comment_trees = []
        for root in root_comments:
            comment_trees.append(self.make_tree(root))
        return Response(comment_trees)
            
    def make_tree(self, root):
        children = defaultdict(list)
        for comment in root.get_descendants():
            children[comment.parent_id].append(comment)
            
        # For every parent, order the children according to the get parameter
        for child_list in children.values():
            child_list.sort(key=self.get_sort_function())
        
        context = self.get_serializer_context()
        context['children'] = children
        serializer = self.get_serializer_class()(root, context=context)
        return serializer.data
        
class DeleteCommentView(UpdateAPIView):
    '''
    The comment is not really deleted. Just as in
    reddit we overwrite the content and remove
    the reference to the poster. Votes, voters, and
    it's creation date are preserved.
    '''
    serializer_class = DeleteCommentSerializer
    queryset = Comment.objects.all()
    
