from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from courses.services.access import is_teacher, is_course_teacher, get_course_from_obj


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Teachers can edit their own courses; everyone else can only read."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or is_teacher(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        course = get_course_from_obj(obj)
        return is_course_teacher(request.user, course)


class IsCourseTeacherOrReadOnly(permissions.BasePermission):
    """Teachers of the course can modify its lectures/homework. Others can only read."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        course = get_course_from_obj(obj)
        return is_course_teacher(request.user, course)
