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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (KeyError, Exception):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        return Course.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        course = serializer.save()  # save the Course first
        course.teachers.add(self.request.user)  # auto-adds creator as teacher (M2M)

    def _manage_relation(self, relation_name, role=None):
        """
        Generic M2M manager for teachers or students.
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
        try:
            user = User.objects.get(id=user_id)
            if role and user.role != role:
                raise User.DoesNotExist
            return user
        except User.DoesNotExist:
            raise NotFound(f"{role or 'User'} not found.")

    def _assert_course_teacher(self, course):
        if self.request.user not in course.teachers.all():
            raise PermissionDenied("You are not a teacher of this course.")

    @action(detail=True, methods=["get", "post", "delete"], url_path="teachers")
    def manage_teachers(self, request, pk=None):
        return self._manage_relation("teachers", role=Role.TEACHER)

    @action(detail=True, methods=["get", "post", "delete"], url_path="students")
    def manage_students(self, request, pk=None):
        return self._manage_relation("students", role=Role.STUDENT)

    @action(detail=True, methods=["get", "post"], url_path="lectures")
    def lectures(self, request, pk=None):
        course = self.get_object()

        if request.method == "GET":
            lectures = course.lectures.all()
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != Role.TEACHER:
            return Response(
                {"detail": "Only teachers can view teaching courses."}, status=403
            )
        courses = request.user.teaching_courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class MyEnrolledCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != Role.STUDENT:
            return Response(
                {"detail": "Only students can view enrolled courses."}, status=403
            )
        courses = request.user.enrolled_courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class LectureViewSet(viewsets.ModelViewSet, PostPutBlockedMixin):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        return Lecture.objects.for_user(self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="homeworks")
    def homeworks(self, request, pk=None):
        lecture = self.get_object()

        if request.method == "GET":
            homeworks = lecture.homeworks.all()
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
    http_method_names = ["get", "patch", "post", "delete"]
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsCourseTeacherOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == Role.TEACHER:
            return Homework.objects.filter(lecture__course__teachers=user)
        return Homework.objects.filter(lecture__course__students=user)

    def get_permissions(self):
        if self.action == "submissions":
            return [CanAccessSubmissions()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="submissions")
    def submissions(self, request, pk=None):
        homework = self.get_object()

        if request.method == "GET":
            submissions = homework.submissions.all()
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
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsStudentAndEnrolled]

    def get_queryset(self):
        user = self.request.user
        if user.role == Role.TEACHER:
            return HomeworkSubmission.objects.filter(
                homework__lecture__course__teachers=user
            )
        return HomeworkSubmission.objects.filter(student=user)

    def get_permissions(self):
        if self.action == "grades" and self.request.method == "POST":
            return [CanGradeCourse()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="grades")
    def grades(self, request, pk=None):
        submission = self.get_object()

        if request.method == "GET":
            grades = submission.grades.all()
            serializer = GradeSerializer(grades, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = GradeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(submission=submission, teacher=request.user)
            return Response(serializer.data, status=201)


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsGradeOwnerOrCourseTeacher]

    def get_queryset(self):
        return Grade.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)  # sets teacher

    def perform_update(self, serializer):
        serializer.save(
            teacher=self.request.user
        )  # also enforce teacher stays the same

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="comments",
        permission_classes=[CanCommentOnGrade],
    )
    def comments(self, request, pk=None):
        grade = self.get_object()

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
    http_method_names = ["get", "patch", "put", "delete"]
    queryset = GradeComment.objects.all()
    serializer_class = GradeCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # Teacher can see all comments on their course’s grades, students see their own
        return GradeComment.objects.for_user(self.request.user)

class MySubmissionsView(ListAPIView):
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = HomeworkSubmission.objects.all()
        if user.role == Role.STUDENT:
            # Students → only their own submissions
            qs = qs.filter(student=user)
        elif user.role == Role.TEACHER:
            # Teachers → submissions from their courses
            qs = qs.filter(homework__lecture__course__teachers=user)
        else:
            # Other roles (e.g. admin) → nothing, or you could allow full access
            return HomeworkSubmission.objects.none()

        # Optional filters
        homework_id = self.request.query_params.get("homework")
        course_id = self.request.query_params.get("course")
        lecture_id = self.request.query_params.get("lecture")

        if homework_id:
            qs = qs.filter(homework_id=homework_id)
        if lecture_id:
            qs = qs.filter(homework__lecture_id=lecture_id)
        if course_id:
            qs = qs.filter(homework__lecture__course_id=course_id)

        return qs
