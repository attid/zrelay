# 002: Infrastructure and Application Implementation

## Контекст
Реализация конкретных адаптеров для работы с БД и MCP-серверами, а также сервиса-оркестратора.

## План изменений
1. [x] Реализовать `src/infrastructure/repositories/sqlite_repository.py`:
    - [x] Поддержка WAL.
    - [x] Инициализация таблиц через SQLModel.
    - [x] Методы `get_api_key`, `save_usage_log`.
2. [x] Реализовать MCP Адаптеры (`src/infrastructure/adapters/`):
    - [x] `mcp_remote.py`: Подключение к удаленным SSE серверам (Search, Reader, Zread).
    - [x] `mcp_local.py`: Подключение к локальному Vision MCP через stdio (`npx`).
3. [x] Реализовать Application Service (`src/application/services/zrelay_service.py`):
    - [x] Оркестрация вызовов.
    - [x] Логирование (UsageLog) через Repository.
    - [x] Обработка ошибок.
4. [x] Реализовать Configuration (`src/infrastructure/config.py`):
    - [x] Pydantic Settings для ENV.

## Риски и открытые вопросы
- Потокобезопасность при работе с несколькими MCP клиентами в асинхронном режиме. (Используются асинхронные контекстные менеджеры)
- Обработка жизненного цикла MCP клиентов (connect/disconnect). (Реализовано через context managers в адаптерах)

## Верификация
- Unit-тесты для репозитория. (Предстоит в рамках общей верификации)
- Unit-тесты для логики сервиса (с моками адаптеров). (Предстоит в рамках общей верификации)
