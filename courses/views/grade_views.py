from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from courses.mixins import PostPutBlockedMixin
from courses.models import Grade, GradeComment
from courses.permissions import IsGradeOwnerOrCourseTeacher, CanCommentOnGrade
from courses.serializers import GradeSerializer, GradeCommentSerializer
from courses.services.grade_services import (
    create_grade,
    update_grade,
    get_grade_comments,
    add_grade_comment, get_visible_grade_comments, create_grade_comment,
)

class GradeViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage grades and their comments."""

    serializer_class = GradeSerializer
    permission_classes = [IsGradeOwnerOrCourseTeacher]

    def get_queryset(self):
        """Return grades accessible by the requesting user."""
        return Grade.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        """Save a new grade with the current user as teacher."""
        serializer.save(teacher=self.request.user)

    def perform_update(self, serializer):
        """Update a grade while keeping the teacher fixed."""
        serializer.save(teacher=self.request.user)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="comments",
        permission_classes=[CanCommentOnGrade],
    )
    def comments(self, request, pk=None):
        """Retrieve or add comments on a grade."""
        grade = (
            self.get_queryset()
            .select_related("submission__homework__lecture__course", "teacher")
            .prefetch_related("comments__author")
            .get(pk=pk)
        )

        if request.method == "GET":
            comments = grade.comments.all()
            serializer = GradeCommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = GradeCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(grade=grade, author=request.user)
            return Response(serializer.data, status=201)


class GradeCommentViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage grade comments."""

    http_method_names = ["get", "patch", "delete"]
    serializer_class = GradeCommentSerializer
    permission_classes = [CanCommentOnGrade]

    def perform_create(self, serializer):
        """Save a new grade comment with the current user as author."""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """
        Return comments visible to the requesting user.
        Teacher can see all comments on their course’s grades, students see their own
        """
        return GradeComment.objects.for_user(self.request.user)