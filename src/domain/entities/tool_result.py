from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    ok: bool
    tool: str
    operation: str
    request_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    meta: Dict[str, Any] = {}
