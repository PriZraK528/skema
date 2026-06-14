from datetime import datetime, timedelta, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.constants import SEED_PASSWORD
from app.models import UserRole
from app.schemas.auth import RegisterRequest


@settings(max_examples=50, deadline=None)
@given(role=st.text(min_size=1, max_size=40))
def test_register_role_rejects_unknown_strings(role: str):
    if role in {r.value for r in UserRole}:
        return
    with pytest.raises(Exception):
        RegisterRequest(
            email="fuzz@example.com",
            password=SEED_PASSWORD,
            role=role,
            full_name="Fuzz User",
            phone="+79990000000",
        )


@settings(max_examples=30, deadline=None)
@given(minutes=st.integers(min_value=5, max_value=480))
def test_availability_slot_duration_validation(minutes: int):
    from app.schemas.schedule import AvailabilitySlotCreate

    start = datetime.now(timezone.utc) + timedelta(days=2)
    slot = AvailabilitySlotCreate(starts_at=start, duration_minutes=minutes)
    assert slot.duration_minutes == minutes
