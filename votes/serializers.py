from rest_framework import serializers

from .models import CommentVote
from comments.models import Comment

class CommentVoteSerializer(serializers.ModelSerializer):
    comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all()
    )
    
    class Meta:
        model = CommentVote
        fields = (
            'vote_type', 'comment',
        )
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
    
class PostVoteSerializer(serializers.ModelSerializer):
    pass
