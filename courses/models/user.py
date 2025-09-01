from django.contrib.auth.models import AbstractUser

from courses.models.base import UUIDModel
from courses.models.roles import Role
from django.db import models


class User(AbstractUser, UUIDModel):
    """Custom user model with role field (student or teacher)."""

    REQUIRED_FIELDS = ["role", "email"]
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        """Return user's email and role display."""
        return f"{self.email} ({self.get_role_display()})"