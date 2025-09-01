from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from courses.models import HomeworkSubmission, User, Role
from courses.models.base import UUIDModel, TimeStampedModel
from courses.querysets import GradeQuerySet, GradeCommentQuerySet


class Grade(UUIDModel, TimeStampedModel):
    """Represents a grade given to a homework submission by a teacher."""

    submission = models.ForeignKey(
        HomeworkSubmission, on_delete=models.CASCADE, related_name="grades"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="given_grades",
        limit_choices_to={"role": Role.TEACHER},
    )
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage grade between 0 and 100",
    )
    feedback = models.TextField(blank=True, default="")

    objects = GradeQuerySet.as_manager()

    def __str__(self):
        """Return 'Grade Value% for Lecture Topic'."""
        return f"{self.value}% for {self.submission.homework.lecture.topic}"


class GradeComment(UUIDModel, TimeStampedModel):
    """Represents a comment on a grade, authored by a user."""

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="grade_comments"
    )
    content = models.TextField(blank=True, default="")

    objects = GradeCommentQuerySet.as_manager()

    def __str__(self):
        """Return 'Comment by Author Email on Grade ID'."""
        return f"Comment by {self.author.email} on {self.grade.id}"
