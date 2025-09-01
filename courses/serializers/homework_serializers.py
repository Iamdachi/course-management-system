from rest_framework import serializers

from courses.models import Homework, HomeworkSubmission


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