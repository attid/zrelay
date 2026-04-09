"""Standardized API error models."""

from typing import Any, Optional

from pydantic import BaseModel


class ApiError(BaseModel):
    """Standard error response format.

    Per golden-principles.md:
    {"error": {"code": "...", "message": "..."}}
    """

    code: str
    message: str
    details: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to nested error format."""
        return {"error": self.model_dump()}


class ErrorCode:
    """Predefined error codes for common scenarios."""

    # Authentication
    AUTH_MISSING = "auth_missing"
    AUTH_INVALID = "auth_invalid"
    AUTH_DISABLED = "auth_disabled"

    # Tool errors
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_ERROR = "tool_error"
    TOOL_TIMEOUT = "tool_timeout"

    # Request errors
    INVALID_REQUEST = "invalid_request"
    VALIDATION_ERROR = "validation_error"

    # Server errors
    INTERNAL_ERROR = "internal_error"
    UPSTREAM_ERROR = "upstream_error"
