from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status, request
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework import viewsets, mixins
from courses.permissions import IsSelfOrAdmin
from courses.serializers import UserSerializer

User = get_user_model()


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Register a new user account.
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LogoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = OutstandingToken.objects.get(token=refresh_token)
            BlacklistedToken.objects.create(token=token)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (KeyError, OutstandingToken.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """User profile management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        """Endpoint for the authenticated user's own profile."""
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        # PATCH
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
