Да. Ниже черновик ТЗ в нормальном рабочем виде, с упором на **MCP → REST/OpenAPI gateway** для z.ai DevPack.

# ТЗ: REST/OpenAPI-шлюз для z.ai MCP tools

## 1. Назначение

Разработать сервис, который запускается в Docker и предоставляет единый **REST API** с **OpenAPI/Swagger** для вызова инструментов z.ai DevPack, при этом внутри сам работает как прокси/адаптер к MCP-инструментам.

Сервис нужен для использования z.ai tool’ов в агенте **без прямой работы с MCP-клиентом**.

## 2. Цель

На выходе должен быть сервис, который:

* поднимается одной Docker-командой;
* публикует OpenAPI-схему;
* принимает обычные HTTP-запросы;
* внутри вызывает соответствующий MCP tool;
* умеет хранить upstream API key в переменных окружения;
* при необходимости выдаёт **собственные локальные API keys** для клиентов;
* ведёт минимальную статистику использования.

## 3. Инструменты первой версии

В первой версии поддерживаются 4 логических источника:

* `vision`
* `search`
* `reader`
* `zread`

Каждый источник должен быть виден как отдельная группа REST-методов.

## 4. Основной сценарий использования

Клиентский агент работает только по HTTP:

1. отправляет запрос в локальный REST-шлюз;
2. шлюз валидирует локальный API key;
3. шлюз определяет нужный tool/provider;
4. шлюз вызывает соответствующий MCP-инструмент;
5. шлюз возвращает клиенту нормализованный JSON-ответ.

## 5. Область работ

### Входит в MVP

* HTTP API
* OpenAPI 3.1
* Swagger UI / docs endpoint
* вызов MCP tools из REST
* конфигурация через `.env`
* Docker и Docker Compose
* локальная API-key авторизация
* базовая статистика
* логирование
* healthcheck

### Не входит в MVP

* UI-панель администратора
* биллинг
* OAuth/SSO
* сложные роли и ACL
* распределённый rate limit
* очереди задач
* webhooks
* многонодовый кластер

## 6. Архитектурная модель

Сервис состоит из следующих модулей:

### 6.1 API Layer

Принимает REST-запросы, валидирует входные данные, отдаёт OpenAPI.

### 6.2 Auth Layer

Проверяет локальный API key клиента.

### 6.3 Tool Router

Определяет, какой MCP backend нужно вызвать: `vision`, `search`, `reader`, `zread`.

### 6.4 MCP Adapter Layer

Единый внутренний интерфейс для разных типов MCP backend:

* remote MCP
* local MCP process
* future custom adapters

### 6.5 Usage/Stats Layer

Пишет:

* время запроса
* tool
* метод
* статус
* длительность
* размер ответа
* client key id

### 6.6 Config Layer

Все секреты и настройки берутся из env или конфиг-файла.

## 7. Функциональные требования

## 7.1 REST API

Сервис должен предоставлять:

* `GET /health`
* `GET /ready`
* `GET /openapi.json`
* `GET /docs`

И прикладные маршруты, например:

* `POST /api/v1/search/web-search`
* `POST /api/v1/reader/read-web`
* `POST /api/v1/zread/search-doc`
* `POST /api/v1/zread/read-file`
* `POST /api/v1/zread/repo-structure`
* `POST /api/v1/vision/image-analysis`
* `POST /api/v1/vision/video-analysis`
* `POST /api/v1/vision/ui-diff-check`

Маршруты могут быть уточнены при реализации, но логика должна быть стабильной: **1 HTTP endpoint = 1 tool operation**.

## 7.2 OpenAPI

Сервис должен автоматически публиковать:

* перечень всех методов;
* схемы request/response;
* описания параметров;
* коды ошибок;
* примеры запросов.

## 7.3 Авторизация

Сервис должен поддерживать два уровня ключей:

### Upstream key

Ключ для доступа к z.ai хранится только на сервере:

* через env;
* не передаётся клиентом в каждом запросе;
* не светится в ответах и логах.

### Local client keys

