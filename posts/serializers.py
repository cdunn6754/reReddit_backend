from rest_framework import serializers

from .models import Post
from redditors.models import User
from subs.models import Sub

class PostSerializer(serializers.HyperlinkedModelSerializer):
    
    poster = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        #queryset=User.objects.all(),
        read_only=True
    )
    
    sub = serializers.HyperlinkedRelatedField(
        view_name='sub-detail',
        queryset=Sub.objects.all()
    )
    
    class Meta:
        model = Post
        fields = ('url', 'id', 'created', 'updated', 'title', 'body',
                    'upvotes', 'sub', 'poster',)