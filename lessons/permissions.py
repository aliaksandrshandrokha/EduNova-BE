from rest_framework import permissions


class IsLessonOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a lesson to view/edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for public lessons or owners
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsLessonOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read access to public lessons,
    but write access only to lesson owners.
    """

    def has_permission(self, request, view):
        # Allow authenticated users to create lessons
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions for public lessons or owners
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        
        # Write permissions only for owners
        return obj.user == request.user

