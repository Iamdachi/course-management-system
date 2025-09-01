from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from courses.permissions import IsSelfOrAdmin
from courses.serializers import UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """Log out a user by blacklisting their refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle POST request to log out a user."""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (KeyError, Exception):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """User profile management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        """Endpoint for the authenticated user's own profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
