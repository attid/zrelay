from datetime import datetime
from typing import Optional, Any, Dict
from sqlmodel import Field, SQLModel
import uuid

class UsageLog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    client_key_id: str = Field(index=True)
    route: str
    tool: str
    operation: str
    status_code: int
    duration_ms: int
    request_id: str = Field(index=True)
    success: bool
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    error_type: Optional[str] = None
