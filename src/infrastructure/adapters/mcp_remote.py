import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

from src.application.ports.mcp_port import MCPPort
from src.domain.entities.tool_result import ToolResult

logger = logging.getLogger(__name__)


class MCPRemoteAdapter(MCPPort):
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    @staticmethod
    def _create_sse_client(
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        auth: httpx.Auth | None = None,
    ) -> httpx.AsyncClient:
        """Create httpx client tuned for SSE — HTTP/2 required for z.ai."""
        return httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            auth=auth,
            follow_redirects=True,
            http2=True,
        )

    async def invoke(
        self,
        operation: str,
        payload: Dict[str, Any],
        request_id: str,
        timeout: Optional[int] = None,
    ) -> ToolResult:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        logger.info(f"Invoking remote tool {operation} at {self.url}")

        try:
            # SSE connections need long timeouts
            # timeout — general httpx timeout, sse_read_timeout — SSE stream read timeout
            # Custom factory disables httpx response buffering for SSE compatibility
            async with sse_client(
                url=self.url,
                headers=headers,
                timeout=60,
                sse_read_timeout=300,
                httpx_client_factory=self._create_sse_client,
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await asyncio.wait_for(session.initialize(), timeout=10)

                    result = await asyncio.wait_for(
                        session.call_tool(operation, arguments=payload),
                        timeout=timeout or 45,
                    )

                    data = {
                        "content": [
                            c.text for c in result.content if hasattr(c, "text")
                        ]
                    }
                    logger.info(f"Remote tool {operation} success")

                    return ToolResult(
                        ok=not result.isError,
                        tool=self.url.split("/")[-2],
                        operation=operation,
                        request_id=request_id,
                        data=data,
                        error={"message": str(result)} if result.isError else None,
                        meta={"is_remote": True},
                    )
        except asyncio.TimeoutError:
            return ToolResult(
                ok=False,
                tool="remote",
                operation=operation,
                request_id=request_id,
                error={"code": "UPSTREAM_TIMEOUT", "message": "Upstream timed out"},
            )
        except Exception as e:
            logger.error(f"MCP Remote Error: {e}", exc_info=True)
            return ToolResult(
                ok=False,
                tool="remote",
                operation=operation,
                request_id=request_id,
                error={"code": "UPSTREAM_ERROR", "message": str(e)},
            )
