set shell := ["bash", "-c"]

# Полная проверка проекта
check: fmt lint test

# Форматирование кода
fmt:
	uv run ruff format .
	uv run ruff check --fix .

# Линтинг и проверка типов
lint:
	uv run ruff check .
	uv run pyright src

# Запуск тестов
test:
	uv run pytest tests

# Запуск приложения локально
run:
	uv run uvicorn src.interface.api.main:app --host 0.0.0.0 --port 8000 --reload
