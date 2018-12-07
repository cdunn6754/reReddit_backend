from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict

from .models import Comment
from .serializers import CommentSerializer, CommentTreeSerializer
from utilities.reddit_orderby import ordering


class CommentListView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostCommentView(ListAPIView):
    """
    For a particular post returns all comments, paginated and in a nested,
    hierarchichal fashion.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    tree_serializer_class = CommentTreeSerializer
    def get_queryset(self):
        """
        Narrows queryset to root comments on this post. Also
        orders depending on get parameter, default to popular.
        """
        post_title = self.kwargs.get('post_title', "Bobby Post Title")
        order_by = ordering.get(
            self.request.query_params.get('orderby', 'popular')
        )
        
        return Comment.objects.filter(
            post__title=post_title,
            parent=None
        ).order_by('-upvotes')
    
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
            child_list.sort(key=lambda child: -child.upvotes)
        
        context = self.get_serializer_context()
        context['children'] = children
        serializer = self.get_serializer_class()(root, context=context)
        return serializer.data
        
    
