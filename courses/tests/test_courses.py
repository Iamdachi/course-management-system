import pytest
from rest_framework.reverse import reverse

from .factories import CourseFactory  # you need this


@pytest.mark.django_db
def test_teacher_can_create_course(api_client, teacher):
    api_client.force_authenticate(user=teacher)
    resp = api_client.post(
        "/api/v1/courses/",
        {"title": "Algebra 101", "description": "Math basics"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["title"] == "Algebra 101"


@pytest.mark.django_db
def test_student_cannot_create_course(api_client, student):
    api_client.force_authenticate(user=student)
    resp = api_client.post(
        "/api/v1/courses/",
        {"title": "Illegal course"},
        format="json",
    )
    assert resp.status_code == 403
