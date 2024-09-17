from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Изменение чужого контента запрещено!'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsModerOnly(permissions.BasePermission):
    message = 'Staff only'

    def has_permission(self, request, view):
        if request.user.is_moder or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_moder or request.user.is_superuser:
            return True
        return False


class IsAuthorOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
