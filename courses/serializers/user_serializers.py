from django.contrib.auth import get_user_model
from rest_framework import serializers

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