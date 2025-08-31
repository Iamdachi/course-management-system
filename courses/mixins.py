from rest_framework.response import Response


class PostPutBlockedMixin:
    """
    Mixin to disable direct POST/PUT on the base endpoint of a
    LectureViewSet, HomeworkViewSet, HomeworkSubmissionViewSet, GradeViewSet, GradeCommentViewSet.

    Rationale:
    - Prevents creating or fully updating resources directly via /<model>/.
    - Still allows custom actions (e.g., /lectures/{id}/homeworks/)
      to handle POST requests explicitly. which was not possible using 'http_method_names'
    """

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Direct POST not allowed."}, status=405)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Direct PUT not allowed."}, status=405)
