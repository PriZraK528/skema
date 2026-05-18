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


def _create_slot(client: TestClient, doctor_headers: dict, starts_at: datetime) -> None:
    ends_at = starts_at + timedelta(minutes=30)
    r = client.post(
        "/api/doctors/1/schedule/slots",
        headers=doctor_headers,
        json={
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        },
    )
    assert r.status_code == 201, r.text


def test_patient_can_book_and_cancel(client: TestClient):
    doctor_token = _login(client, "doctor@clinic.example")
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
    starts_at = _next_weekday_morning()
    _create_slot(client, doctor_headers, starts_at)

    token = _login(client, "patient@clinic.example")
    headers = {"Authorization": f"Bearer {token}"}

    book = client.post(
        "/api/appointments",
        headers=headers,
        json={"doctor_id": 1, "starts_at": starts_at.isoformat(), "note": "Test visit"},
    )
    assert book.status_code == 201, book.text
    appt_id = book.json()["id"]

    cancel = client.post(f"/api/appointments/{appt_id}/cancel", headers=headers)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"


def test_doctor_can_assign_appointment(client: TestClient):
    token = _login(client, "doctor@clinic.example")
    headers = {"Authorization": f"Bearer {token}"}
    starts_at = _next_weekday_morning() + timedelta(hours=1)
    _create_slot(client, headers, starts_at)

    r = client.post(
        "/api/appointments/assign",
        headers=headers,
        json={"patient_id": 1, "starts_at": starts_at.isoformat(), "note": "Assigned by doctor"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["patient_id"] == 1


def test_no_slots_without_doctor_create(client: TestClient):
    token = _login(client, "patient@clinic.example")
    headers = {"Authorization": f"Bearer {token}"}
    starts_at = _next_weekday_morning() + timedelta(hours=3)

    book = client.post(
        "/api/appointments",
        headers=headers,
        json={"doctor_id": 1, "starts_at": starts_at.isoformat()},
    )
    assert book.status_code == 409
