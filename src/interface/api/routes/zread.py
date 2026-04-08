from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service
from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
import uuid
from typing import Optional

router = APIRouter(prefix="/v1/zread", tags=["Zread"])

class RepoRequest(BaseModel):
    repo: str = Field(..., description="owner/repo")

class SearchDocRequest(RepoRequest):
    query: str = Field(..., description="Поисковый запрос")

class ReadFileRequest(RepoRequest):
    path: str = Field(..., description="Путь к файлу")

@router.post("/search-doc", response_model=ToolResult)
async def search_doc(
    request_data: SearchDocRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service = Depends(get_zrelay_service)
):
    return await service.call_tool(
        tool_name="zread", operation="search_doc", payload=request_data.model_dump(),
        client_key_id=api_key.id, request_id=str(uuid.uuid4()), route=str(request.url.path)
    )

@router.post("/repo-structure", response_model=ToolResult)
async def repo_structure(
    request_data: RepoRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service = Depends(get_zrelay_service)
):
    return await service.call_tool(
        tool_name="zread", operation="get_repo_structure", payload=request_data.model_dump(),
        client_key_id=api_key.id, request_id=str(uuid.uuid4()), route=str(request.url.path)
    )

@router.post("/read-file", response_model=ToolResult)
async def read_file(
    request_data: ReadFileRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service = Depends(get_zrelay_service)
):
    return await service.call_tool(
        tool_name="zread", operation="read_file", payload=request_data.model_dump(),
        client_key_id=api_key.id, request_id=str(uuid.uuid4()), route=str(request.url.path)
    )
