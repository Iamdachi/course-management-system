from django.db import models

from .roles import Role


class CourseQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        if user.role == "teacher":
            return self.filter(teachers=user)

        if user.role == "student":
            return self.filter(students=user)

        return self.none()


class UserFilteredQuerySet(models.QuerySet):
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
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        if user.role == "teacher":
            return self.filter(lecture__course__teachers=user)

        if user.role == "student":
            return self.filter(lecture__course__students=user)

        return self.none()


class HomeworkSubmissionQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.role == Role.TEACHER:
            return self.filter(homework__lecture__course__teachers=user)
        elif user.role == Role.STUDENT:
            return self.filter(student=user)
        return self.none()


class GradeQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_anonymous:
            return self.none()
        if user.role == Role.TEACHER:
            return self.filter(submission__homework__lecture__course__teachers=user)
        if user.role == Role.STUDENT:
            return self.filter(submission__student=user)
        return self.none()
