# Используем образ с Python 3.13 и Node.js 22
FROM nikolaik/python-nodejs:python3.13-nodejs22-slim

WORKDIR /app

# Базовые утилиты для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project

# Копируем исходный код
COPY src ./src
COPY docs ./docs
COPY llms.txt ./llms.txt

# Финальная синхронизация проекта
RUN uv sync --frozen --no-cache

# Создаем директорию для БД
RUN mkdir -p /app/data

# Настройка переменных окружения
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV DATABASE_URL="sqlite+aiosqlite:////app/data/stats.db"

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "src.interface.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
