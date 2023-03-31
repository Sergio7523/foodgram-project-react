from rest_framework import permissions


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Неавторизованным пользователям разрешён только просмотр.
    Полный доступ для владельца или администратора.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author.id == request.user.id
            or request.user.is_staff
        )
