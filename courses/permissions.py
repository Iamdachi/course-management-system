from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from courses.models.roles import Role


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Teachers can edit their own courses; everyone else can only read."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == "teacher"

    def has_object_permission(self, request, view, obj):
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
        return obj.homework.lecture.course.students.filter(id=user.id).exists()


class IsTeacherOfCourse(permissions.BasePermission):
    """Only teachers of the course can grade."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.TEACHER

    def has_object_permission(self, request, view, obj):
        return obj.submission.homework.lecture.course.teachers.filter(
            id=request.user.id
        ).exists()


class IsGradeOwnerOrCourseTeacher(permissions.BasePermission):
    """
    Students can only see their own grades.
    Teachers can manage grades for submissions in their courses.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def _is_teacher_of(self, user, obj):
        return user in obj.submission.homework.lecture.course.teachers.all()

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            if user.role == Role.STUDENT:
                return obj.submission.student == user
            if user.role == Role.TEACHER:
                return self._is_teacher_of(user, obj)
            return False

        if user.role == Role.TEACHER:
            return self._is_teacher_of(user, obj)

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
            return user in obj.lecture.course.teachers.all()

        return user in obj.lecture.course.students.all()


class CanAccessSubmissions(permissions.BasePermission):
    """
    - GET: teachers of the course OR students enrolled in the course.
    - POST: only students enrolled in the course.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        homework = view.get_object()
        course = homework.lecture.course

        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            if user.role == Role.TEACHER:
                return course.teachers.filter(id=user.id).exists()
            if user.role == Role.STUDENT:
                return course.students.filter(id=user.id).exists()
            return False

        if request.method == "POST":
            return (
                user.role == Role.STUDENT
                and course.students.filter(id=user.id).exists()
            )

        return False


class CanGradeCourse(permissions.BasePermission):
    """Only teachers of the submission's course can POST grades."""

    def has_object_permission(self, request, view, obj):
        if request.user.role != Role.TEACHER:
            return False
        return obj.homework.lecture.course.teachers.filter(id=request.user.id).exists()


class CanCommentOnGrade(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == Role.TEACHER and obj.grade.submission.homework.lecture.course.teachers.filter(id=user.id).exists():
            return True

        if user.role == Role.STUDENT and obj.grade.submission.student == user:
            return True

        return False



class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allow access if the requesting user is the object itself or is staff.
    """

    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_staff or obj == request.user)
