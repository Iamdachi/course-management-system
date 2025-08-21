from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lecture, Homework, HomeworkSubmission, Grade, GradeComment, Role

User = get_user_model()

# ---------- Users ----------
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

# ---------- Courses ----------
class CourseSerializer(serializers.ModelSerializer):
    teachers = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(role=Role.TEACHER))
    students = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(role=Role.STUDENT), required=False)

    class Meta:
        model = Course
        fields = "__all__"

# ---------- Lectures ----------
class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = "__all__"

# ---------- Homework ----------
class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = "__all__"

# ---------- Homework Submissions ----------
class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = "__all__"

# ---------- Grades ----------
class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"

class GradeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeComment
        fields = "__all__"
