import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse

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


@app.get("/")
async def root():
    return RedirectResponse(url="/llms.txt", status_code=307)


@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    llms_path = Path(__file__).resolve().parents[3] / "llms.txt"
    if not llms_path.exists():
        return PlainTextResponse("llms.txt not found", status_code=404)
    return PlainTextResponse(llms_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    # Можно добавить проверку доступности БД
    return {"status": "ready"}


# Добавляем роуты админки в конец, чтобы они не перехватывали /llms.txt и системные endpoints
app.router.routes.extend(admin_app.routes)
