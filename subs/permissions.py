from rest_framework import permissions

class IsModeratorOrAdminOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        admin = request.user.is_staff
        mod = request.user in obj.moderators.all()
        return admin or mod