import pytest
from rest_framework import status
from django.urls import reverse

from courses.tests.factories import (
    CourseFactory,
    LectureFactory,
    HomeworkFactory,
    HomeworkSubmissionFactory,
    StudentFactory,
)


@pytest.mark.django_db
def test_student_can_submit_homework(api_client, student):
    course = CourseFactory(students=[student])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)

    api_client.force_authenticate(user=student)
    url = reverse("homework-submissions", args=[homework.id])
    resp = api_client.post(
        url,
        {
            "content": "My answers",
        },
        format="multipart",
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["content"] == "My answers"


@pytest.mark.django_db
def test_teacher_can_list_submissions(api_client, teacher):
    # Create course, lecture, homework
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)

    # Create two student submissions
    students = [StudentFactory() for _ in range(2)]
    for student in students:
        HomeworkSubmissionFactory(homework=homework, student=student)

    # Authenticate as teacher and hit endpoint
    api_client.force_authenticate(user=teacher)
    url = reverse("homework-submissions", args=[homework.id])
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_teacher_can_retrieve_submission(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)
    submission = HomeworkSubmissionFactory(homework=homework)

    api_client.force_authenticate(user=teacher)
    url = reverse("submission-detail", args=[submission.id])
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["id"]
