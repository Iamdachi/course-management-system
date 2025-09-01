from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from courses.permissions import IsTeacherOrReadOnly
from courses.roles import Role
from courses.serializers import CourseSerializer, UserSerializer, LectureSerializer

User = get_user_model()

class CourseViewSet(viewsets.ModelViewSet):
    """Manage courses, including teachers, students, and lectures."""

    queryset = Course.objects.all().prefetch_related("teachers", "students")
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        """Return courses accessible by the requesting user."""
        return Course.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        """Save a new course and add the creator as a teacher."""
        course = serializer.save()
        course.teachers.add(self.request.user)

    def _teacher_student_management(self, relation_name, role=None):
        """
        Handle get/add/remove operations for course teachers or students.
        - relation_name: str, e.g., 'teachers' or 'students'
        - role: optional Role constant to enforce (Role.TEACHER / Role.STUDENT)
        """
        course = self.get_object()
        relation = getattr(course, relation_name)

        def get_items():
            serializer = UserSerializer(relation.all(), many=True)
            return Response(serializer.data)

        def add_item():
            self._assert_course_teacher(course)
            user_id = self.request.data.get("user")
            user = self._get_user_or_404(user_id, role)
            relation.add(user)
            return Response({"detail": f"{user.username} added."}, status=201)

        def remove_item():
            self._assert_course_teacher(course)
            user_id = self.request.data.get("user")
            user = self._get_user_or_404(user_id, role)
            relation.remove(user)
            return Response({"detail": f"{user.username} removed."}, status=204)

        dispatch = {
            "GET": get_items,
            "POST": add_item,
            "DELETE": remove_item,
        }

        handler = dispatch.get(self.request.method)
        if handler is None:
            return Response({"detail": "Method not allowed."}, status=405)
        return handler()

    def _get_user_or_404(self, user_id, role=None):
        """Fetch a user by ID, optionally filtering by role, or raise 404."""
        try:
            user = User.objects.get(id=user_id)
            if role and user.role != role:
                raise User.DoesNotExist
            return user
        except User.DoesNotExist:
            raise NotFound(f"{role or 'User'} not found.")

    def _assert_course_teacher(self, course):
        """Raise PermissionDenied if the requesting user is not a course teacher."""
        if not course.teachers.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a teacher in this course.")

    @action(detail=True, methods=["get", "post", "delete"], url_path="teachers")
    def manage_teachers(self, request, pk=None):
        """Manage teachers for the course."""
        return self._teacher_student_management("teachers", role=Role.TEACHER)

    @action(detail=True, methods=["get", "post", "delete"], url_path="students")
    def manage_students(self, request, pk=None):
        """Manage students for the course."""
        return self._teacher_student_management("students", role=Role.STUDENT)

    @action(detail=True, methods=["get", "post"], url_path="lectures")
    def lectures(self, request, pk=None):
        """Retrieve or create lectures for the course."""
        course = self.get_object()

        if request.method == "GET":
            lectures = (
                course.lectures.select_related("course")
                .prefetch_related("homeworks")
                .prefetch_related("course__teachers", "course__students")
            )
            serializer = LectureSerializer(lectures, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            if request.user not in course.teachers.all():
                return Response(
                    {"detail": "Only course teachers can add lectures."}, status=403
                )
            serializer = LectureSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(course=course)
            return Response(serializer.data, status=201)


class MyTeachingCoursesView(APIView):
    """Retrieve all courses the authenticated teacher is teaching."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the list of courses for the requesting teacher."""
        if request.user.role != Role.TEACHER:
            return Response(
                {"detail": "Only teachers can view teaching courses."}, status=403
            )
        courses = request.user.teaching_courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class MyEnrolledCoursesView(APIView):
    """Retrieve all courses the authenticated student is enrolled in."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the list of courses for the requesting student."""
        if request.user.role != Role.STUDENT:
            return Response(
                {"detail": "Only students can view enrolled courses."}, status=403
            )
        courses = request.user.enrolled_courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
