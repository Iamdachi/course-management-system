from rest_framework.exceptions import PermissionDenied

from courses.models import Lecture, Homework


def get_lecture_representation(instance, request=None):
    rep = {
        "id": instance.id,
        "course": instance.course.id,
        "topic": instance.topic,
        "presentation": None,
        "created_at": instance.created_at,
        "updated_at": instance.updated_at,
    }
    if instance.presentation and request is not None:
        rep["presentation"] = request.build_absolute_uri(instance.presentation.url)
    return rep


def get_lecture_homeworks(lecture: Lecture):
    """Return homeworks for a lecture with optimal prefetch/select."""
    return lecture.homeworks.select_related("lecture__course").prefetch_related("submissions")


def create_homework_for_lecture(lecture: Lecture, user, homework_data: dict):
    """Create a homework for the lecture if the user is a teacher."""
    if user not in lecture.course.teachers.all():
        raise PermissionDenied("Only course teachers can add homework.")

    homework = Homework.objects.create(lecture=lecture, **homework_data)
    return homework