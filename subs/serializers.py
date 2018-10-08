from rest_framework import serializers

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