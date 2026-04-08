# Architecture: zrelay

## Слои и Направление зависимостей

В проекте используется Чистая Архитектура. Зависимости направлены только внутрь:
`domain ← application ← infrastructure / interface`

### 1. Domain (Ядро)
- Расположение: `src/domain/`
- Описание: Сущности (`ApiKey`, `UsageLog`), бизнес-правила, исключения.
- Ограничения: Не имеет внешних зависимостей.

### 2. Application (Сценарии использования)
- Расположение: `src/application/`
- Описание: Сценарии вызова инструментов (`ZRelayService`), оркестрация.
- Порты (Интерфейсы): `ports/mcp_port.py`, `ports/repository.py`.

### 3. Infrastructure (Адаптеры)
- Расположение: `src/infrastructure/`
- Описание: Реализация портов.
    - `adapters/mcp_local.py` (Vision через stdio).
    - `adapters/mcp_remote.py` (Search/Reader/Zread через SSE).
    - `repositories/sqlite_repository.py` (SQLite + SQLModel).

### 4. Interface (Порты ввода)
- Расположение: `src/interface/`
- Описание: Эндпоинты FastAPI, валидация Pydantic, Swagger.

## Правила границ (Guardrails)
1. Код из `domain` никогда не импортирует из `application`, `infrastructure` или `interface`.
2. Код из `application` импортирует только из `domain`.
3. Код из `interface` и `infrastructure` импортирует из `application` и `domain`.
4. Для взаимодействия `application` с `infrastructure` используются абстрактные интерфейсы (Ports).
