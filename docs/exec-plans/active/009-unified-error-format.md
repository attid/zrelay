# 009: Unified Error Format

## Контекст
В `docs/golden-principles.md` заявлен строгий формат ошибок `{"error": {"code": "...", "message": "..."}}`, но фактический API возвращает `ToolResult` с полями `ok`, `error`, `data` на верхнем уровне.

## План изменений
1. [x] Создать `src/domain/entities/api_error.py`:
   - [x] Модель `ApiError` с полями code, message, details
   - [x] `ErrorCode` - предопределённые коды ошибок
2. [x] Обновить `ToolResult`:
   - [x] Добавить поле `error_detail` для unified формата
3. [x] Создать `src/interface/api/middleware/error_handler.py`:
   - [x] Exception handlers для HTTPException, RequestValidationError, общих Exception
   - [x] Преобразование в `ApiError` формат
4. [x] Обновить `auth.py`:
   - [x] Использовать `APIKeyHeader` с `auto_error=False`
   - [x] Возвращать ошибки в unified формате

## Верификация
- ✅ Все ошибки возвращают `{"error": {"code": "...", "message": "..."}}`
- ✅ 401 (auth), 404 (not found), 422 (validation) - все в едином формате
- ✅ Все тесты проходят
