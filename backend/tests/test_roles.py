import pytest
from fastapi.testclient import TestClient

from app.constants import SEED_PASSWORD


def _login(client: TestClient, email: str, password: str = SEED_PASSWORD) -> str:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_register_rejects_admin_role(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "bad@example.com",
            "password": SEED_PASSWORD,
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
            "password": SEED_PASSWORD,
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


def test_doctor_registration_requires_clinic_key(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "doc-no-key@example.com",
            "password": SEED_PASSWORD,
            "role": "doctor",
            "full_name": "Новый Врач",
            "phone": "+79990001124",
            "specialization": "Терапевт",
        },
    )
    assert r.status_code == 422


def test_doctor_registration_rejects_wrong_clinic_key(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "doc-bad-key@example.com",
            "password": SEED_PASSWORD,
            "role": "doctor",
            "full_name": "Новый Врач",
            "phone": "+79990001125",
            "specialization": "Терапевт",
            "clinic_key": "wrong-key",
        },
    )
    assert r.status_code == 403


def test_doctor_registration_with_valid_clinic_key(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "doc-new@example.com",
            "password": SEED_PASSWORD,
            "role": "doctor",
            "full_name": "Новый Врач",
            "phone": "+79990001126",
            "specialization": "Кардиолог",
            "clinic_key": "test-clinic-key",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["user"]["role"] == "doctor"


def test_specializations_list_is_public(client: TestClient):
    r = client.get("/api/auth/specializations")
    assert r.status_code == 200
    assert "Терапевт" in r.json()


def test_unread_notifications_count(client: TestClient):
    token = _login(client, "patient@clinic.example")
    r = client.get(
        "/api/notifications/unread-count",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "count" in r.json()
    assert r.json()["count"] >= 0
