# 005: Testing and Coverage

## Контекст
Реализация набора тестов для обеспечения качества и соблюдения DoD (Definition of Done) согласно `AI_FIRST.md`.

## План изменений
1. [x] Настроить конфигурацию pytest (`pyproject.toml` или `pytest.ini`).
2. [x] Реализовать Unit-тесты для Domain/Application:
    - [x] `tests/application/test_zrelay_service.py`: Пройдено.
3. [x] Реализовать Integration-тесты для Infrastructure:
    - [x] `tests/infrastructure/test_sqlite_repository.py`: Пройдено.
4. [x] Реализовать API-тесты для Interface:
    - [x] `tests/interface/test_api_auth.py`: Пройдено.
5. [x] Запустить тесты и сформировать отчет о покрытии. (Достигнуто **81%** общего покрытия).

## Риски и открытые вопросы
- Проблемы с закрытием event loop в aiosqlite (решается настройкой scope в pytest-asyncio, для MVP не критично, тесты зеленые).

## Верификация
- `just test` показывает покрытие **81%** для основного кода.
