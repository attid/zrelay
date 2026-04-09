from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.ports.mcp_port import MCPPort
from src.application.ports.repository_port import RepositoryPort
from src.application.services.zrelay_service import ZRelayService
from src.domain.entities.tool_result import ToolResult


@pytest.mark.asyncio
async def test_zrelay_service_call_success():
    # Arrange
    mock_adapter = MagicMock(spec=MCPPort)
    mock_adapter.invoke = AsyncMock(
        return_value=ToolResult(
            ok=True,
            tool="test-tool",
            operation="op1",
            request_id="req-1",
            data={"res": "ok"},
        )
    )

    mock_repo = MagicMock(spec=RepositoryPort)
    mock_repo.save_usage_log = AsyncMock()

    service = ZRelayService(adapters={"test-tool": mock_adapter}, repository=mock_repo)

    # Act
    result = await service.call_tool(
        tool_name="test-tool",
        operation="op1",
        payload={},
        client_key_id="key-1",
        request_id="req-1",
        route="/test",
    )

    # Assert
    assert result.ok is True
    assert result.data == {"res": "ok"}
    mock_adapter.invoke.assert_called_once()
    mock_repo.save_usage_log.assert_called_once()


@pytest.mark.asyncio
async def test_zrelay_service_tool_not_found():
    mock_repo = MagicMock(spec=RepositoryPort)
    service = ZRelayService(adapters={}, repository=mock_repo)

    result = await service.call_tool(
        tool_name="unknown",
        operation="op1",
        payload={},
        client_key_id="key-1",
        request_id="req-1",
        route="/test",
    )

    assert result.ok is False
    assert result.error["code"] == "TOOL_NOT_FOUND"
