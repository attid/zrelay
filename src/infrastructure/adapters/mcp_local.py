import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.application.ports.mcp_port import MCPPort
from src.domain.entities.tool_result import ToolResult

logger = logging.getLogger(__name__)


class MCPLocalAdapter(MCPPort):
    def __init__(self, command: str, args: List[str], env: Dict[str, str]):
        self.params = StdioServerParameters(
            command=command, args=args, env={**os.environ, **env}
        )

    async def invoke(
        self,
        operation: str,
        payload: Dict[str, Any],
        request_id: str,
        timeout: Optional[int] = None,
    ) -> ToolResult:
        try:
            async with stdio_client(self.params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await asyncio.wait_for(
                        session.call_tool(operation, arguments=payload),
                        timeout=timeout or 60,  # Vision может быть медленным
                    )

                    data = {}
                    if hasattr(result, "content"):
                        data = {
                            "content": [
                                c.text for c in result.content if hasattr(c, "text")
                            ]
                        }

                    return ToolResult(
                        ok=not result.isError,
                        tool="vision",
                        operation=operation,
                        request_id=request_id,
                        data=data,
                        error={"message": str(result)} if result.isError else None,
                        meta={"is_local": True},
                    )
        except asyncio.TimeoutError:
            return ToolResult(
                ok=False,
                tool="vision",
                operation=operation,
                request_id=request_id,
                error={"code": "UPSTREAM_TIMEOUT", "message": "Vision MCP timed out"},
            )
        except Exception as e:
            logger.error(f"MCP Local Error: {e}", exc_info=True)
            return ToolResult(
                ok=False,
                tool="vision",
                operation=operation,
                request_id=request_id,
                error={"code": "UPSTREAM_ERROR", "message": str(e)},
            )
