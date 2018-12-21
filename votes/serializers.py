from rest_framework import serializers

from .models import CommentVote, PostVote
from comments.models import Comment, Post

class VoteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            defaults = {'vote_type': validated_data.pop('vote_type')}
        except KeyError:
            raise exceptions.ValidationError("vote_type is a required field")
        instance, _ = CommentVote.objects.update_or_create(
            **validated_data,
            defaults=defaults
        )
        return instance

class CommentVoteSerializer(VoteSerializer):
    comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all()
    )
    
    class Meta:
        model = CommentVote
        fields = (
            'vote_type', 'comment',
        )

class PostVoteSerializer(VoteSerializer):
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all()
    )

    class Meta:
        model = PostVote
        fields = (
            'vote_type', 'post',
        )
