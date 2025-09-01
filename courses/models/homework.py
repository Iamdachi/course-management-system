from django.db import models

from courses.models import Lecture, User, Role
from courses.models.base import UUIDModel, TimeStampedModel
from courses.querysets import HomeworkQuerySet, HomeworkSubmissionQuerySet


class Homework(UUIDModel, TimeStampedModel):
    """Represents homework assigned for a lecture."""

    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="homeworks"
    )
    description = models.TextField(blank=True, default="")

    objects = HomeworkQuerySet.as_manager()

    def __str__(self):
        """Return 'HW for Lecture Topic'."""
        return f"HW for {self.lecture.topic}"


class HomeworkSubmission(UUIDModel, TimeStampedModel):
    """Represents a student's submission for a homework, including optional file."""

    homework = models.ForeignKey(
        Homework, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submissions",
        limit_choices_to={"role": Role.STUDENT},
    )
    content = models.TextField()
    file = models.FileField(upload_to="submissions/", blank=True, null=True)

    objects = HomeworkSubmissionQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["homework", "student"],
                name="unique_submission_per_homework",
            )
        ]

    def __str__(self):
        """Return 'Student Email → Lecture Topic'."""
        return f"{self.student.email} → {self.homework.lecture.topic}"

