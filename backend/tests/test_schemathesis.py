"""OpenAPI fuzzing via Schemathesis (run explicitly: pytest tests/test_schemathesis.py -q)."""

import uuid

import pytest
import schemathesis
from hypothesis import settings as hypothesis_settings
from schemathesis.checks import CHECKS

from app.main import app

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@schemathesis.hook
def before_call(context, case, kwargs):
    if case.method == "POST" and case.path == "/api/auth/register":
        case.body = {
            "email": f"fuzz-{uuid.uuid4().hex}@example.com",
            "full_name": "Test User",
            "password": "password123",
            "phone": "+79001234567",
            "role": "patient",
            "specialization": None,
            "clinic_key": None,
        }


@schema.parametrize()
@hypothesis_settings(max_examples=15, deadline=None)
@pytest.mark.slow
def test_api_fuzz(case):
    response = case.call()
    case.validate_response(
        response,
        excluded_checks=[CHECKS.get_one("unsupported_method")],
    )
