from courses.models import Course
from courses.models.base import UUIDModel, TimeStampedModel
from django.db import models

from courses.querysets import LectureQuerySet


class Lecture(UUIDModel, TimeStampedModel):
    """Represents a lecture within a course with optional presentation file."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    topic = models.CharField(max_length=255)
    presentation = models.FileField(upload_to="presentations/", blank=True, null=True)

    objects = LectureQuerySet.as_manager()

    def __str__(self):
        """Return 'Course Title - Lecture Topic'."""
        return f"{self.course.title} - {self.topic}"
