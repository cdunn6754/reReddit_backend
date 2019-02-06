from rest_framework import serializers, exceptions
from collections import defaultdict
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import gettext as _

from .models import Comment
from redditors.models import User
from redditors.serializers import UserSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from votes.models import CommentVote

class CommentSerializer(serializers.ModelSerializer):
    
    post = PostSerializer(
        read_only=True
    )
    poster = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )
    parent = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True
    )
    parent_fn = serializers.CharField(
        write_only=True
    )
    vote_state = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = (
            'post', 'poster', 'parent', 'body', 'upvotes',
            'parent_fn', 'pk', 'vote_state', 'deleted', 'created',
        )
    
    def validate_parent_fn(self, value):
        """
        the parent_id must begin with 'tx_' where x is either
        1 or 2 to indicate that the comment was made on another
        comment or a post, respectively. Follows the idea from
        the reddit api.
        """
        # TODO get a regex
        if not (value.startswith("t") and value[2] == "_"):
            raise serializers.ValidationError(
                _(("parent_fn must be a 'full name' "
                "and begin with either 't1_' or 't2_'"))
            )
        return value
    
    def get_vote_state(self, obj):
        return 0
        
    def get_created(self, obj):
        return naturaltime(obj.created)
    
    def create(self, validated_data):
        
        parent_fn = validated_data.pop('parent_fn')
        parent_pk = parent_fn[3:]
        
        # If this is a child comment, add the parent comment
        if int(parent_fn[1]) == 1:
            try:
                validated_data['parent'] = Comment.objects.get(pk=parent_pk)
            except Comment.DoesNotExist:
                error_message = _((
                    "The comment you are replying to is no "
                    "longer available"
                ))
                raise exceptions.NotFound(detail=error_message)
            # The child's post is the same as the parent's
            try:
                validated_data['post'] = Post.objects.get(
                    pk=validated_data['parent'].post_id
                )
            except Post.DoesNotExist:
                error_message = _((
                    "The post you are replying to is no "
                    "longer available"
                ))
                raise exceptions.NotFound(detail=error_message)
        elif int(parent_fn[1]) == 2:
            try:
                validated_data['post'] = Post.objects.get(pk=parent_pk)
            except Post.DoesNotExist:
                error_message = _((
                    "The post you are replying to is no "
                    "longer available"
                ))
                raise exceptions.NotFound(detail=error_message)
        return super().create(validated_data)
    
    def reddit_delete(self):
        """
        The comment is not really deleted. Just as in
        reddit we overwrite the content and remove
        the reference to the poster. Votes, voters, and
        its creation date are preserved.
        """
        instance = self.instance
        poster = getattr(instance, 'poster')
        setattr(instance, 'poster', None)
        setattr(instance, 'body', 'deleted')
        setattr(instance, 'deleted', True)
        instance.save()
        
        return instance

class CommentPosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'karma')
    
class CommentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    poster = CommentPosterSerializer()
    created = serializers.SerializerMethodField()
    vote_state = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = Comment
        fields= (
            'post', 'body', 'upvotes', 'parent',
            'created', 'vote_state', 'deleted', 'pk', 'poster', 'children',
        )
    
    def get_children(self, obj):
        children = self.context['children'].get(obj.pk, [])
        serializer = self.__class__(
            children,
            context=self.context,
            many=True,
        )
        return serializer.data
    
    def get_created(self, obj):
        return naturaltime(obj.created)
    
    def get_vote_state(self, obj):
        """
        If a user is authenticated, look up whether they have voted on this
        comment before.
        """
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            try:
                vote = obj.votes.all().get(user_id=request.user.pk)
                return vote.vote_type
            except CommentVote.DoesNotExist:
                pass
        return 0
        
