import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service

router = APIRouter(prefix="/v1/reader", tags=["Reader"])


class ReadWebRequest(BaseModel):
    url: str = Field(..., description="URL of the website to fetch and read")
    timeout: int = Field(20, description="Request timeout in seconds")
    return_format: str = Field("markdown", description="Response format: markdown or text")


@router.post("/read-web", response_model=ToolResult)
async def read_web(
    request_data: ReadWebRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    request_id = str(uuid.uuid4())
    return await service.call_tool(
        tool_name="reader",
        operation="webReader",
        payload=request_data.model_dump(),
        client_key_id=api_key.id,
        request_id=request_id,
        route=str(request.url.path),
    )
