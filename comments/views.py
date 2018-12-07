from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict

from .models import Comment
from .serializers import CommentSerializer, CommentTreeSerializer


class CommentListView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostCommentView(RetrieveAPIView):
    """
    For a particular post returns all comments, paginated and in a nested,
    hierarchichal fashion.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    
    def retrieve(self, request, *args, **kwargs):
        root = self.get_object()
        children = defaultdict(list)
        for comment in root.get_descendants():
            children[comment.parent_id].append(comment)
            
        context = self.get_serializer_context()
        context['children'] = children
        serializer = self.get_serializer_class()(root, context=context)
        print(context)
        return Response(serializer.data)
        
    
