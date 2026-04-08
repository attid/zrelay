from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.api_key import ApiKey
from src.domain.entities.usage_log import UsageLog

class RepositoryPort(ABC):
    """
    Интерфейс для работы с постоянным хранилищем (БД)
    """
    @abstractmethod
    async def get_api_key(self, key: str) -> Optional[ApiKey]:
        pass

    @abstractmethod
    async def save_usage_log(self, log: UsageLog) -> None:
        pass

    @abstractmethod
    async def init_db(self) -> None:
        pass
