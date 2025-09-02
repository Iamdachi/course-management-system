from django.db import models
from courses.services.access import is_teacher, is_student
from courses.services.filters import filters_for_course, filters_for_lecture, filters_for_homework, \
    filters_for_submission, filters_for_grade, filters_for_comment


class RoleFilteredQuerySet(models.QuerySet):
    """
    Base QuerySet to filter objects by user role.

    - Teachers see only objects they own/teach.
    - Students see only objects linked to their enrollments.
    - Anonymous users see nothing.
    """

    def for_user(self, user, teacher_filter=None, student_filter=None):
        if not user.is_authenticated:
            return self.none()
        if is_teacher(user):
            return self.filter(**teacher_filter) if teacher_filter else self.none()
        if is_student(user):
            return self.filter(**student_filter) if student_filter else self.none()
        return self.none()


class CourseQuerySet(RoleFilteredQuerySet):
    """ Teachers see courses they teach. Students see courses they are enrolled in."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_course(user))


class UserFilteredQuerySet(RoleFilteredQuerySet):
    """ Generic QuerySet for objects linked to courses via FK."""

    def for_user(self, user, teacher_filter=None, student_filter=None):
        return super().for_user(user, teacher_filter, student_filter)


class LectureQuerySet(UserFilteredQuerySet):
    """ Teachers see lectures in their own courses. Students see lectures in enrolled courses."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_lecture(user))


class HomeworkQuerySet(UserFilteredQuerySet):
    """ Teachers see homeworks in their own courses. Students see homeworks in enrolled courses."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_homework(user))


class HomeworkSubmissionQuerySet(UserFilteredQuerySet):
    """ Teachers see submissions in their own courses. Students see only their own submissions."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_submission(user))


class GradeQuerySet(UserFilteredQuerySet):
    """ Teachers see grades in their own courses. Students see only their own grades."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_grade(user))


class GradeCommentQuerySet(UserFilteredQuerySet):
    """ Teachers see comments on grades in their own courses. Students see comments only on their own grades."""

    def for_user(self, user):
        return super().for_user(user, *filters_for_comment(user))
