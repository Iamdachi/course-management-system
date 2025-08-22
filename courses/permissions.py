# permissions.py
from rest_framework import permissions

from courses.roles import Role


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


class IsStudentAndEnrolled(permissions.BasePermission):
    """Only students enrolled in the course can submit homework."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if user.role != "student":
            return False
        # object here is HomeworkSubmission
        return obj.homework.lecture.course.students.filter(id=user.id).exists()

class IsTeacherOfCourse(permissions.BasePermission):
    """Only teachers of the course can grade."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.TEACHER

    def has_object_permission(self, request, view, obj):
        return obj.submission.homework.lecture.course.teachers.filter(id=request.user.id).exists()


class IsGradeOwnerOrCourseTeacher(permissions.BasePermission):
    """
    Students can only see their own grades.
    Teachers can manage grades for submissions in their courses.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Read-only case
        if request.method in permissions.SAFE_METHODS:
            if user.role == Role.STUDENT:
                return obj.submission.student == user
            if user.role == Role.TEACHER:
                return user in obj.submission.homework.lecture.course.teachers.all()
            return False

        # Write/update/delete case
        if user.role == Role.TEACHER:
            return user in obj.submission.homework.lecture.course.teachers.all()

        return False


class IsStudentOfCourseOrTeacherCanView(permissions.BasePermission):
    """
    - Students can create/update/delete submissions, but only for homeworks
      in courses they are enrolled in.
    - Teachers can only view submissions of their own courses.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == Role.TEACHER:
            # Teacher can view only if they teach this course
            return user in obj.lecture.course.teachers.all()

        # Student can act only if enrolled in the course
        return user in obj.lecture.course.students.all()
