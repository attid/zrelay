import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.config import settings
from src.interface.admin.app import app as admin_app
from src.interface.api.auth import get_repository
from src.interface.api.middleware.error_handler import register_exception_handlers
from src.interface.api.routes import reader, search, vision, zread

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - initialize database
    logger.info("Starting zrelay...")
    repo = get_repository()
    await repo.init_db()

    yield
    # Shutdown
    logger.info("Shutting down zrelay...")


app = FastAPI(
    title="zrelay",
    description="REST/OpenAPI gateway for z.ai MCP tools",
    version="0.1.0",
    lifespan=lifespan,
)

# Exception handlers for unified error format
register_exception_handlers(app)

# Роуты инструментов
app.include_router(search.router, prefix="/api")
app.include_router(reader.router, prefix="/api")
app.include_router(zread.router, prefix="/api")
app.include_router(vision.router, prefix="/api")

# Admin Dashboard (FastHTML)
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
