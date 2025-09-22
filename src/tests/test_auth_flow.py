import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_register_and_login():
    c = APIClient()
    r = c.post("/api/auth/register", {
        "email": "new@test.com", "password": "secret123", "password2": "secret123"
    }, format="json")
    assert r.status_code == 201
    r = c.post("/api/auth/login", {
        "email": "new@test.com", "password": "secret123"
    }, format="json")
    assert r.status_code == 200
    assert "access" in r.data and "refresh" in r.data

@pytest.mark.django_db
def test_me_requires_auth():
    c = APIClient()
    r = c.get("/api/auth/users/me")
    assert r.status_code in (401, 403)

@pytest.mark.django_db
def test_me_ok(user, bearer):
    c = APIClient()
    c = bearer(c, user)
    r = c.get("/api/auth/users/me")
    assert r.status_code == 200
    assert r.data["email"] == "u@test.com"
