from rest_framework import viewsets, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from courses.mixins import PostPutBlockedMixin
from courses.models import Lecture
from courses.permissions import IsCourseTeacherOrReadOnly
from courses.serializers import LectureSerializer, HomeworkSerializer


class LectureViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    """Manage lectures and associated homeworks."""

    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        """Return lectures accessible by the requesting user."""
        return Lecture.objects.for_user(self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="homeworks")
    def homeworks(self, request, pk=None):
        """Retrieve or create homeworks for the lecture."""
        lecture = self.get_object()

        if request.method == "GET":
            homeworks = lecture.homeworks.select_related(
                "lecture__course"
            ).prefetch_related("submissions")
            serializer = HomeworkSerializer(homeworks, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            if request.user not in lecture.course.teachers.all():
                raise PermissionDenied("Only course teachers can add homework.")
            serializer = HomeworkSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(lecture=lecture)
            return Response(serializer.data, status=201)
