from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from comments.models import Comment
from .serializers import CommentVoteSerializer, PostVoteSerializer

class CreateVoteView(CreateAPIView):
    comment_serializer_class = CommentVoteSerializer
    post_serializer_class = PostVoteSerializer
    permission_classes = (IsAuthenticated,)
            
    def get_serializer(self, *args, **kwargs):
        """
        Depending on the full_name of the voted upon item
        (i.e. whether it's a comment or a post), use the right
        serializer
        
        Also update the request data
        """
        data = kwargs["data"].copy()
        fn = data["item_fn"]
        assert (fn and (fn[0:3] == "t1_" or fn[0:3] =='t2_')), (
            "item_fn is required and must be a 'full name', "
            "i.e. it must begin with either 't1_' or 't2_'"
        )
        if fn[0:3] == "t1_":
            data["comment"] = fn[3:]
            return self.comment_serializer_class(data=data)
        elif fn[0:3] == "t2_":
            data["post"] = fn[3:]
            return self.post_serializer_class(data=data)

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except AssertionError as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)
