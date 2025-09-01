from rest_framework import serializers

from courses.models import Grade, GradeComment


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
