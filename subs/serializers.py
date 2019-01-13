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