Ключи, которыми пользуются внутренние клиенты/агенты:

* задаются через конфиг;
* каждый ключ имеет `id`, `name`, `enabled`;
* можно отключать без смены upstream key.

## 7.4 Статистика

Минимум должно сохраняться:

* timestamp
* client_key_id
* route
* tool
* upstream target
* success/error
* http status
* duration_ms
* request_id

Дополнительно желательно:

* input size
* output size
* error_type
* upstream status

## 7.5 Конфигурация

Сервис должен запускаться без ручного редактирования кода.

Настройки через env:

* `PORT`
* `LOG_LEVEL`
* `MASTER_API_KEY` или список client keys
* `ZAI_API_KEY`
* `REQUEST_TIMEOUT_SEC`
* `ENABLE_SWAGGER=true|false`
* `ENABLE_USAGE_STATS=true|false`
* `DATABASE_URL` или `STATS_DB_PATH`
* `ALLOW_ANON=false`

## 8. Нефункциональные требования

### 8.1 Docker-first

Сервис должен штатно работать в Docker.

### 8.2 Stateless core

Основная логика сервиса stateless; состояние только в config и stats storage.

### 8.3 Безопасность

* upstream API key не возвращается наружу;
* секреты не пишутся в logs;
* ошибки не должны раскрывать внутренние токены;
* по умолчанию анонимный доступ отключён.

### 8.4 Надёжность

* таймаут на upstream вызовы;
* корректная обработка недоступности MCP backend;
* стандартизированные ответы об ошибках;
* health/readiness endpoints.

### 8.5 Расширяемость

Новый tool/provider должен добавляться как новый адаптер без переписывания всей системы.

## 9. Хранилище статистики

Для MVP достаточно одного из вариантов:

### Вариант по умолчанию

SQLite

Требования:

* одна таблица usage_logs;
* одна таблица api_keys;
* простые индексы по timestamp, client_key_id, route.

Это даёт:

* простую переносимость;
* минимум инфраструктуры;
* возможность быстро смотреть usage.

## 10. Формат ошибок

Единый JSON-формат:

```json
{
  "error": {
    "code": "UPSTREAM_TIMEOUT",
    "message": "Upstream tool did not respond in time",
    "request_id": "req_123",
    "details": null
  }
}
```

Поддержать как минимум коды:

* `UNAUTHORIZED`
* `FORBIDDEN`
* `BAD_REQUEST`
* `VALIDATION_ERROR`
* `UPSTREAM_ERROR`
* `UPSTREAM_TIMEOUT`
* `TOOL_NOT_FOUND`
* `TOOL_UNAVAILABLE`
* `INTERNAL_ERROR`

## 11. Логирование

Логи в JSON.

Обязательные поля:

* timestamp
* level
* request_id
* route
* method
* client_key_id
* tool
* duration_ms
* status_code

Нельзя логировать:

* upstream API key
* bearer tokens целиком
* секреты из env
* полные чувствительные payload, если они содержат приватные данные

## 12. Предлагаемая структура API

## 12.1 Search

### `POST /api/v1/search/web-search`

Назначение: web search через backend search tool.

Пример тела запроса:

```json
{
  "query": "latest firebird 5 replication issues",
  "language": "ru",
  "max_results": 10
}
```

## 12.2 Reader

### `POST /api/v1/reader/read-web`

Назначение: прочитать и структурировать содержимое URL.

Пример:

```json
{
  "url": "https://example.com/article"
}
```

## 12.3 ZRead

### `POST /api/v1/zread/search-doc`

```json
{
  "query": "docker swarm healthcheck"
}
```

### `POST /api/v1/zread/read-file`

```json
{
  "path": "docs/setup.md"
}
```

### `POST /api/v1/zread/repo-structure`

```json
{
  "path": "/"
}
```

## 12.4 Vision

### `POST /api/v1/vision/image-analysis`

```json
{
  "image_url": "https://example.com/image.png",
  "prompt": "Опиши что на экране"
}
```

### `POST /api/v1/vision/ui-diff-check`

