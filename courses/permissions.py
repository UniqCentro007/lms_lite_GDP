from rest_framework import permissions


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Permission to allow instructors to create/edit courses,
    but allow read access to all authenticated users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_instructor


class IsCourseInstructor(permissions.BasePermission):
    """
    Permission to allow only the course instructor to edit.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.instructor == request.user or request.user.is_admin




