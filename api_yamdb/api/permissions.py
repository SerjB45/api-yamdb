from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.role == 'admin'
                or user.is_superuser
            )
        )


class IsAdminOrReadyOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin)
        )
