# 008: Linters and Guardrails Setup

## Контекст
В `AI_FIRST.md` обещаны высокие guardrails и линтеры, но папка `.linters/` пустая. Нужно настроить автоматические проверки качества кода.

## План изменений
1. [x] Создать `.linters/ruff.toml`
2. [x] Создать `.linters/mypy.ini` (базовая конфигурация)
3. [x] Добавить `lint` и `fmt` в Justfile
4. [x] Исправить ошибки линтера:
   - [x] Trailing whitespace в mcp_port.py
   - [x] Сравнения с True вместо truth checks
   - [x] Multi-statement на одной строке
5. [x] Настроить генерацию пароля админки (random если не задан)

## Верификация
- ✅ Ruff check проходит без ошибок
- ✅ Ruff format исправил 18 файлов
- ✅ Все тесты проходят