```json
{
  "before_image_url": "https://example.com/before.png",
  "after_image_url": "https://example.com/after.png",
  "prompt": "Найди визуальные различия"
}
```

## 13. Внутренний интерфейс адаптера

Нужен единый контракт:

```python
class ToolAdapter:
    async def invoke(self, operation: str, payload: dict, context: dict) -> dict:
        ...
```

Где:

* `operation` — конкретная операция tool’а;
* `payload` — входные аргументы;
* `context` — request_id, client_key_id, timeout и пр.

Это позволит подменять backend:

* remote MCP adapter
* local process adapter
* direct REST adapter в будущем

## 14. Нормализация ответов

Желательно единообразие.

Успешный ответ:

```json
{
  "ok": true,
  "tool": "search",
  "operation": "web-search",
  "request_id": "req_123",
  "data": {
    "...": "..."
  },
  "meta": {
    "duration_ms": 842
  }
}
```

## 15. Конфиг ключей

Для MVP допустим один из форматов:

### Через env

```env
LOCAL_API_KEYS_JSON=[{"id":"agent1","key":"xxx","name":"Main agent","enabled":true}]
```

или через файл:

```json
[
  {
    "id": "agent1",
    "name": "Main agent",
    "key": "xxx",
    "enabled": true
  }
]
```

## 16. Health endpoints

### `GET /health`

Возвращает, что процесс жив.

### `GET /ready`

Возвращает, что:

* конфиг загружен;
* key storage доступен;
* upstream adapters инициализированы.

## 17. Rate limiting

Для MVP — опционально, но желательно предусмотреть слой, который можно включить.

Минимум:

* per API key
* per minute
* configurable

## 18. Admin-функции MVP-light

Без UI, только внутренние endpoints, опционально под отдельным admin key:

* `GET /admin/stats/summary`
* `GET /admin/stats/by-key`
* `GET /admin/stats/by-route`
* `POST /admin/keys/reload`

Если это усложняет MVP, можно отложить на фазу 2.

## 19. Docker требования

Должны быть:

* `Dockerfile`
* `docker-compose.yml`
* `.env.example`

Контейнер должен:

* стартовать без интерактива;
* читать конфиг из env;
* писать логи в stdout;
* при необходимости хранить SQLite в volume.

## 20. Технологические ограничения

Предпочтительная реализация:

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLite + SQLAlchemy или SQLModel
* отдельный слой adapters/services/repositories

Это хорошо подходит под OpenAPI и Docker.

## 21. Критерии приёмки

Система считается принятой, если:

1. Поднимается в Docker.
2. Отдаёт `/docs` и `/openapi.json`.
3. Принимает локальный API key.
4. Не требует передавать upstream z.ai key в каждом запросе.
5. Умеет вызвать минимум по одной операции из `search`, `reader`, `zread`, `vision`.
6. Возвращает стандартизированный JSON.
7. Пишет usage-статистику.
8. Корректно обрабатывает таймауты и ошибки upstream.
9. Не светит секреты в логах и ответах.

## 22. Этапы реализации

### Этап 1

Каркас сервиса:

* FastAPI
* auth
* config
* docs
* health

### Этап 2

Интеграция adapters:

* search
* reader
* zread
* vision

### Этап 3

Usage stats:

* SQLite
* таблицы
* summary endpoints

### Этап 4

Полировка:

* ошибки
* логирование
* Docker
* примеры запросов
* README

## 23. Короткая формулировка результата

Нужен **самостоятельный Docker-сервис**, который превращает набор z.ai MCP tool’ов в **обычный REST/OpenAPI gateway** с локальной авторизацией, скрытым upstream key и минимальной статистикой использования.

## 24. Практическое решение по сути

Если брать за основу готовый мост, то ТЗ можно строить так:

* ядро: готовый MCP→OpenAPI bridge;
* обвязка: собственный auth/statistics layer;
* конфигурация: env + JSON;
* deployment: один контейнер, один volume под stats.

Это даёт самую короткую дорогу к рабочему результату.

