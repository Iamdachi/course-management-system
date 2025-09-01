from .course_views import CourseViewSet, MyTeachingCoursesViewSet, MyEnrolledCoursesViewSet
from .lecture_views import LectureViewSet
from .homework_views import HomeworkViewSet, HomeworkSubmissionViewSet, MySubmissionsViewSet
from .grade_views import GradeViewSet, GradeCommentViewSet
from .user_views import UserViewSet, RegisterViewSet, LogoutViewSet

__all__ = [
    "CourseViewSet",
    "MyTeachingCoursesViewSet",
    "MyEnrolledCoursesViewSet",
    "LectureViewSet",
    "HomeworkViewSet",
    "HomeworkSubmissionViewSet",
    "MySubmissionsViewSet",
    "GradeViewSet",
    "GradeCommentViewSet",
    "UserViewSet",
    "RegisterViewSet",
    "LogoutViewSet",
]
