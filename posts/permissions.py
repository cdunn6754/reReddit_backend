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
        post_sub_moderators = obj.sub.moderators.all()
        
        mod = (True if user in post_sub_moderators else False)
        admin = (True if user.is_staff else False)
        
        
        return (request.user == obj.poster) or admin or mod
    
class IsMemberOfSubOrReadOnly(permissions.BasePermission):
    """
    This ensures that the user creating the post
    is a member of the sub that contains the incipient post
    """
    message = "You must be a member of this subReddit to create a post here."
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        elif request.data:
            # prevent creation unless user is member of the sub
            post_sub_pk = get_pk_from_link(request.data['sub'])
            user = request.user
            user_sub_pks = [sub.pk for sub in user.subs.all()]
            if not (post_sub_pk in user_sub_pks):
                return False
                    
        return True

def get_pk_from_link(url):
    """
    Cut out and return the pk at the end of 
    a hyperlink url from a hyperlinkedrelated field
    """
    return int(re.search('[^/]+(?=/$|$)', url).group(0))
        