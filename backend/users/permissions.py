from rest_framework import permissions


class UserDetailPermission(permissions.AllowAny):
    """Url 'users/me/' allowed for authorized users and admin.
    Also, only get method allowed."""
    def has_permission(self, request, view):
        if (('me' in request.path and request.user.is_anonymous)
                or (request.method not in permissions.SAFE_METHODS)):
            return False

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if (('me' in request.path and request.user.is_anonymous)
                or (request.method not in permissions.SAFE_METHODS)):
            return False

        return super().has_object_permission(request, view, obj)


class PermissionDenied(permissions.BasePermission):
    """Permission for djoser provided 'user_delete' possibility."""
    def has_object_permission(self, request, view, obj):
        return False

    def has_permission(self, request, view):
        return False


class AnonOrAdmin(permissions.BasePermission):
    """Create new user can only anonymous and admin."""
    def has_permission(self, request, view):
        return request.user.is_anonymous or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_anonymous or request.user.is_staff
