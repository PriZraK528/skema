import pytest
from fastapi.testclient import TestClient


def _login(client: TestClient, email: str, password: str = "Password123!") -> str:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_register_rejects_admin_role(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "bad@example.com",
            "password": "Password123!",
            "role": "admin",
            "full_name": "Bad Admin",
            "phone": "+79990001122",
        },
    )
    assert r.status_code == 422


def test_register_rejects_invalid_role_string(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "bad2@example.com",
            "password": "Password123!",
            "role": "superuser",
            "full_name": "Bad Role",
            "phone": "+79990001123",
        },
    )
    assert r.status_code == 422


def test_patient_cannot_list_users(client: TestClient):
    token = _login(client, "patient@clinic.example")
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_can_list_users(client: TestClient):
    token = _login(client, "admin@clinic.example")
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_patient_cannot_change_user_role(client: TestClient):
    patient_token = _login(client, "patient@clinic.example")
    r = client.patch(
        "/api/users/1/role",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"role": "admin"},
    )
    assert r.status_code == 403
