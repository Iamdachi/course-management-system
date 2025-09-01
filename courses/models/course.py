from courses.models import User, Role
from courses.models.base import UUIDModel, TimeStampedModel
from django.db import models

from courses.querysets import CourseQuerySet


class Course(UUIDModel, TimeStampedModel):
    """Represents a course with teachers and enrolled students."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    teachers = models.ManyToManyField(
        User, related_name="teaching_courses", limit_choices_to={"role": Role.TEACHER}
    )
    students = models.ManyToManyField(
        User,
        related_name="enrolled_courses",
        blank=True,
        limit_choices_to={"role": Role.STUDENT},
    )

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        """Return the course title."""
        return self.title