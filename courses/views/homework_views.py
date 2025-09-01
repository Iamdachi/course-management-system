from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.mixins import PostPutBlockedMixin
from courses.models import Homework, HomeworkSubmission
from courses.permissions import IsCourseTeacherOrReadOnly, CanAccessSubmissions, IsStudentAndEnrolled, CanGradeCourse
from courses.models.roles import Role
from courses.serializers import HomeworkSerializer, HomeworkSubmissionSerializer, GradeSerializer

from courses.services.homework_services import (
    get_homeworks_for_user,
    get_homework_submissions,
    submit_homework, add_grade_to_submission, get_submission_grades, get_submissions_for_user,
    filter_submissions_for_user,
)


class HomeworkViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage homeworks and their submissions."""

    http_method_names = ["get", "patch", "post", "delete"]
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def get_queryset(self):
        return get_homeworks_for_user(self.request.user)

    def get_permissions(self):
        if self.action == "submissions":
            return [CanAccessSubmissions()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="submissions")
    def submissions(self, request, pk=None):
        homework = self.get_object()

        if request.method == "GET":
            submissions = get_homework_submissions(homework)
            serializer = HomeworkSubmissionSerializer(submissions, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            submission = submit_homework(homework, request.user, request.data, HomeworkSubmissionSerializer)
            serializer = HomeworkSubmissionSerializer(submission)
            return Response(serializer.data, status=201)


class HomeworkSubmissionViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage individual homework submissions and grades."""

    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsStudentAndEnrolled]

    def get_queryset(self):
        return get_submissions_for_user(self.request.user)

    def get_permissions(self):
        if self.action == "grades" and self.request.method == "POST":
            return [CanGradeCourse()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="grades")
    def grades(self, request, pk=None):
        submission = self.get_object()  # queryset filtering already done in get_queryset()

        if request.method == "GET":
            grades = get_submission_grades(submission)
            serializer = GradeSerializer(grades, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            grade = add_grade_to_submission(submission, request.user, request.data, GradeSerializer)
            serializer = GradeSerializer(grade)
            return Response(serializer.data, status=201)


class MySubmissionsView(ListAPIView):
    """List homework submissions for the authenticated user."""

    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        params = self.request.query_params
        return filter_submissions_for_user(
            self.request.user,
            homework_id=params.get("homework"),
            lecture_id=params.get("lecture"),
            course_id=params.get("course"),
        )