from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lecture
from courses.permissions import IsTeacherOrReadOnly
from courses.models.roles import Role
from courses.serializers import CourseSerializer, UserSerializer, LectureSerializer
from courses.services.course_services import (
    add_user_to_course,
    remove_user_from_course,
    get_course_users,
    create_lecture_for_course, get_teaching_courses, get_enrolled_courses,
)
User = get_user_model()


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().prefetch_related("teachers", "students")
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        return Course.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        course = serializer.save()
        course.teachers.add(self.request.user)

    @action(detail=True, methods=["get", "post", "delete"], url_path="teachers")
    def manage_teachers(self, request, pk=None):
        course = self.get_object()
        if request.method == "GET":
            users = get_course_users(course, Role.TEACHER)
            return Response(UserSerializer(users, many=True).data)

        user_id = request.data.get("user")
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Teacher not found."}, status=404)

        if request.method == "POST":
            add_user_to_course(course, user, Role.TEACHER, request.user)
            return Response({"detail": f"{user.username} added."}, status=201)

        if request.method == "DELETE":
            remove_user_from_course(course, user, Role.TEACHER, request.user)
            return Response({"detail": f"{user.username} removed."}, status=204)

    @action(detail=True, methods=["get", "post", "delete"], url_path="students")
    def manage_students(self, request, pk=None):
        course = self.get_object()
        if request.method == "GET":
            users = get_course_users(course, Role.STUDENT)
            return Response(UserSerializer(users, many=True).data)

        user_id = request.data.get("user")
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Student not found."}, status=404)

        if request.method == "POST":
            add_user_to_course(course, user, Role.STUDENT, request.user)
            return Response({"detail": f"{user.username} added."}, status=201)

        if request.method == "DELETE":
            remove_user_from_course(course, user, Role.STUDENT, request.user)
            return Response({"detail": f"{user.username} removed."}, status=204)

    @action(detail=True, methods=["get", "post"], url_path="lectures")
    def lectures(self, request, pk=None):
        course = self.get_object()
        if request.method == "GET":
            lectures = course.lectures.select_related("course").prefetch_related(
                "homeworks", "course__teachers", "course__students"
            )
            serializer = LectureSerializer(lectures, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            lecture = create_lecture_for_course(course, request.data, request.user, LectureModel=Lecture)
            serializer = LectureSerializer(lecture)
            return Response(serializer.data, status=201)


class MyTeachingCoursesViewSet(viewsets.ViewSet):
    """Retrieve all courses the authenticated teacher is teaching."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        courses = get_teaching_courses(request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class MyEnrolledCoursesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        courses = get_enrolled_courses(request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
