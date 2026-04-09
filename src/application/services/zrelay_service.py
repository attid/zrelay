import logging
import time
from typing import Any, Dict, Optional

from src.application.ports.mcp_port import MCPPort
from src.application.ports.repository_port import RepositoryPort
from src.domain.entities.tool_result import ToolResult
from src.domain.entities.usage_log import UsageLog

logger = logging.getLogger(__name__)


class ZRelayService:
    def __init__(
        self,
        adapters: Dict[str, MCPPort],
        repository: RepositoryPort,
        enable_stats: bool = True,
    ):
        self.adapters = adapters
        self.repository = repository
        self.enable_stats = enable_stats

    async def call_tool(
        self,
        tool_name: str,
        operation: str,
        payload: Dict[str, Any],
        client_key_id: str,
        request_id: str,
        route: str,
        timeout: Optional[int] = None,
    ) -> ToolResult:
        adapter = self.adapters.get(tool_name)
        if not adapter:
            return ToolResult(
                ok=False,
                tool=tool_name,
                operation=operation,
                request_id=request_id,
                error={
                    "code": "TOOL_NOT_FOUND",
                    "message": f"Tool '{tool_name}' not configured",
                },
            )

        start_time = time.time()
        result = await adapter.invoke(operation, payload, request_id, timeout)
        duration_ms = int((time.time() - start_time) * 1000)

        if self.enable_stats:
            log = UsageLog(
                client_key_id=client_key_id,
                route=route,
                tool=tool_name,
                operation=operation,
                status_code=200 if result.ok else 500,  # Упрощенно
                duration_ms=duration_ms,
                request_id=request_id,
                success=result.ok,
                error_type=result.error.get("code") if result.error else None,
            )
            try:
                await self.repository.save_usage_log(log)
            except Exception as e:
                logger.error(f"Failed to save usage log: {e}")

        # Добавляем метрики в результат
        result.meta["duration_ms"] = duration_ms
        return result
