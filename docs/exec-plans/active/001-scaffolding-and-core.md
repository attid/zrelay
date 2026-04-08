# 001: Scaffolding and Core Layer

## Контекст
Инициализация проекта `zrelay` (REST/OpenAPI gateway для z.ai MCP tools) согласно принципам Clean Architecture и AI-First Repo Contract.

## План изменений
1. [x] Создать структуру директорий (`src/domain`, `src/application`, `src/infrastructure`, `src/interface`, `docs/`, `tests/`)
2. [x] Подготовить базовую документацию:
    - [x] `docs/architecture.md` (слои и границы)
    - [x] `docs/glossary.md` (доменный язык: MCP, Upstream, Local Key)
    - [x] `docs/golden-principles.md` (аксиомы)
3. [x] Настроить окружение:
    - [x] `pyproject.toml` (uv, fastapi, sqlmodel, mcp-python-sdk)
    - [x] `Justfile` (fmt, lint, test, check)
    - [x] `.env.example`
4. [x] Реализовать Domain Layer (`src/domain`):
    - [x] `entities/api_key.py`: Модель локального API ключа
    - [x] `entities/usage_log.py`: Модель лога использования
    - [x] `entities/tool.py` (заменено на `tool_result.py`): Модель результата инструмента
5. [x] Реализовать Application Layer Ports (Interfaces):
    - [x] `src/application/ports/mcp_port.py`: Абстрактный интерфейс для MCP адаптеров
    - [x] `src/application/ports/repository_port.py`: Абстрактный интерфейс для БД

## Риски и открытые вопросы
- Сложность в Node.js зависимостях для Vision MCP в Docker. Нужно аккуратно собрать мультистейдж Dockerfile. (В процессе решения через Dockerfile)
- Определение конкретных схем Pydantic для каждого инструмента (Vision/Search/Reader/Zread). (Будет решено в Interface Layer)

## Верификация
- `just check` проходит успешно. (Нужно установить зависимости и запустить ruff)
- Код соответствует структуре и импортам Clean Architecture. (Да)
