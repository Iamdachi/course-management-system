from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from courses.services.access import is_student, is_teacher, is_course_student, is_course_teacher, get_course_from_obj


class IsStudentAndEnrolled(permissions.BasePermission):
    """Only students enrolled in the course can submit homework."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        course = obj.homework.lecture.course
        return is_course_student(request.user, course)


class IsStudentOfCourseOrTeacherCanView(permissions.BasePermission):
    """
    - Students can create/update/delete submissions in their courses.
    - Teachers can only view submissions of their own courses.
    """

    def has_object_permission(self, request, view, obj):
        course = get_course_from_obj(obj)
        if is_teacher(request.user):
            return is_course_teacher(request.user, course)
        if is_student(request.user):
            return is_course_student(request.user, course)
        return False


class CanAccessSubmissions(permissions.BasePermission):
    """
    - GET: teachers or students of the course.
    - POST: only students of the course.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        homework = view.get_object()
        course = homework.lecture.course

        if request.method in SAFE_METHODS:
            return is_course_teacher(user, course) or is_course_student(user, course)

        if request.method == "POST":
            return is_course_student(user, course)

        return False
