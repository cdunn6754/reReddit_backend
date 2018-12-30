from rest_framework import permissions
import re

class IsPosterOrModOrAdminOrReadOnly(permissions.BasePermission):
    """
    Only the poster, moderators of this sub, or admins can edit/delete a post
    """
    message = ("You can only modify this post if you are the poster, " +
            "a moderator of this subReddit, or an admin.")
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user = request.user
        post_sub_moderators = obj.subreddit.moderators.all()
        
        print(user)
        print(obj.poster)

        is_poster = True if user == obj.poster else False
        mod = True if user in post_sub_moderators else False
        admin = True if user.is_staff else False
        
        
        return is_poster or admin or mod
        
