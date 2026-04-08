# zrelay 🚀

**zrelay** — это высокопроизводительный REST/OpenAPI шлюз для экосистемы инструментов [z.ai MCP](https://docs.z.ai/devpack/mcp/). Он объединяет локальные и удаленные MCP-инструменты в единый, защищенный HTTP API.

## ✨ Основные возможности

- **Единый API**: Доступ к `Vision`, `Search`, `Reader` и `Zread` через стандартные REST-запросы.
- **Двухуровневая авторизация**: Скрывает ваш мастер-ключ `Z_AI_API_KEY`, предоставляя клиентам локальные ключи с возможностью управления доступом.
- **Поддержка MCP протокола**:
  - **Local**: Запуск `Vision` через `npx` (stdio транспорт).
  - **Remote**: Подключение к `Search`, `Reader` и `Zread` через SSE (Server-Sent Events).
- **Статистика и логирование**: Запись каждого вызова в SQLite (режим WAL) для анализа использования и производительности.
- **Clean Architecture**: Кодовая база разделена на четкие слои (Domain, Application, Infrastructure, Interface) для легкой поддержки и расширения.
- **Полная документация**: Автоматическая генерация Swagger UI и OpenAPI спецификации.

## 🛠 Технологический стек

- **Язык**: Python 3.11
- **Фреймворк**: FastAPI + Pydantic v2
- **MCP SDK**: `mcp-python-sdk` (Anthropic)
- **База данных**: SQLite + SQLModel (SQLAlchemy)
- **Среда выполнения**: Docker (Node.js 22 + Python 3.11)
- **Менеджер пакетов**: `uv`

## 🚀 Быстрый старт

### 1. Подготовка окружения
Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```
Отредактируйте `.env` и укажите ваш мастер-ключ:
```env
Z_AI_API_KEY=ваш_ключ_от_z_ai
```

### 2. Запуск через Docker Compose
```bash
docker compose up --build -d
```
Сервис будет доступен по адресу: `http://localhost:8000`

### 3. Проверка работоспособности
- **Интерактивная документация**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Healthcheck**: `curl http://localhost:8000/health`

## 🔑 Авторизация

Для выполнения запросов используйте заголовок `X-API-Key`. Локальные ключи настраиваются через переменную окружения `LOCAL_API_KEYS_JSON` в формате:
```json
[{"id": "agent-1", "key": "secret-key-123", "name": "Main Agent", "enabled": true}]
```

## 📖 Примеры запросов

### Поиск в Web (Search)
```bash
curl -X POST "http://localhost:8000/api/v1/search/web-search" \
     -H "X-API-Key: secret-key-123" \
     -H "Content-Type: application/json" \
     -d '{"query": "FastAPI best practices", "max_results": 5}'
```

### Анализ изображений (Vision)
```bash
curl -X POST "http://localhost:8000/api/v1/vision/image-analysis" \
     -H "X-API-Key: secret-key-123" \
     -H "Content-Type: application/json" \
     -d '{"path": "https://example.com/screenshot.png", "prompt": "What is in this UI?"}'
```

## 🏗 Архитектура

Проект следует принципам **Clean Architecture**:

- `src/domain`: Сущности (ApiKey, UsageLog) и бизнес-логика.
- `src/application`: Сценарии использования (ZRelayService) и порты для инфраструктуры.
- `src/infrastructure`: Реализации адаптеров (MCP Local/Remote) и репозитория (SQLite).
- `src/interface`: FastAPI эндпоинты, валидация и Swagger.

## 🧪 Тестирование

Проект покрыт тестами на **>80%**. Для запуска используйте `Justfile`:

```bash
just test   # Запуск всех тестов с отчетом о покрытии
just check  # Полная проверка (fmt + lint + test)
```

## 📝 Лицензия

MIT
