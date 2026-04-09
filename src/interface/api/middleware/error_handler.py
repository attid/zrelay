"""Error handlers for unified error format."""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.entities.api_error import ApiError, ErrorCode

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for unified error format."""

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Convert Starlette HTTPException to unified ApiError format."""
        code_map = {
            400: ErrorCode.INVALID_REQUEST,
            401: ErrorCode.AUTH_INVALID,
            403: ErrorCode.AUTH_DISABLED,
            404: ErrorCode.TOOL_NOT_FOUND,
            422: ErrorCode.VALIDATION_ERROR,
            500: ErrorCode.INTERNAL_ERROR,
        }
        error = ApiError(
            code=code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR),
            message=str(exc.detail) if isinstance(exc.detail, str) else "Error",
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error.to_dict(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Convert HTTPException to unified ApiError format."""
        code_map = {
            400: ErrorCode.INVALID_REQUEST,
            401: ErrorCode.AUTH_INVALID,
            403: ErrorCode.AUTH_DISABLED,
            404: ErrorCode.TOOL_NOT_FOUND,
            422: ErrorCode.VALIDATION_ERROR,
            500: ErrorCode.INTERNAL_ERROR,
        }
        error = ApiError(
            code=code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR),
            message=str(exc.detail) if isinstance(exc.detail, str) else "Error",
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error.to_dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        error = ApiError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            details={"errors": exc.errors()},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception("Unhandled exception: %s", exc)
        error = ApiError(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.to_dict(),
        )
