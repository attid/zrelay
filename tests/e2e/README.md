# E2E Tests — zrelay

Запускаются против живого Docker-контейнера. Реальные MCP-вызовы к z.ai upstream.

## Запуск

```bash
# Обязательно: URL и пароль админки
ZRELAY_URL=http://localhost:8000 \
ZRELAY_ADMIN_PASSWORD=your-admin-password \
uv run pytest tests/e2e/ -v

# Только конкретный тест
ZRELAY_URL=http://localhost:8000 \
ZRELAY_ADMIN_PASSWORD=your-admin-password \
uv run pytest tests/e2e/test_e2e.py::TestSearch::test_search_web -v
```

## Как это работает

1. Логинится в админку
2. Создаёт временный API ключ
3. Прогоняет все тесты с этим ключом
4. Удаляет ключ после завершения

## Переменные окружения

| Переменная | Обязательно | Описание |
|-----------|------------|----------|
| `ZRELAY_URL` | да | URL сервера (Docker container) |
| `ZRELAY_ADMIN_PASSWORD` | да | Пароль админки для создания ключа |
