from .base import IsSelfOrAdmin
from .courses import IsTeacherOrReadOnly, IsCourseTeacherOrReadOnly
from .submissions import (
    IsStudentAndEnrolled,
    IsStudentOfCourseOrTeacherCanView,
    CanAccessSubmissions,
)
from .grades import (
    IsTeacherOfCourse,
    IsGradeOwnerOrCourseTeacher,
    CanGradeCourse,
    CanCommentOnGrade,
)

__all__ = [
    "IsSelfOrAdmin",
    "IsTeacherOrReadOnly",
    "IsCourseTeacherOrReadOnly",
    "IsStudentAndEnrolled",
    "IsStudentOfCourseOrTeacherCanView",
    "CanAccessSubmissions",
    "IsTeacherOfCourse",
    "IsGradeOwnerOrCourseTeacher",
    "CanGradeCourse",
    "CanCommentOnGrade",
]
