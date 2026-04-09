from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Any
import json

class Settings(BaseSettings):
    # API Keys
    Z_AI_API_KEY: str
    
    # App
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENABLE_USAGE_STATS: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///data/stats.db"
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin" # Change this in production!
    
    # Local Auth (JSON format for MVP)
    # [{"id": "agent1", "key": "xxx", "name": "Agent 1", "enabled": true}]
    LOCAL_API_KEYS_JSON: str = "[]"

    # MCP Endpoints (Based on z.ai documentation)
    SEARCH_MCP_URL: str = "https://api.z.ai/api/mcp/web_search_prime/sse"
    READER_MCP_URL: str = "https://api.z.ai/api/mcp/web_reader/sse"
    ZREAD_MCP_URL: str = "https://api.z.ai/api/mcp/zread/sse"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def local_api_keys(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.LOCAL_API_KEYS_JSON)
        except Exception:
            return []

settings = Settings()
