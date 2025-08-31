import pytest
from rest_framework import status
from django.urls import reverse

from courses.tests.factories import (
    CourseFactory,
    LectureFactory,
    HomeworkFactory,
    HomeworkSubmissionFactory,
    TeacherFactory,
    StudentFactory,
)


@pytest.mark.django_db
def test_teacher_can_create_and_list_grades(api_client):
    teacher = TeacherFactory()
    student = StudentFactory()
    course = CourseFactory(teachers=[teacher], students=[student])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)
    submission = HomeworkSubmissionFactory(homework=homework, student=student)

    api_client.force_authenticate(user=teacher)

    # List (should be empty initially)
    list_url = reverse("submission-grades", args=[submission.id])
    resp = api_client.get(list_url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == []

    # Create
    payload = {"value": 95, "feedback": "Great work"}
    resp = api_client.post(list_url, payload)
    assert resp.status_code == status.HTTP_201_CREATED
    grade_id = resp.data["id"]
    assert resp.data["value"] == 95
    assert resp.data["feedback"] == "Great work"

    # List again (should contain one grade)
    resp = api_client.get(list_url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_teacher_can_retrieve_update_and_delete_grade(api_client):
    teacher = TeacherFactory()
    student = StudentFactory()
    course = CourseFactory(teachers=[teacher], students=[student])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)
    submission = HomeworkSubmissionFactory(homework=homework, student=student)

    api_client.force_authenticate(user=teacher)

    # Create a grade
    list_url = reverse("submission-grades", args=[submission.id])
    resp = api_client.post(list_url, {"value": 95, "feedback": "Great work"})
    grade_id = resp.data["id"]

    detail_url = reverse("grade-detail", args=[grade_id])

    # Retrieve
    resp = api_client.get(detail_url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["value"] == 95

    # Update (PATCH)
    resp = api_client.patch(detail_url, {"value": 88})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["value"] == 88

    # Delete
    resp = api_client.delete(detail_url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    resp = api_client.get(detail_url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
