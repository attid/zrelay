"""Tool result model with unified error format."""

from typing import Any, Optional

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool invocation.

    Maintains backward compatibility with ok/error/data fields.
    Errors are also formatted per golden-principles.md.
    """

    ok: bool = True
    tool: str = ""
    operation: str = ""
    request_id: str = ""
    data: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None
    error_detail: Optional[dict[str, Any]] = None  # Unified error format
    meta: dict[str, Any] = {}

    def set_error(self, code: str, message: str, details: Optional[dict] = None) -> None:
        """Set error in unified format."""
        self.ok = False
        self.error_detail = {"error": {"code": code, "message": message, "details": details}}
        self.error = {"code": code, "message": message}
