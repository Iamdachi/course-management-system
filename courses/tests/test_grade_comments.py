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
    GradeFactory,
)


@pytest.mark.django_db
def test_teacher_can_create_and_list_grade_comments(api_client):
    teacher = TeacherFactory()
    student = StudentFactory()
    course = CourseFactory(teachers=[teacher], students=[student])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)
    submission = HomeworkSubmissionFactory(homework=homework, student=student)
    grade = GradeFactory(submission=submission, teacher=teacher, value=90)

    api_client.force_authenticate(user=teacher)

    list_url = reverse("grade-comments", args=[grade.id])
    resp = api_client.get(list_url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == []

    payload = {"content": "Nice feedback!"}
    resp = api_client.post(list_url, payload)
    assert resp.status_code == status.HTTP_201_CREATED
    comment_id = resp.data["id"]
    assert resp.data["content"] == "Nice feedback!"

    resp = api_client.get(list_url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_teacher_can_retrieve_update_and_delete_comment(api_client):
    teacher = TeacherFactory()
    student = StudentFactory()
    course = CourseFactory(teachers=[teacher], students=[student])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)
    submission = HomeworkSubmissionFactory(homework=homework, student=student)
    grade = GradeFactory(submission=submission, teacher=teacher, value=90)

    api_client.force_authenticate(user=teacher)

    list_url = reverse("grade-comments", args=[grade.id])
    resp = api_client.post(list_url, {"content": "Nice feedback!"})
    comment_id = resp.data["id"]

    detail_url = reverse("grade-comment-detail", args=[comment_id])

    resp = api_client.get(detail_url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["content"] == "Nice feedback!"

    resp = api_client.patch(detail_url, {"content": "Edited comment"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["content"] == "Edited comment"

    resp = api_client.delete(detail_url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = api_client.get(detail_url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
