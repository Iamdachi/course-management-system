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
        read_only_fields = ("student",)

    def validate_homework(self, homework):
        user = self.context["request"].user
        # Ensure student is enrolled in course of the homework
        course = homework.lecture.course
        if not course.students.filter(id=user.id).exists():
            raise serializers.ValidationError("You are not enrolled in this course.")
        return homework

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user

        if user.role == Role.STUDENT:
            # Students: only homeworks in their courses
            self.fields['homework'].queryset = Homework.objects.filter(
                lecture__course__students=user
            )
        else:
            self.fields['homework'].queryset = Homework.objects.none() # only let students see valid homework choices


class GradeSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source="teacher.username")

    class Meta:
        model = Grade
        fields = "__all__"
        read_only_fields = ["teacher", "created", "modified"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user

        if user.role == Role.TEACHER:
            # Teachers can only grade submissions from their own courses
            self.fields["submission"].queryset = HomeworkSubmission.objects.filter(
                homework__lecture__course__teachers=user
            )
        else:
            # Students (or others) should not be able to grade at all
            self.fields["submission"].queryset = HomeworkSubmission.objects.none()


class GradeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeComment
        fields = "__all__"
