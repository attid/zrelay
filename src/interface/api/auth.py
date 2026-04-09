from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.domain.entities.api_error import ErrorCode
from src.domain.entities.api_key import ApiKey
from src.infrastructure.config import settings
from src.infrastructure.repositories.sqlite_repository import SQLiteRepository

# Глобальный экземпляр репозитория (будет инициализирован в lifespan)
_repository: Optional[SQLiteRepository] = None

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_repository() -> SQLiteRepository:
    global _repository
    if _repository is None:
        _repository = SQLiteRepository(settings.DATABASE_URL)
    return _repository


async def get_current_api_key(
    x_api_key: Optional[str] = Depends(API_KEY_HEADER),
    repo: SQLiteRepository = Depends(get_repository),
) -> ApiKey:
    """Validate API key from header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": ErrorCode.AUTH_MISSING, "message": "API Key required"}},
        )
    api_key = await repo.get_api_key(x_api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": ErrorCode.AUTH_INVALID, "message": "Invalid API Key"}},
        )
    if not api_key.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": ErrorCode.AUTH_DISABLED, "message": "API Key disabled"}},
        )
    return api_key
