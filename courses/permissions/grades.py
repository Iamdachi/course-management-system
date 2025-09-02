from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from courses.services.access import is_teacher, is_student, is_course_teacher, get_course_from_obj


class IsTeacherOfCourse(permissions.BasePermission):
    """Only teachers of the course can grade."""

    def has_permission(self, request, view):
        return is_teacher(request.user)

    def has_object_permission(self, request, view, obj):
        course = obj.submission.homework.lecture.course
        return is_course_teacher(request.user, course)


class IsGradeOwnerOrCourseTeacher(permissions.BasePermission):
    """Students can only see their own grades; teachers manage their course grades."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        course = get_course_from_obj(obj)

        if request.method in SAFE_METHODS:
            if is_student(user):
                return obj.submission.student == user
            if is_teacher(user):
                return is_course_teacher(user, course)
            return False

        return is_teacher(user) and is_course_teacher(user, course)


class CanGradeCourse(permissions.BasePermission):
    """Only teachers of the submission's course can POST grades."""

    def has_object_permission(self, request, view, obj):
        course = obj.homework.lecture.course
        return is_course_teacher(request.user, course)


class CanCommentOnGrade(permissions.BasePermission):
    """
    - Teachers of the course can comment on student grades.
    - Students can comment on their own grades.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        course = obj.grade.submission.homework.lecture.course

        if is_teacher(user):
            return is_course_teacher(user, course)

        if is_student(user):
            return obj.grade.submission.student == user

        return False
