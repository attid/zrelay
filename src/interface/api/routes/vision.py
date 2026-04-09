import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.domain.entities.api_key import ApiKey
from src.domain.entities.tool_result import ToolResult
from src.interface.api.auth import get_current_api_key
from src.interface.api.dependencies import get_zrelay_service

router = APIRouter(prefix="/v1/vision", tags=["Vision"])


class VisionRequest(BaseModel):
    path: str = Field(..., description="Путь к изображению или видео")
    prompt: Optional[str] = Field(None, description="Промпт для анализа")


class UIDiffRequest(BaseModel):
    before_path: str = Field(..., description="Путь к изображению ДО")
    after_path: str = Field(..., description="Путь к изображению ПОСЛЕ")
    prompt: Optional[str] = Field(None, description="Промпт для сравнения")


@router.post("/image-analysis", response_model=ToolResult)
async def image_analysis(
    request_data: VisionRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    return await service.call_tool(
        tool_name="vision",
        operation="image_analysis",
        payload=request_data.model_dump(),
        client_key_id=api_key.id,
        request_id=str(uuid.uuid4()),
        route=str(request.url.path),
    )


@router.post("/ui-diff-check", response_model=ToolResult)
async def ui_diff_check(
    request_data: UIDiffRequest,
    request: Request,
    api_key: ApiKey = Depends(get_current_api_key),
    service=Depends(get_zrelay_service),
):
    return await service.call_tool(
        tool_name="vision",
        operation="ui_diff_check",
        payload=request_data.model_dump(),
        client_key_id=api_key.id,
        request_id=str(uuid.uuid4()),
        route=str(request.url.path),
    )
