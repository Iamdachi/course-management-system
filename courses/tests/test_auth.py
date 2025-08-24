import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register(api_client):
    url = reverse("register")  # safer than "/api/v1/auth/register/"
    resp = api_client.post(
        url,
        {"username": "newuser", "email": "n@example.com", "password": "pass", "role": "student"},
        format="json",
    )
    assert resp.status_code == 201




@pytest.mark.django_db
def test_login(api_client, teacher):
    url = reverse("token_obtain_pair")  # maps to /token/
    resp = api_client.post(
        url,
        {"username": teacher.username, "password": "password123"},  # match factory password
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data
