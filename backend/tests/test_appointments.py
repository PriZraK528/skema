from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def _login(client: TestClient, email: str) -> str:
    r = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    return r.json()["access_token"]


def _next_weekday_morning() -> datetime:
    now = datetime.now(timezone.utc)
    dt = now + timedelta(days=1)
    while dt.weekday() > 4:
        dt += timedelta(days=1)
    return dt.replace(hour=10, minute=0, second=0, microsecond=0)


def test_patient_can_book_and_cancel(client: TestClient):
    token = _login(client, "patient@clinic.example")
    headers = {"Authorization": f"Bearer {token}"}
    starts_at = _next_weekday_morning().isoformat()

    book = client.post(
        "/api/appointments",
        headers=headers,
        json={"doctor_id": 1, "starts_at": starts_at, "note": "Test visit"},
    )
    assert book.status_code == 201, book.text
    appt_id = book.json()["id"]

    cancel = client.post(f"/api/appointments/{appt_id}/cancel", headers=headers)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"


def test_doctor_can_assign_appointment(client: TestClient):
    token = _login(client, "doctor@clinic.example")
    headers = {"Authorization": f"Bearer {token}"}
    starts_at = (_next_weekday_morning() + timedelta(hours=1)).isoformat()

    r = client.post(
        "/api/appointments/assign",
        headers=headers,
        json={"patient_id": 1, "starts_at": starts_at, "note": "Assigned by doctor"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["patient_id"] == 1
