from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from courses.views import (
    RegisterView,
    LogoutView,
    UserViewSet,
    CourseViewSet,
    LectureViewSet,
    HomeworkViewSet,
    HomeworkSubmissionViewSet,
    GradeViewSet,
    MyTeachingCoursesView,
    MyEnrolledCoursesView,
    GradeCommentViewSet,
    MySubmissionsView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lectures", LectureViewSet)
router.register(r"homeworks", HomeworkViewSet)
router.register(r"submissions", HomeworkSubmissionViewSet, basename="submission")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"grade-comments", GradeCommentViewSet, basename="grade-comment")


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
    path(
        "me/teaching-courses/",
        MyTeachingCoursesView.as_view(),
        name="my-teaching-courses",
    ),
    path(
        "me/enrolled-courses/",
        MyEnrolledCoursesView.as_view(),
        name="my-enrolled-courses",
    ),
    path("me/submissions/", MySubmissionsView.as_view(), name="my-submissions"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
