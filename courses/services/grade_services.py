from courses.models import Grade, GradeComment, Role
from rest_framework.exceptions import PermissionDenied, NotFound

def create_grade(submission, teacher, value, feedback=""):
    """Create a grade, ensuring the teacher has permissions."""
    if teacher.role != Role.TEACHER:
        raise PermissionDenied("Only teachers can assign grades.")
    grade = Grade.objects.create(
        submission=submission, teacher=teacher, value=value, feedback=feedback
    )
    return grade

def update_grade(grade: Grade, teacher, value, feedback=""):
    """Update a grade, ensuring the teacher remains the same."""
    if teacher.role != Role.TEACHER:
        raise PermissionDenied("Only teachers can update grades.")
    grade.value = value
    grade.feedback = feedback
    grade.save()
    return grade

def get_grade_comments(grade: Grade):
    """Return all comments for a given grade."""
    return grade.comments.select_related("author").all()

def add_grade_comment(grade: Grade, author, content):
    """Add a comment to a grade, enforcing any permission rules."""
    comment = GradeComment.objects.create(grade=grade, author=author, content=content)
    return comment

def create_grade_comment(author, grade, content):
    """Create a grade comment, enforcing permissions externally via DRF."""
    comment = GradeComment.objects.create(grade=grade, author=author, content=content)
    return comment

def get_visible_grade_comments(user):
    """
    Return all comments visible to the user.
    Teachers see comments on their course grades; students see their own comments.
    """
    return GradeComment.objects.for_user(user)