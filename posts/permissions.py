from rest_framework import permissions

class IsPosterOrReadOnly(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user == obj.poster
    
# class IsMemberOfSub(permissions.BasePermission):
#     """
#     This is to be sure that the user creating the post
#     is a member of the sub that contains the incipeint post
#     """
#     def has_permission(self, request, view):
#         if request.sub in requests.user.subs