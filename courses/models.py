import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .querysets import LectureQuerySet, HomeworkQuerySet, CourseQuerySet, HomeworkSubmissionQuerySet, GradeQuerySet, \
    GradeCommentQuerySet
from .roles import Role


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser, UUIDModel):
    REQUIRED_FIELDS = ['role', 'email']
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)


class Course(UUIDModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teachers = models.ManyToManyField(User, related_name="teaching_courses", limit_choices_to={"role": Role.TEACHER})
    students = models.ManyToManyField(User, related_name="enrolled_courses", blank=True, limit_choices_to={"role": Role.STUDENT})

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title


class Lecture(UUIDModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lectures")
    topic = models.CharField(max_length=255)
    presentation = models.FileField(upload_to="presentations/", blank=True, null=True)

    objects = LectureQuerySet.as_manager()

    def __str__(self):
        return f"{self.course.title} - {self.topic}"


class Homework(UUIDModel, TimeStampedModel):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="homeworks")
    description = models.TextField()

    objects = HomeworkQuerySet.as_manager()

    def __str__(self):
        return f"HW for {self.lecture.topic}"


class HomeworkSubmission(UUIDModel, TimeStampedModel):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions", limit_choices_to={"role": Role.STUDENT})
    content = models.TextField()
    file = models.FileField(upload_to="submissions/", blank=True, null=True)

    objects = HomeworkSubmissionQuerySet.as_manager()

    class Meta:
        unique_together = ("homework", "student")


class Grade(UUIDModel, TimeStampedModel):
    submission = models.ForeignKey(HomeworkSubmission, on_delete=models.CASCADE, related_name="grades")
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="given_grades", limit_choices_to={"role": Role.TEACHER})
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage grade between 0 and 100"
    )
    feedback = models.TextField(blank=True)

    objects = GradeQuerySet.as_manager()


class GradeComment(UUIDModel, TimeStampedModel):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="grade_comments")
    content = models.TextField()

    objects = GradeCommentQuerySet.as_manager()
