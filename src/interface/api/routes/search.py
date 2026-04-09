import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service

router = APIRouter(prefix="/v1/search", tags=["Search"])


class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Search query (max 70 chars recommended)")
    recency: str = Field("noLimit", description="Time filter: oneDay, oneWeek, oneMonth, oneYear, noLimit")
    content_size: str = Field("medium", description="Summary size: medium (400-600 words) or high (2500 words)")
    location: str = Field("us", description="Region: cn (China) or us (other)")


@router.post("/web-search", response_model=ToolResult)
async def web_search(
    request_data: WebSearchRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    request_id = str(uuid.uuid4())
    # Map to z.ai MCP schema
    payload = {
        "search_query": request_data.query,
        "search_recency_filter": request_data.recency,
        "content_size": request_data.content_size,
        "location": request_data.location,
    }
    return await service.call_tool(
        tool_name="search",
        operation="web_search_prime",
        payload=payload,
        client_key_id=api_key.id,
        request_id=request_id,
        route=str(request.url.path),
    )
