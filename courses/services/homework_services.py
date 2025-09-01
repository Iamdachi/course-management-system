from courses.models import Homework, HomeworkSubmission, Role
from rest_framework.exceptions import PermissionDenied

def get_homeworks_for_user(user):
    """Return homeworks visible to the user."""
    if user.role == Role.TEACHER:
        return Homework.objects.filter(lecture__course__teachers=user)
    elif user.role == Role.STUDENT:
        return Homework.objects.filter(lecture__course__students=user)
    else:
        return Homework.objects.none()

def get_homework_submissions(homework):
    """Return all submissions for a homework."""
    return homework.submissions.select_related(
        "student", "homework__lecture__course"
    ).prefetch_related("grades")

def submit_homework(homework, student, data, serializer_class):
    """Create a new homework submission for a student."""
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    submission = serializer.save(homework=homework, student=student)
    return submission

def get_submissions_for_user(user):
    """Return homework submissions visible to the user."""
    if user.role == Role.TEACHER:
        return HomeworkSubmission.objects.filter(homework__lecture__course__teachers=user)
    elif user.role == Role.STUDENT:
        return HomeworkSubmission.objects.filter(student=user)
    return HomeworkSubmission.objects.none()

def get_submission_grades(submission):
    """Return all grades for a submission."""
    return submission.grades.select_related("teacher").prefetch_related("comments").all()

def add_grade_to_submission(submission, teacher, data, serializer_class):
    """Create a new grade for a submission."""
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    grade = serializer.save(submission=submission, teacher=teacher)
    return grade

def filter_submissions_for_user(user, homework_id=None, lecture_id=None, course_id=None):
    """Return submissions filtered by user role and optional IDs."""
    submissions = HomeworkSubmission.objects.for_user(user)

    if homework_id:
        submissions = submissions.filter(homework_id=homework_id)
    if lecture_id:
        submissions = submissions.filter(homework__lecture_id=lecture_id)
    if course_id:
        submissions = submissions.filter(homework__lecture__course_id=course_id)

    return submissions