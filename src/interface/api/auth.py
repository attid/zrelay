from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from src.domain.entities.api_key import ApiKey
from src.infrastructure.config import settings
from src.infrastructure.repositories.sqlite_repository import SQLiteRepository

# Глобальный экземпляр репозитория (будет инициализирован в lifspan)
_repository: Optional[SQLiteRepository] = None


def get_repository() -> SQLiteRepository:
    global _repository
    if _repository is None:
        _repository = SQLiteRepository(settings.DATABASE_URL)
    return _repository


async def get_current_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    repo: SQLiteRepository = Depends(get_repository),
) -> ApiKey:
    api_key = await repo.get_api_key(x_api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key
