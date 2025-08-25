from django.contrib.auth import get_user_model
from django.utils import timezone
import factory

from ..models import Course, Lecture, Homework
from ..roles import Role

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

    @factory.post_generation
    def teachers(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for teacher in extracted:
                self.teachers.add(teacher)

    @factory.post_generation
    def students(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for student in extracted:
                self.students.add(student)


class LectureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lecture

    course = factory.SubFactory(CourseFactory)
    topic = factory.Faker("sentence", nb_words=3)
    presentation = None
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class HomeworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Homework

    lecture = factory.SubFactory(LectureFactory)
    description = factory.Faker("paragraph", nb_sentences=2)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
