from rest_framework import permissions


class IsAuthorOrReadOnlyPermissions(permissions.BasePermission):
    """
    Кастомный класс для проверки разрешений.
    Дает доступ всем пользователям, если метод запроса является безопасным.
    Доступ на измениение и удаление дается только аутентифицированным
    пользователям и авторам своего контента.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnlyPermissions(permissions.BasePermission):
    """
    Кастомный класс для проверки разрешений.
    Дает доступ всем пользователям, если метод запроса является безопасным.
    Доступ на измениение и удаление дается только адимину.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user.is_staff
