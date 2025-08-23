from django.db import models

from .roles import Role


class CourseQuerySet(models.QuerySet):
    """ Return courses visible to the given user. """
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        if user.role == "teacher":
            return self.filter(teachers=user)

        if user.role == "student":
            return self.filter(students=user)

        return self.none()


class UserFilteredQuerySet(models.QuerySet):
    """ Return courses visible to the given user through a FK (Lecture->Course). """
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        if user.role == "teacher":
            return self.filter(course__teachers=user)

        if user.role == "student":
            return self.filter(course__students=user)

        return self.none()


class LectureQuerySet(UserFilteredQuerySet):
    pass


class HomeworkQuerySet(UserFilteredQuerySet):
    """ Return courses visible to the given user through FKs (Homework->Lecture->Course). """
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        if user.role == "teacher":
            return self.filter(lecture__course__teachers=user)

        if user.role == "student":
            return self.filter(lecture__course__students=user)

        return self.none()


class HomeworkSubmissionQuerySet(models.QuerySet):
    """
    Return submissions visible to the given user through FKs (HomeworkSubmission->Homework->Lecture->Course).
    Teacher sees submissions in their course. Student sees only their submissions.
    """
    def for_user(self, user):
        if user.role == Role.TEACHER:
            return self.filter(homework__lecture__course__teachers=user)
        elif user.role == Role.STUDENT:
            return self.filter(student=user)
        return self.none()


class GradeQuerySet(models.QuerySet):
    """
        Return grades visible to the given user through FKs (HomeworkSubmission->Homework->Lecture->Course).
        Teacher sees grades in their course. Student sees only their grades.
    """
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()
        if user.role == Role.TEACHER:
            return self.filter(submission__homework__lecture__course__teachers=user)
        if user.role == Role.STUDENT:
            return self.filter(submission__student=user)
        return self.none()