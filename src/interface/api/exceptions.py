"""Custom exceptions for API errors."""

from src.domain.entities.api_error import ApiError


class ApiException(Exception):
    """Custom exception that formats errors in ApiError format."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ):
        self.api_error = ApiError(code=code, message=message, details=details)
        self.status_code = status_code
        super().__init__(message)
