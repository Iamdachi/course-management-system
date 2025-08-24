import pytest
from rest_framework.test import APIClient

from courses.tests.factories import TeacherFactory, StudentFactory, CourseFactory


@pytest.fixture
def api_client():
    """DRF test client"""
    return APIClient()


@pytest.fixture
def teacher(db):
    """A teacher user"""
    return TeacherFactory()


@pytest.fixture
def student(db):
    """A student user"""
    return StudentFactory()


@pytest.fixture
def course(db, teacher):
    """A course created by a teacher"""
    return CourseFactory()
