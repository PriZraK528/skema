"""OpenAPI fuzzing via Schemathesis (run explicitly: pytest tests/test_schemathesis.py -q)."""

import pytest
import schemathesis
from hypothesis import settings as hypothesis_settings

schema = schemathesis.openapi.from_asgi("/openapi.json", app_import="app.main:app")


@schema.parametrize()
@hypothesis_settings(max_examples=15, deadline=None)
@pytest.mark.slow
def test_api_fuzz(case):
    case.call_and_validate()
