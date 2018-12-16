from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from comments.models import Comment
from .serializers import CommentVoteSerializer

class CreateCommentVoteView(CreateAPIView):
    serializer_class = CommentVoteSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
