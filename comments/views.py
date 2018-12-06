from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import Comment
from .serializers import CreateCommentSerializer


class CommentCreateView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
