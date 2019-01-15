from rest_framework import serializers
from django.utils.translation import gettext as _

from .models import Sub
from redditors.models import User

class SubSerializer(serializers.HyperlinkedModelSerializer):
    
    moderators = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    
    class Meta:
        model = Sub
        fields = ('pk', 'created', 'title', 'description',
                  'moderators', 'members')
                  
    def validate_title(self, value):
        """
        Prevent title collisions with those of the psuedo subreddits
        """
        if value.title in Sub.protected_subreddit_titles:
            message = "The subreddit title '{}' is reserved".format(value)
            raise serializers.ValidationError(message)
