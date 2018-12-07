from rest_framework import serializers
from collections import defaultdict

from .models import Comment
from redditors.models import User
from posts.models import Post

class CommentSerializer(serializers.ModelSerializer):
    
    post = serializers.SlugRelatedField(
        slug_field='title',
        queryset = Post.objects.all()
    )
    poster = serializers.SlugRelatedField(
        slug_field='username',
        queryset = User.objects.all()
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        allow_null=True
    )
    
    class Meta:
        model = Comment
        fields = ('poster', 'post', 'body', 'upvotes', 'parent', 'pk')
        
    def validate(self, data):
        """
        The parent and the child (self) need to be made on the same post
        """
        if not data['post'] == data['parent'].post:
            raise serializers.ValidationError("The parent comment must be " +
                "made on the same post."
            )
        return data
    
class CommentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields= ('poster', 'post', 'body', 'upvotes', 'parent', 'children',)
    
    def get_children(self, obj):
        children = self.context['children'].get(obj.pk, [])
        serializer = self.__class__(
            children,
            context=self.context,
            many=True,
        )
        return serializer.data
        
        
