import pytest
from rest_framework import status
from django.urls import reverse

from courses.tests.factories import CourseFactory, LectureFactory, HomeworkFactory


@pytest.mark.django_db
def test_teacher_can_add_homework(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)

    api_client.force_authenticate(user=teacher)
    url = reverse("lecture-homeworks", args=[lecture.id])
    resp = api_client.post(
        url,
        {"description": "Solve problems 1–5"},
        format="json",
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["description"] == "Solve problems 1–5"


@pytest.mark.django_db
def test_student_cannot_add_homework(api_client, student):
    course = CourseFactory(students=[student])
    lecture = LectureFactory(course=course)

    api_client.force_authenticate(user=student)
    url = reverse("lecture-homeworks", args=[lecture.id])
    resp = api_client.post(
        url,
        {"description": "Illegal homework"},
        format="json",
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_teacher_can_list_homeworks(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    HomeworkFactory.create_batch(2, lecture=lecture)

    api_client.force_authenticate(user=teacher)
    url = reverse("lecture-homeworks", args=[lecture.id])
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_teacher_can_retrieve_homework(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)

    api_client.force_authenticate(user=teacher)
    url = reverse("homework-detail", args=[homework.id])
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["id"] == str(homework.id)


@pytest.mark.django_db
def test_teacher_can_update_homework(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)

    api_client.force_authenticate(user=teacher)
    url = reverse("homework-detail", args=[homework.id])
    resp = api_client.patch(url, {"description": "Updated HW"}, format="json")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["description"] == "Updated HW"


@pytest.mark.django_db
def test_teacher_can_delete_homework(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    homework = HomeworkFactory(lecture=lecture)

    api_client.force_authenticate(user=teacher)
    url = reverse("homework-detail", args=[homework.id])
    resp = api_client.delete(url)

    assert resp.status_code == status.HTTP_204_NO_CONTENT
