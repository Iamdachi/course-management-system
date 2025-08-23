import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .querysets import (
    CourseQuerySet,
    GradeCommentQuerySet,
    GradeQuerySet,
    HomeworkQuerySet,
    HomeworkSubmissionQuerySet,
    LectureQuerySet,
)
from .roles import Role


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser, UUIDModel):
    REQUIRED_FIELDS = ["role", "email"]
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Course(UUIDModel, TimeStampedModel):
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
        return self.title


class Lecture(UUIDModel, TimeStampedModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    topic = models.CharField(max_length=255)
    presentation = models.FileField(upload_to="presentations/", blank=True, null=True)

    objects = LectureQuerySet.as_manager()

    def __str__(self):
        return f"{self.course.title} - {self.topic}"


class Homework(UUIDModel, TimeStampedModel):
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="homeworks"
    )
    description = models.TextField(blank=True, default="")

    objects = HomeworkQuerySet.as_manager()

    def __str__(self):
        return f"HW for {self.lecture.topic}"


class HomeworkSubmission(UUIDModel, TimeStampedModel):
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
        return f"{self.student.email} → {self.homework.lecture.topic}"


class Grade(UUIDModel, TimeStampedModel):
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
        return f"{self.value}% for {self.submission.homework.lecture.topic}"


class GradeComment(UUIDModel, TimeStampedModel):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="grade_comments"
    )
    content = models.TextField(blank=True, default="")

    objects = GradeCommentQuerySet.as_manager()

    def __str__(self):
        return f"Comment by {self.author.email} on {self.grade.id}"
