from rest_framework import serializers
from django.utils.translation import gettext as _
from django.db import IntegrityError

from .models import Sub
from redditors.models import User, UserSubMembership

class SubSerializer(serializers.ModelSerializer):
    
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
        if value.lower() in Sub.pseudo_subreddits:
            message = "The subreddit title '{}' is reserved".format(value.title())
            raise serializers.ValidationError(message)
        return value
        
class SubredditSubscribeSerializer(serializers.ModelSerializer):
    
    action = serializers.CharField(write_only=True)
    sub = SubSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = UserSubMembership
        fields = ('pk', 'user', 'sub', 'action' )
        
    def validate_action(self, value):
        if value.lower() not in ["unsub", "sub"]:
            message = _("Action must be either 'sub' or 'unsub'.")
            raise serializers.ValidationError(message)
        return value
            
    def create(self, validated_data):
        action = validated_data["action"]
        user = self.context["request"].user
        subreddit_title = self.context["subreddit_title"]
        
        # make sure the user is authenticated
        if not user.is_authenticated:
            message=_(
                "You must be logged in to make a subreddit subscription."
            )
            raise serializers.ValidationError(message)

        # make sure the subreddit exists
        try:
            sub = Sub.objects.get(title=subreddit_title)
        except Sub.DoesNotExist:
            message=_(
                "The subreddit '{}' does not exist.".format(subreddit_title)
            )
            raise serializers.ValidationError(message)
            


        # try to subscribe
        if action == "sub":
            try:
                membership = self.Meta.model.objects.create(
                    user=user,
                    sub=sub
                )
                return membership
            except IntegrityError:
                message=_(
                    "You are already subscribed to '{}'".format(subreddit_title)
                )
                raise serializers.ValidationError(message)
            
        # try to unsubscribe
        elif action == "unsub":
            try:
                membership = self.Meta.model.objects.get(
                    user=user,
                    sub=sub
                )
            except self.Meta.model.DoesNotExist:
                message=_(
                    "You are not subscribed to the '{}'' subreddit.".format(
                        subreddit_title
                    )
                )
                raise serializers.ValidationError(message)
            membership.delete()
        # ugly fix to get around the neccessity of returning an instance
        # without rewriting .save()
        return True
            
        
