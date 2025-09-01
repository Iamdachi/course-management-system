from courses.models import Course, User, Role
from rest_framework.exceptions import PermissionDenied, NotFound

def add_user_to_course(course: Course, user: User, role: Role, acting_user: User):
    """Add a user (teacher/student) to a course, enforcing rules."""
    if not course.teachers.filter(id=acting_user.id).exists():
        raise PermissionDenied("Only course teachers can modify this course.")

    if user.role != role:
        raise ValueError(f"User must have role {role}.")
    relation = course.teachers if role == Role.TEACHER else course.students
    relation.add(user)
    return user

def remove_user_from_course(course: Course, user: User, role: Role, acting_user: User):
    """Remove a user (teacher/student) from a course, enforcing rules."""
    if not course.teachers.filter(id=acting_user.id).exists():
        raise PermissionDenied("Only course teachers can modify this course.")

    if user.role != role:
        raise ValueError(f"User must have role {role}.")
    relation = course.teachers if role == Role.TEACHER else course.students
    relation.remove(user)
    return user

def get_course_users(course: Course, role: Role):
    """Return all users of a given role in a course."""
    relation = course.teachers if role == Role.TEACHER else course.students
    return relation.all()

def create_lecture_for_course(course: Course, data: dict, acting_user: User, LectureModel):
    """Create a lecture under a course, ensuring only teachers can do it."""
    if acting_user not in course.teachers.all():
        raise PermissionDenied("Only course teachers can add lectures.")
    lecture = LectureModel.objects.create(course=course, **data)
    return lecture


def get_teaching_courses(user):
    """Return courses taught by the given user, enforcing teacher role."""
    if user.role != Role.TEACHER:
        raise PermissionDenied("Only teachers can view teaching courses.")
    return user.teaching_courses.all()

def get_enrolled_courses(user):
    """Return courses a student is enrolled in, enforcing student role."""
    if user.role != Role.STUDENT:
        raise PermissionDenied("Only students can view enrolled courses.")
    return user.enrolled_courses.all()