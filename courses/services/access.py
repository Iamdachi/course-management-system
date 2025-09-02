from courses.models.roles import Role


def is_teacher(user) -> bool:
    return user.is_authenticated and user.role == Role.TEACHER


def is_student(user) -> bool:
    return user.is_authenticated and user.role == Role.STUDENT


def is_course_teacher(user, course) -> bool:
    """Check if user is a teacher of the given course."""
    return is_teacher(user) and course.teachers.filter(id=user.id).exists()


def is_course_student(user, course) -> bool:
    """Check if user is a student enrolled in the given course."""
    return is_student(user) and course.students.filter(id=user.id).exists()


def get_course_from_obj(obj):
    """
    Try to resolve the Course object from different domain objects.
    Works for course, lecture, homework, submission, grade, comment.
    """
    if hasattr(obj, "teachers") and hasattr(obj, "students"):
        return obj  # it's a Course
    if hasattr(obj, "course"):
        return obj.course
    if hasattr(obj, "lecture"):
        return obj.lecture.course
    if hasattr(obj, "homework"):
        return obj.homework.lecture.course
    if hasattr(obj, "submission"):
        return obj.submission.homework.lecture.course
    if hasattr(obj, "grade"):
        return obj.grade.submission.homework.lecture.course
    return None
