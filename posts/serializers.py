from rest_framework import serializers
from django.utils.timezone import now

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
        queryset=Sub.objects.all(),
        lookup_field='title'
    )
    
    subreddit_title = serializers.SerializerMethodField()
    poster_username = serializers.SerializerMethodField()
    age_in_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('url', 'pk', 'created', 'updated', 'title', 'body',
                  'upvotes', 'sub', 'poster', 'subreddit_title',
                  'poster_username', 'age_in_days')
                    
                    
    def validate(self, data):
        """
        Ensure that the user is a member of the sub
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
    
    def get_subreddit_title(self, obj):
        return obj.sub.title
    
    def get_poster_username(self, obj):
        return obj.poster.username

    def get_age_in_days(self, obj):
        return (now() - obj.created).days
