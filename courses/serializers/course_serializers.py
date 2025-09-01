from django.contrib.auth import get_user_model
from rest_framework import serializers

from courses.models import Course
from courses.models.roles import Role

User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model, showing teachers and students as usernames."""

    teachers = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.filter(role=Role.TEACHER),
        required=False,
    )
    students = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.filter(role=Role.STUDENT),
        required=False,  # field is optional
        allow_empty=True,  # allow submitting empty list
    )

    class Meta:
        model = Course
        fields = ["id", "title", "description", "teachers", "students"]
