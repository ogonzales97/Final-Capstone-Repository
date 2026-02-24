"""Permissions for the news API."""

from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    """Allows access only to journalists."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_journalist)


class IsEditor(permissions.BasePermission):
    """Allows access only to editors."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_editor)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Journalists can edit their own work; others can only read."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
