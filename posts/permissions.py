from rest_framework import permissions

class IsPosterOrReadOnly(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user == obj.poster
    
# class IsMemberOfSub(permissions.BasePermission):
#     def