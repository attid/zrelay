from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.interface.api.auth import get_repository
from src.interface.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_auth_missing_key(client):
    # Попытка вызова без ключа
    response = client.post("/api/v1/search/web-search", json={"query": "test"})
    assert response.status_code == 422  # FastAPI validation error for missing Header


def test_api_auth_invalid_key(client):
    # Переопределяем репозиторий для возврата None (невалидный ключ)
    mock_repo = MagicMock()
    mock_repo.get_api_key = AsyncMock(return_value=None)

    app.dependency_overrides[get_repository] = lambda: mock_repo

    response = client.post(
        "/api/v1/search/web-search",
        json={"query": "test"},
        headers={"X-API-Key": "invalid"},
    )
    assert response.status_code == 401

    app.dependency_overrides.clear()
