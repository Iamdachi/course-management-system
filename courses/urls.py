from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from courses.views import RegisterView, LogoutView, UserViewSet, CourseViewSet, LectureViewSet, HomeworkViewSet, \
    HomeworkSubmissionViewSet, GradeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r"lectures", LectureViewSet)
router.register(r"homeworks", HomeworkViewSet)
router.register(r'submissions', HomeworkSubmissionViewSet, basename='submission')
router.register(r'grades', GradeViewSet, basename='grade')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('', include(router.urls)),
]