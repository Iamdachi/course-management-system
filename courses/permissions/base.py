from rest_framework import permissions

class IsSelfOrAdmin(permissions.BasePermission):
    """Allow access if the requesting user is the object itself or is staff."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and (user.is_staff or obj == user)
