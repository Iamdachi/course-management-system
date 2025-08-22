from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lecture, Homework, HomeworkSubmission, Grade, GradeComment, Role

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "role")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email"),
            role=validated_data["role"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ["id", "course", "topic", "presentation", "created_at", "updated_at"]
        read_only_fields = ("course",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if instance.presentation and request is not None:
            rep["presentation"] = request.build_absolute_uri(instance.presentation.url)
        return rep


class CourseSerializer(serializers.ModelSerializer):
    # Show teachers and students as read-only usernames
    teachers = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.filter(role=Role.TEACHER),
        required = False
    )
    students = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.filter(role=Role.STUDENT),
        required=False,  # field is optional
        allow_empty=True  # allow submitting empty list
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teachers', 'students']


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ["id", "lecture", "description", "created_at", "updated_at"]
        read_only_fields = ("lecture",)


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)  # allows file uploads

    class Meta:
        model = HomeworkSubmission
        fields = "__all__"
        read_only_fields = ("student", "homework")


class GradeSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source="teacher.username")

    class Meta:
        model = Grade
        fields = "__all__"
        read_only_fields = ["teacher", "created", "modified"]



class GradeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeComment
        fields = "__all__"
