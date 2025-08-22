from django.utils.translation import gettext_lazy as _
from django.db import models

class Role(models.TextChoices):
    TEACHER = "teacher", _("Teacher")
    STUDENT = "student", _("Student")
