from requests import Response


class PostPutBlockedMixin:
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Direct POST not allowed."}, status=405)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Direct PUT not allowed."}, status=405)
