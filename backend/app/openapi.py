from __future__ import annotations

from fastapi.openapi.utils import get_openapi

ERROR_BODY_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "object"}},
            ]
        }
    },
    "required": ["detail"],
}


def _error_response(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/json": {"schema": ERROR_BODY_SCHEMA}},
    }


COMMON_ERROR_RESPONSES: dict[int, dict] = {
    400: _error_response("Bad request"),
    401: _error_response("Not authenticated"),
    403: _error_response("Forbidden"),
    404: _error_response("Not found"),
    409: _error_response("Conflict"),
    422: _error_response("Validation error"),
}


def apply_common_responses(openapi_schema: dict) -> dict:
    paths = openapi_schema.get("paths", {})
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method == "parameters" or not isinstance(operation, dict):
                continue
            responses = operation.setdefault("responses", {})
            for status_code, response in COMMON_ERROR_RESPONSES.items():
                responses[str(status_code)] = response
    return openapi_schema


def build_openapi(app) -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = apply_common_responses(schema)
    return app.openapi_schema
