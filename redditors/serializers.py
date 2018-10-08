from rest_framework import serializers

from .models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    subs = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='sub-detail',
        read_only=True
    )
    
    moderated_subs = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='sub-detail',
        read_only=True
    )
    
    class Meta:
        model = User
        fields = ('url', 'id', 'karma', 'username', 'subs', 'moderated_subs',)