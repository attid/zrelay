import pytest
import pytest_asyncio
from src.infrastructure.repositories.sqlite_repository import SQLiteRepository
from src.domain.entities.api_key import ApiKey
from src.domain.entities.usage_log import UsageLog
import uuid

@pytest_asyncio.fixture
async def repo():
    # Используем in-memory базу для тестов
    repository = SQLiteRepository("sqlite+aiosqlite:///:memory:")
    await repository.init_db()
    return repository

@pytest.mark.asyncio
async def test_add_and_get_api_key(repo):
    key_val = "test-key-" + str(uuid.uuid4())
    api_key = ApiKey(id="agent-1", key=key_val, name="Test Agent")
    
    await repo.add_api_keys([api_key])
    
    fetched = await repo.get_api_key(key_val)
    assert fetched is not None
    assert fetched.name == "Test Agent"
    assert fetched.id == "agent-1"

@pytest.mark.asyncio
async def test_get_non_existent_key(repo):
    fetched = await repo.get_api_key("missing")
    assert fetched is None

@pytest.mark.asyncio
async def test_save_usage_log(repo):
    log = UsageLog(
        client_key_id="agent-1",
        route="/api/v1/search",
        tool="search",
        operation="web_search",
        status_code=200,
        duration_ms=150,
        request_id="req-123",
        success=True
    )
    
    await repo.save_usage_log(log)
    # Если не упало — уже хорошо. Для полноценной проверки можно добавить метод get_logs в репозиторий.
