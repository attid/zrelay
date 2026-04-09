import logging
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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
    ADMIN_PASSWORD: str = ""  # Generate random if not set

    # MCP Endpoints
    SEARCH_MCP_URL: str = "https://api.z.ai/api/mcp/web_search_prime/sse"
    READER_MCP_URL: str = "https://api.z.ai/api/mcp/web_reader/sse"
    ZREAD_MCP_URL: str = "https://api.z.ai/api/mcp/zread/sse"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **data):
        super().__init__(**data)
        # Generate random password if not set
        if not self.ADMIN_PASSWORD:
            self.ADMIN_PASSWORD = secrets.token_urlsafe(16)
            logger.warning("Generated random admin password: %s", self.ADMIN_PASSWORD)


settings = Settings()
