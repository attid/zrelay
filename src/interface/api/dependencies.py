from typing import Dict
from src.application.services.zrelay_service import ZRelayService
from src.infrastructure.adapters.mcp_remote import MCPRemoteAdapter
from src.infrastructure.adapters.mcp_local import MCPLocalAdapter
from src.infrastructure.config import settings
from src.interface.api.auth import get_repository

def get_zrelay_service() -> ZRelayService:
    repo = get_repository()
    
    # Инициализация адаптеров
    # Search, Reader, Zread - удаленные через SSE
    # Vision - локальный через npx @z_ai/mcp-server vision
    common_env = {"Z_AI_API_KEY": settings.Z_AI_API_KEY, "Z_AI_MODE": "ZAI"}
    
    adapters = {
        "search": MCPRemoteAdapter(settings.SEARCH_MCP_URL, settings.Z_AI_API_KEY),
        "reader": MCPRemoteAdapter(settings.READER_MCP_URL, settings.Z_AI_API_KEY),
        "zread": MCPRemoteAdapter(settings.ZREAD_MCP_URL, settings.Z_AI_API_KEY),
        "vision": MCPLocalAdapter(command="npx", args=["-y", "@z_ai/mcp-server", "vision"], env=common_env)
    }
    
    return ZRelayService(
        adapters=adapters,
        repository=repo,
        enable_stats=settings.ENABLE_USAGE_STATS
    )
