from rest_framework import serializers
from django.utils.timezone import now
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Post
from redditors.models import User
from subs.models import Sub

class PostSerializer(serializers.ModelSerializer):
    
    poster = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )
    
    subreddit = serializers.PrimaryKeyRelatedField(
        queryset=Sub.objects.all(),
    )
    
    subreddit_title = serializers.SerializerMethodField()
    poster_username = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    vote_state = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('pk', 'created', 'updated', 'title', 'body',
                  'upvotes', 'subreddit', 'poster', 'subreddit_title',
                  'poster_username', 'vote_state')
                    
                    
    # def validate(self, data):
    #     """
    #     Ensure that the user is a member of the sub
    #     being posted to
    #     """
    #     user = None
    #     request = self.context.get('request')
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #
    #     for i in data:
    #         print("dict: {}".format(i))
    #     exit()
    #     if data.get('sub') and not data['sub'] in user.subs.all():
    #         raise serializers.ValidationError(
    #             "You must be a member of the subreddit to post here."
    #         )
    #
    #     return data
    
    def get_subreddit_title(self, obj):
        return obj.subreddit.title
    
    def get_poster_username(self, obj):
        return obj.poster.username

    def get_created(self, obj):
        return naturaltime(obj.created)

    def get_updated(self, obj):
        return naturaltime(obj.updated)

    def get_vote_state(self, obj):
        try:
            vote = obj.votes.all().get(user_id=self.context['post_user_pk'])
            return vote.vote_type
        except:
            return 0
