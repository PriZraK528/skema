"""Property-based fuzzing of API inputs (roles, schedule, auth)."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

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
            password="Password123!",
            role=role,  # type: ignore[arg-type]
            full_name="Fuzz User",
            phone="+79990000000",
        )


@settings(max_examples=30, deadline=None)
@given(weekday=st.integers())
def test_schedule_weekday_validation(weekday: int):
    from app.schemas.schedule import ScheduleRuleCreate
    from datetime import time

    if 0 <= weekday <= 6:
        rule = ScheduleRuleCreate(
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        assert rule.weekday == weekday
    else:
        with pytest.raises(Exception):
            ScheduleRuleCreate(
                weekday=weekday,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )
