# permissions.py
from rest_framework import permissions

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Teachers can edit their own courses; everyone else can only read.
    """

    def has_permission(self, request, view):
        # can I access this view?
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'teacher'

    def has_object_permission(self, request, view, obj):
        # can I act on this specific object?
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in obj.teachers.all()


class IsCourseTeacherOrReadOnly(permissions.BasePermission):
    """
    Teachers of the course can modify its lectures/homework.
    Others can only read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        course = getattr(obj, "course", None) or obj.lecture.course
        return request.user in course.teachers.all()

class IsOwnerTeacher(permissions.BasePermission):
    """Only teachers of the course can modify. Everyone can read."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True  # anyone can read

        user = request.user
        if not user.is_authenticated or user.role != "teacher":
            return False

        # obj can be Lecture or Homework
        if hasattr(obj, "course"):
            return obj.course.teachers.filter(id=user.id).exists()
        if hasattr(obj, "lecture"):
            return obj.lecture.course.teachers.filter(id=user.id).exists()
        return False