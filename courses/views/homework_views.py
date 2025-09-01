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


class HomeworkViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage homeworks and their submissions."""

    http_method_names = ["get", "patch", "post", "delete"]
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def get_queryset(self):
        """Return homeworks visible to the requesting user."""
        user = self.request.user
        if user.role == Role.TEACHER:
            return Homework.objects.filter(lecture__course__teachers=user)
        return Homework.objects.filter(lecture__course__students=user)

    def get_permissions(self):
        """Return permissions depending on the current action."""
        if self.action == "submissions":
            return [CanAccessSubmissions()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="submissions")
    def submissions(self, request, pk=None):
        """Retrieve or submit homework submissions."""
        homework = self.get_object()

        if request.method == "GET":
            submissions = homework.submissions.select_related(
                "student", "homework__lecture__course"
            ).prefetch_related(
                "grades"
            )
            serializer = HomeworkSubmissionSerializer(submissions, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = HomeworkSubmissionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                homework=homework,
                student=request.user,
            )
            return Response(serializer.data, status=201)


class HomeworkSubmissionViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage individual homework submissions and grades."""

    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsStudentAndEnrolled]

    def get_queryset(self):
        """Return submissions visible to the requesting user."""
        user = self.request.user
        if user.role == Role.TEACHER:
            return HomeworkSubmission.objects.filter(
                homework__lecture__course__teachers=user
            )
        return HomeworkSubmission.objects.filter(student=user)

    def get_permissions(self):
        """Return permissions depending on the current action."""
        if self.action == "grades" and self.request.method == "POST":
            return [CanGradeCourse()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="grades")
    def grades(self, request, pk=None):
        """Retrieve or add grades for a homework submission."""
        submission = (
            self.get_queryset()
            .select_related("homework__lecture__course")
            .prefetch_related("grades__comments")
            .get(pk=pk)
        )

        if request.method == "GET":
            grades = submission.grades.select_related("teacher").all()
            serializer = GradeSerializer(grades, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = GradeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(submission=submission, teacher=request.user)
            return Response(serializer.data, status=201)


class MySubmissionsView(ListAPIView):
    """List homework submissions for the authenticated user."""

    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return submissions filtered by role and optional query params."""
        user = self.request.user
        submissions = HomeworkSubmission.objects.for_user(user)

        homework_id = self.request.query_params.get("homework")
        course_id = self.request.query_params.get("course")
        lecture_id = self.request.query_params.get("lecture")

        if homework_id:
            submissions = submissions.filter(homework_id=homework_id)
        if lecture_id:
            submissions = submissions.filter(homework__lecture_id=lecture_id)
        if course_id:
            submissions = submissions.filter(homework__lecture__course_id=course_id)

        return submissions
