from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to allow only superadmins to add or modify sports and positions.
    """

    def has_permission(self, request, view):
        # Only allow superadmins to create or modify
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return request.user.is_authenticated and request.user.is_superuser
        return True  # Allow anyone to view sports and positions