from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.domain.entities.tool_result import ToolResult


class MCPPort(ABC):
    """
    Интерфейс для взаимодействия с MCP серверами (Vision, Search и т.д.)
    """

    @abstractmethod
    async def invoke(
        self,
        operation: str,
        payload: Dict[str, Any],
        request_id: str,
        timeout: Optional[int] = None,
    ) -> ToolResult:
        pass
