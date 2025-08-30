from rest_framework import generics, status, viewsets, permissions, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from courses.mixins import PostPutBlockedMixin
from .models import (
    Course,
    Role,
    Lecture,
    Homework,
    HomeworkSubmission,
    Grade,
    GradeComment,
)
from .permissions import (
    IsTeacherOrReadOnly,
    IsCourseTeacherOrReadOnly,
    IsStudentAndEnrolled,
    IsGradeOwnerOrCourseTeacher,
    CanAccessSubmissions,
    CanGradeCourse,
    CanCommentOnGrade,
)
from .serializers import (
    UserSerializer,
    CourseSerializer,
    LectureSerializer,
    HomeworkSerializer,
    HomeworkSubmissionSerializer,
    GradeSerializer,
    GradeCommentSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """Log out a user by blacklisting their refresh token."""

    permission_classes = [AllowAny]

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
    """CRUD operations for user accounts."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


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
        course = serializer.save()  # save the Course first
        course.teachers.add(self.request.user)  # auto-adds creator as teacher (M2M)

    def _teacher_student_management(self, relation_name, role=None):
        """
        Handle get/add/remove operations for course teachers or students.
        - relation_name: str, e.g., 'teachers' or 'students'
        - role: optional Role constant to enforce (Role.TEACHER / Role.STUDENT)
        """
        course = self.get_object()
        relation = getattr(course, relation_name)  # course.teachers or course.students

        def get_items():
            serializer = UserSerializer(relation.all(), many=True)
            return Response(serializer.data)

        def add_item():
            self._assert_course_teacher(course)  # only course teachers can add
            user_id = self.request.data.get("user")
            user = self._get_user_or_404(user_id, role)
            relation.add(user)
            return Response({"detail": f"{user.username} added."}, status=201)

        def remove_item():
            self._assert_course_teacher(course)  # only course teachers can remove
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
                student=request.user,  # attach the authenticated student
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
            .prefetch_related("grades__comments")  # if GradeComment has FK to Grade
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


class GradeViewSet(viewsets.ModelViewSet):
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


class GradeCommentViewSet(viewsets.ModelViewSet):
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
