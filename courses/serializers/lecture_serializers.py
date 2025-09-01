from rest_framework import serializers

from courses.models import Lecture


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