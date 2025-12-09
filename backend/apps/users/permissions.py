from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    检查用户角色是否为管理员
    """
    def has_permission(self, request, view):
        try:
            return (
                request.user and
                request.user.is_authenticated and
                hasattr(request.user, 'role') and
                request.user.role == 'admin'
            )
        except (AttributeError, TypeError):
            return False

