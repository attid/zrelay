from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from src.interface.api.routes import search, reader, zread, vision
from src.interface.admin.app import app as admin_app
from src.interface.api.auth import get_repository
from src.infrastructure.config import settings
from src.domain.entities.api_key import ApiKey
import logging

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting zrelay...")
    repo = get_repository()
    await repo.init_db()
    
    # Загрузка ключей из конфига
    local_keys = []
    for k in settings.local_api_keys:
        local_keys.append(ApiKey(
            id=k.get("id"),
            key=k.get("key"),
            name=k.get("name", "Unknown"),
            enabled=k.get("enabled", True)
        ))
    if local_keys:
        await repo.add_api_keys(local_keys)
        logger.info(f"Loaded {len(local_keys)} local API keys from settings.")
        
    yield
    # Shutdown
    logger.info("Shutting down zrelay...")

app = FastAPI(
    title="zrelay",
    description="REST/OpenAPI gateway for z.ai MCP tools",
    version="0.1.0",
    lifespan=lifespan
)

# Роуты инструментов
app.include_router(search.router, prefix="/api")
app.include_router(reader.router, prefix="/api")
app.include_router(zread.router, prefix="/api")
app.include_router(vision.router, prefix="/api")

# Admin Dashboard (FastHTML)
from src.interface.admin.app import app as admin_app
from starlette.middleware.sessions import SessionMiddleware

# Добавляем атрибуты FastHTML
app.canonical = True

# Session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.ADMIN_PASSWORD)

# Добавляем роуты админки в начало
app.router.routes[:0] = admin_app.routes

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    # Можно добавить проверку доступности БД
    return {"status": "ready"}
