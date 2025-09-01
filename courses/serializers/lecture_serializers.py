from rest_framework import serializers
from courses.services.lecture_services import get_lecture_representation

from courses.models import Lecture


class LectureSerializer(serializers.ModelSerializer):
    """Serializer for Lecture model with presentation URL absolute conversion."""

    class Meta:
        model = Lecture
        fields = ["id", "course", "topic", "presentation", "created_at", "updated_at"]
        read_only_fields = ("course", "created_at", "updated_at")

    def to_representation(self, instance):
        request = self.context.get("request")
        return get_lecture_representation(instance, request)