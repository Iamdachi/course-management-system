from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Role, Lecture, Homework, HomeworkSubmission, Grade
from .permissions import IsTeacherOrReadOnly, IsCourseTeacherOrReadOnly, IsStudentAndEnrolled, IsTeacherOfCourse, \
    IsGradeOwnerOrCourseTeacher
from .serializers import UserSerializer, CourseSerializer, LectureSerializer, HomeworkSerializer, \
    HomeworkSubmissionSerializer, GradeSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # requires simplejwt blacklist app
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
    })

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        return Course.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        course = serializer.save()  # save the Course first
        course.teachers.add(self.request.user)  # then add the M2M relation

    @action(detail=True, methods=["get", "post", "delete"], url_path="teachers")
    def manage_teachers(self, request, pk=None):
        course = self.get_object()

        def get_teachers():
            serializer = UserSerializer(course.teachers.all(), many=True)
            return Response(serializer.data)

        def add_teacher():
            self._assert_course_teacher(course)
            user_id = request.data.get("user")
            teacher = self._get_teacher_or_404(user_id)
            course.teachers.add(teacher)
            return Response({"detail": f"Teacher {teacher.username} added."}, status=201)

        def remove_teacher():
            self._assert_course_teacher(course)
            user_id = request.data.get("user")
            teacher = self._get_teacher_or_404(user_id)
            course.teachers.remove(teacher)
            return Response({"detail": f"Teacher {teacher.username} removed."}, status=204)

        dispatch = {
            "GET": get_teachers,
            "POST": add_teacher,
            "DELETE": remove_teacher,
        }

        handler = dispatch.get(request.method)
        return handler()

    def _get_teacher_or_404(self, user_id):
        try:
            return User.objects.get(id=user_id, role=Role.TEACHER)
        except User.DoesNotExist:
            raise NotFound("Teacher not found.")

    def _assert_course_teacher(self, course):
        if self.request.user not in course.teachers.all():
            raise PermissionDenied("You are not a teacher of this course.")


class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not course.teachers.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a teacher in this course.")
        serializer.save()

    def get_queryset(self):
        return Lecture.objects.for_user(self.request.user)


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def perform_create(self, serializer):
        lecture = serializer.validated_data["lecture"]
        course = lecture.course
        if not course.teachers.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a teacher in this course.")
        serializer.save()

    def get_queryset(self):
        return Homework.objects.for_user(self.request.user)


class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsStudentAndEnrolled]

    def get_queryset(self):
        return HomeworkSubmission.objects.visible_to(self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != Role.STUDENT:
            raise PermissionDenied("Only students can submit homework.")
        serializer.save(student=self.request.user)


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsGradeOwnerOrCourseTeacher]

    def get_queryset(self):
        return Grade.objects.visible_to(self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != Role.TEACHER:
            raise PermissionDenied("Only teachers can grade submissions.")
        serializer.save(teacher=self.request.user)

        def perform_update(self, serializer):
            # also enforce teacher stays the same
            serializer.save(teacher=self.request.user)
