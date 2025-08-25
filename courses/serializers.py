from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course,
    Lecture,
    Homework,
    HomeworkSubmission,
    Grade,
    GradeComment,
    Role,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model, handles password hashing on creation."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "role")

    def create(self, validated_data):
        """Create a new user and set their password securely."""
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email"),
            role=validated_data["role"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LectureSerializer(serializers.ModelSerializer):
    """Serializer for Lecture model with presentation URL absolute conversion."""

    class Meta:
        model = Lecture
        fields = ["id", "course", "topic", "presentation", "created_at", "updated_at"]
        read_only_fields = ("course", "created_at", "updated_at")

    def to_representation(self, instance):
        """Return lecture data, including absolute URL for presentation if available."""
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if instance.presentation and request is not None:
            rep["presentation"] = request.build_absolute_uri(instance.presentation.url)
        return rep


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


class HomeworkSerializer(serializers.ModelSerializer):
    """Serializer for Homework model with read-only lecture field."""

    class Meta:
        model = Homework
        fields = ["id", "lecture", "description", "created_at", "updated_at"]
        read_only_fields = ("lecture",)


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for HomeworkSubmission model, handling file uploads."""

    file = serializers.FileField(required=False)  # allows file uploads

    class Meta:
        model = HomeworkSubmission
        fields = "__all__"
        read_only_fields = ("student", "homework")


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade model with read-only teacher field."""

    teacher = serializers.ReadOnlyField(source="teacher.username")

    class Meta:
        model = Grade
        fields = "__all__"
        read_only_fields = ["teacher", "created", "modified", "submission"]


class GradeCommentSerializer(serializers.ModelSerializer):
    """Serializer for GradeComment model with read-only author and grade fields."""

    class Meta:
        model = GradeComment
        fields = "__all__"
        read_only_fields = ("author", "grade", "created_at")
