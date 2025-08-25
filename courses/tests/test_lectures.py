import pytest
from django.urls import reverse
from rest_framework import status

from .factories import (
    TeacherFactory,
    StudentFactory,
    CourseFactory,
    LectureFactory,
    HomeworkFactory,
)


@pytest.mark.django_db
def test_teacher_can_list_lectures(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    LectureFactory.create_batch(3, course=course)
    api_client.force_authenticate(user=teacher)

    url = reverse("lecture-list")
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 3


@pytest.mark.django_db
def test_student_can_list_only_their_lectures(api_client, student):
    course = CourseFactory(students=[student])
    LectureFactory.create_batch(2, course=course)
    # lectures from another course (not enrolled)
    LectureFactory.create_batch(2)

    api_client.force_authenticate(user=student)
    url = reverse("lecture-list")
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 2


@pytest.mark.django_db
def test_teacher_can_create_lecture(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    api_client.force_authenticate(user=teacher)

    url = reverse("course-lectures", args=[course.id])  # nested route
    resp = api_client.post(
        url,
        {"topic": "Intro Lecture"},  # only topic
        format="json",
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["topic"] == "Intro Lecture"
    assert str(resp.data["course"]) == str(course.id)


@pytest.mark.django_db
def test_student_cannot_create_lecture(api_client, student):
    course = CourseFactory(students=[student])
    api_client.force_authenticate(user=student)

    url = reverse("course-lectures", args=[course.id])  # nested under course
    resp = api_client.post(
        url,
        {"topic": "Should Fail"},
        format="json",
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_homeworks_list(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)
    HomeworkFactory.create_batch(2, lecture=lecture)

    api_client.force_authenticate(user=teacher)
    url = reverse("lecture-homeworks", args=[lecture.id])
    resp = api_client.get(url)

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_teacher_can_add_homework(api_client, teacher):
    course = CourseFactory(teachers=[teacher])
    lecture = LectureFactory(course=course)

    api_client.force_authenticate(user=teacher)
    url = reverse("lecture-homeworks", args=[lecture.id])  # nested route
    resp = api_client.post(
        url,
        {"description": "Solve problems 1–5"},
        format="json",
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["description"] == "Solve problems 1–5"
    assert str(resp.data["lecture"]) == str(lecture.id)


@pytest.mark.django_db
def test_student_cannot_add_homework(api_client, student):
    course = CourseFactory(students=[student])
    lecture = LectureFactory(course=course)

    api_client.force_authenticate(user=student)
    url = reverse("lecture-homeworks", args=[lecture.id])
    resp = api_client.post(
        url,
        {"description": "Should fail"},
        format="json",
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN
