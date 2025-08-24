from django.contrib.auth import get_user_model
import factory

from ..models import Course
from ..roles import Role  # your Role enum-like object

User = get_user_model()

class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class TeacherFactory(BaseUserFactory):
    role = Role.TEACHER


class StudentFactory(BaseUserFactory):
    role = Role.STUDENT


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: f"Course {n}")
    description = "Test course"