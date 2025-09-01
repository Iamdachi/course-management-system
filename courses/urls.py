from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from courses.views import (
    RegisterViewSet,
    LogoutViewSet,
    UserViewSet,
    CourseViewSet,
    LectureViewSet,
    HomeworkViewSet,
    HomeworkSubmissionViewSet,
    GradeViewSet,
    MyTeachingCoursesViewSet,
    MyEnrolledCoursesViewSet,
    GradeCommentViewSet,
    MySubmissionsViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lectures", LectureViewSet)
router.register(r"homeworks", HomeworkViewSet)
router.register(r"submissions", HomeworkSubmissionViewSet, basename="submission")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"grade-comments", GradeCommentViewSet, basename="grade-comment")
router.register(r"logout", LogoutViewSet, basename="logout")
router.register(r"me/enrolled-courses", MyEnrolledCoursesViewSet, basename="my-enrolled-courses"),

urlpatterns = [
    path("register/", RegisterViewSet.as_view({'post': 'create'}), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns += [
    path(
        "me/teaching-courses/",
        MyTeachingCoursesViewSet.as_view({'get': 'list'}),
        name="my-teaching-courses",
    ),
    path(
        "me/submissions/",
        MySubmissionsViewSet.as_view({'get': 'list'}),
        name="my-submissions",
    ),
]
