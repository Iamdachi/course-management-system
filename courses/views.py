from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Role, Lecture, Homework
from .permissions import IsTeacherOrReadOnly, IsCourseTeacherOrReadOnly
from .serializers import UserSerializer, CourseSerializer, LectureSerializer, HomeworkSerializer

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

    def perform_create(self, serializer):
        # Optionally auto-add the logged-in teacher
        serializer.save(teachers=[self.request.user])


class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not course.teachers.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a teacher in this course.")
        serializer.save()


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
