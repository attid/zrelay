from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service
from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
import uuid

router = APIRouter(prefix="/v1/reader", tags=["Reader"])

class ReadWebRequest(BaseModel):
    url: str = Field(..., description="URL веб-страницы для чтения")

@router.post("/read-web", response_model=ToolResult)
async def read_web(
    request_data: ReadWebRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service = Depends(get_zrelay_service)
):
    request_id = str(uuid.uuid4())
    return await service.call_tool(
        tool_name="reader",
        operation="webReader",
        payload=request_data.model_dump(),
        client_key_id=api_key.id,
        request_id=request_id,
        route=str(request.url.path)
    )
