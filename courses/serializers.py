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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        # Restrict the course choices in the browsable form
        self.fields["course"].queryset = Course.objects.filter(teachers=user)



class CourseSerializer(serializers.ModelSerializer):
    # Show teachers and students as read-only usernames
    teachers = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.filter(role=Role.TEACHER)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        # Restrict lecture choices to lectures in user's own courses
        self.fields["lecture"].queryset = Lecture.objects.filter(course__teachers=user)


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"


class GradeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeComment
        fields = "__all__"
