# 009: Unified Error Format

## Контекст
В `docs/golden-principles.md` заявлен строгий формат ошибок `{"error": {"code": "...", "message": "..."}}`, но фактический API возвращает `ToolResult` с полями `ok`, `error`, `data` на верхнем уровне.

## План изменений
1. [ ] Определить стандартный формат ошибок:
   - [ ] Создать `src/domain/entities/api_error.py` с моделями:
     - `ApiError(code: str, message: str, details: Optional[dict])`
     - HTTP статус-коды для каждого типа ошибки
2. [ ] Обновить `ToolResult`:
   - [ ] Добавить поле `error_detail: Optional[ApiError]`
   - [ ] Убрать или депрекировать `ok`, `error` поля (или оставить для backward compatibility)
3. [ ] Создать middleware для统一ного форматирования:
   - [ ] `src/interface/api/middleware/error_handler.py`
   - [ ] Перехват всех Exception и преобразование в `ApiError`
4. [ ] Обновить роуты:
   - [ ] Использовать `raise HTTPException` или кастомный `ApiException`
   - [ ] Проверить все endpoints

## Риски и открытые вопросы
- Breaking changes для существующих клиентов. Документировать в CHANGELOG.

## Верификация
- Все ошибки возвращают `{"error": {"code": "...", "message": "..."}}`
- Проверить через `curl` на разных эндпоинтах
