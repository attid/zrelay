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
    async def get_all_api_keys(self) -> List[ApiKey]:
        pass

    @abstractmethod
    async def update_api_key_status(self, key_id: str, enabled: bool) -> None:
        pass

    @abstractmethod
    async def get_recent_logs(self, limit: int = 50) -> List[UsageLog]:
        pass

    @abstractmethod
    async def get_stats_summary(self) -> Dict[str, Any]:
        pass
