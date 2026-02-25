"""Permissions for the news API."""

from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    """
    Permission class that allows access only to journalists.
    
    Checks if the authenticated user has the is_journalist flag
    set to True.
    
    :param request: The incoming HTTP request object
    :type request: rest_framework.request.Request
    :param view: The view being accessed
    :type view: rest_framework.views.APIView
    :return: True if user is a journalist, False otherwise
    :rtype: bool
    """

    def has_permission(self, request, view):
        """
        Check if the user is a journalist.
        
        :param request: The incoming HTTP request object
        :type request: rest_framework.request.Request
        :param view: The view being accessed
        :type view: rest_framework.views.APIView
        :return: True if user is authenticated and is a journalist
        :rtype: bool
        """
        return bool(request.user and request.user.is_journalist)


class IsEditor(permissions.BasePermission):
    """
    Permission class that allows access only to editors.
    
    Checks if the authenticated user has the is_editor flag set to
    True.
    
    :param request: The incoming HTTP request object
    :type request: rest_framework.request.Request
    :param view: The view being accessed
    :type view: rest_framework.views.APIView
    :return: True if user is an editor, False otherwise
    :rtype: bool
    """

    def has_permission(self, request, view):
        """
        Check if the user is an editor.
        
        :param request: The incoming HTTP request object
        :type request: rest_framework.request.Request
        :param view: The view being accessed
        :type view: rest_framework.views.APIView
        :return: True if user is authenticated and is an editor
        :rtype: bool
        """
        return bool(request.user and request.user.is_editor)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission class for object-level access control.
    
    Allows read-only access to everyone (GET, HEAD, OPTIONS requests).
    Write access (PUT, PATCH, DELETE) is restricted to the
    article author.
    
    :param request: The incoming HTTP request object
    :type request: rest_framework.request.Request
    :param view: The view being accessed
    :type view: rest_framework.views.APIView
    :param obj: The object being accessed
    :type obj: news_api.models.Article
    :return: True if user has permission, False otherwise
    :rtype: bool
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user can access the specific object.
        
        Safe methods (GET, HEAD, OPTIONS) are allowed for everyone.
        Write methods require the user to be the article author.
        
        :param request: The incoming HTTP request object
        :type request: rest_framework.request.Request
        :param view: The view being accessed
        :type view: rest_framework.views.APIView
        :param obj: The article object being accessed
        :type obj: news_api.models.Article
        :return: True if read-only or user is the author
        :rtype: bool
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
