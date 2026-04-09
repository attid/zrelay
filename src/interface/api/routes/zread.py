import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service

router = APIRouter(prefix="/v1/zread", tags=["Zread"])


class RepoRequest(BaseModel):
    repo: str = Field(..., description="GitHub repository: owner/repo")


class SearchDocRequest(RepoRequest):
    query: str = Field(..., description="Search keywords or question")
    language: str = Field("en", description="Language: zh or en")


class ReadFileRequest(RepoRequest):
    path: str = Field(..., description="Relative file path (e.g. src/index.ts)")


class RepoStructureRequest(RepoRequest):
    dir_path: str = Field("/", description="Directory path to inspect")


@router.post("/search-doc", response_model=ToolResult)
async def search_doc(
    request_data: SearchDocRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    payload = {"repo_name": request_data.repo, "query": request_data.query}
    if request_data.language:
        payload["language"] = request_data.language
    return await service.call_tool(
        tool_name="zread",
        operation="search_doc",
        payload=payload,
        client_key_id=api_key.id,
        request_id=str(uuid.uuid4()),
        route=str(request.url.path),
    )


@router.post("/repo-structure", response_model=ToolResult)
async def repo_structure(
    request_data: RepoStructureRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    payload = {"repo_name": request_data.repo}
    if request_data.dir_path and request_data.dir_path != "/":
        payload["dir_path"] = request_data.dir_path
    return await service.call_tool(
        tool_name="zread",
        operation="get_repo_structure",
        payload=payload,
        client_key_id=api_key.id,
        request_id=str(uuid.uuid4()),
        route=str(request.url.path),
    )


@router.post("/read-file", response_model=ToolResult)
async def read_file(
    request_data: ReadFileRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    payload = {"repo_name": request_data.repo, "file_path": request_data.path}
    return await service.call_tool(
        tool_name="zread",
        operation="read_file",
        payload=payload,
        client_key_id=api_key.id,
        request_id=str(uuid.uuid4()),
        route=str(request.url.path),
    )
