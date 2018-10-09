from rest_framework import serializers
from django.utils.translation import gettext as _

from .models import Sub
from redditors.models import User

class SubSerializer(serializers.HyperlinkedModelSerializer):
    
    moderators = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='user-detail',
        queryset=User.objects.all()
    )
    
    members = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='user-detail',
        queryset=User.objects.all()
    )
    
    class Meta:
        model = Sub
        fields = ('url', 'id', 'created', 'title', 'description',
            'moderators', 'members')
            
    def to_internal_value(self, data):
        """
        Ensures that a moderator also becomes a member
        """
        incoming = super().to_internal_value(data)
        moderators = incoming['moderators']
        members = incoming['members']
        for moderator in moderators:
            if not moderator in members:
                members.append(moderator)
        return incoming
            
            
    def validate_moderators(self, moderators):
        """
        Make sure they include at lease one moderator
        """
        if not len(moderators) :
            raise serializers.ValidationError(
                    _("At least one moderator must be set")
            )
        return moderators
    
    