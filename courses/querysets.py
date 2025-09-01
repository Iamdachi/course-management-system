from django.db import models
from courses.models.roles import Role


class RoleFilteredQuerySet(models.QuerySet):
    """Base QuerySet to filter objects by user role."""

    def for_user(self, user, teacher_filter=None, student_filter=None):
        """Filter objects based on user role (teacher/student)."""
        if user.is_anonymous:
            return self.none()
        if user.role == Role.TEACHER:
            return self.filter(**teacher_filter) if teacher_filter else self.none()
        if user.role == Role.STUDENT:
            return self.filter(**student_filter) if student_filter else self.none()
        return self.none()


class CourseQuerySet(RoleFilteredQuerySet):
    """QuerySet for courses visible to a user."""

    def for_user(self, user):
        """Return courses a teacher teaches or a student is enrolled in."""
        return super().for_user(
            user,
            teacher_filter={"teachers": user},
            student_filter={"students": user},
        )


class UserFilteredQuerySet(RoleFilteredQuerySet):
    """Generic QuerySet for objects linked to courses via FK."""

    def for_user(self, user, teacher_filter=None, student_filter=None):
        """Filter objects based on course visibility and user role."""
        return super().for_user(user, teacher_filter, student_filter)


class LectureQuerySet(UserFilteredQuerySet):
    """QuerySet for lectures visible to a user."""

    def for_user(self, user):
        """Return lectures in courses visible to the user."""
        return super().for_user(
            user,
            teacher_filter={"course__teachers": user},
            student_filter={"course__students": user},
        )


class HomeworkQuerySet(UserFilteredQuerySet):
    """QuerySet for homeworks visible to a user."""

    def for_user(self, user):
        """Return homeworks in lectures visible to the user."""
        return super().for_user(
            user,
            teacher_filter={"lecture__course__teachers": user},
            student_filter={"lecture__course__students": user},
        )


class HomeworkSubmissionQuerySet(UserFilteredQuerySet):
    """QuerySet for homework submissions visible to a user."""

    def for_user(self, user):
        """Return submissions for courses or student-owned submissions."""
        return super().for_user(
            user,
            teacher_filter={"homework__lecture__course__teachers": user},
            student_filter={"student": user},
        )


class GradeQuerySet(UserFilteredQuerySet):
    """QuerySet for grades visible to a user."""

    def for_user(self, user):
        """Return grades in courses or grades of the student."""
        return super().for_user(
            user,
            teacher_filter={"submission__homework__lecture__course__teachers": user},
            student_filter={"submission__student": user},
        )


class GradeCommentQuerySet(UserFilteredQuerySet):
    """QuerySet for grade comments visible to a user."""

    def for_user(self, user):
        """Return grade comments in courses or on the student's grades."""
        return super().for_user(
            user,
            teacher_filter={"grade__submission__homework__lecture__course__teachers": user},
            student_filter={"grade__submission__student": user},
        )