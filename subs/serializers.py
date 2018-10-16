from rest_framework import serializers
from django.utils.translation import gettext as _

from .models import Sub
from redditors.models import User

class SubSerializer(serializers.HyperlinkedModelSerializer):
    
    moderators = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='user-detail',
        read_only=True,
        lookup_field='username'
    )
    
    members = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='user-detail',
        read_only=True,
        lookup_field='username'
    )
    
    class Meta:
        model = Sub
        fields = ('url', 'id', 'created', 'title', 'description',
                  'moderators', 'members')
        # extra_kwargs = {
        #     'members': {'lookup_field': 'username'}
        # }