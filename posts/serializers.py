from rest_framework import serializers

from .models import Post
from redditors.models import User
from subs.models import Sub

class PostSerializer(serializers.HyperlinkedModelSerializer):
    
    poster = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        #queryset=User.objects.all(),
        read_only=True,
        lookup_field='username'
    )
    
    sub = serializers.HyperlinkedRelatedField(
        view_name='sub-detail',
        queryset=Sub.objects.all()
    )
    
    class Meta:
        model = Post
        fields = ('url', 'id', 'created', 'updated', 'title', 'body',
                    'upvotes', 'sub', 'poster')
                    
                    
    def validate(self, data):
        """
        Ensure that the use is a member of the sub
        being posted to
        """
        user = None
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
        
        if not data['sub'] in user.subs.all():
            raise serializers.ValidationError(
                "You must be a member of the subreddit to post here."
            )            
            
        return data