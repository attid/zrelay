from typing import Any, Dict, Optional
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from src.application.ports.mcp_port import MCPPort
from src.domain.entities.tool_result import ToolResult
import logging

logger = logging.getLogger(__name__)

class MCPRemoteAdapter(MCPPort):
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    async def invoke(
        self, 
        operation: str, 
        payload: Dict[str, Any], 
        request_id: str,
        timeout: Optional[int] = None
    ) -> ToolResult:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with sse_client(url=self.url, headers=headers) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # В MCP SDK вызов инструмента идет через call_tool
                    # Предполагаем, что operation соответствует имени инструмента
                    result = await asyncio.wait_for(
                        session.call_tool(operation, arguments=payload),
                        timeout=timeout or 30
                    )
                    
                    # Извлекаем данные из ответа (Content в MCP)
                    data = {}
                    if hasattr(result, 'content'):
                        # Собираем текстовый контент в один словарь/строку
                        data = {"content": [c.text for c in result.content if hasattr(c, 'text')]}
                    
                    return ToolResult(
                        ok=not result.isError,
                        tool=self.url.split('.')[0].split('/')[-1], # Извлекаем имя из URL
                        operation=operation,
                        request_id=request_id,
                        data=data,
                        error={"message": str(result)} if result.isError else None,
                        meta={"is_remote": True}
                    )
        except asyncio.TimeoutError:
            return ToolResult(
                ok=False, tool="remote", operation=operation, request_id=request_id,
                error={"code": "UPSTREAM_TIMEOUT", "message": "Upstream timed out"}
            )
        except Exception as e:
            logger.error(f"MCP Remote Error: {e}", exc_info=True)
            return ToolResult(
                ok=False, tool="remote", operation=operation, request_id=request_id,
                error={"code": "UPSTREAM_ERROR", "message": str(e)}
            )
