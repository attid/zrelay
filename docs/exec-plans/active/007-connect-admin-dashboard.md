# 007: Connect Admin Dashboard to FastAPI

## Контекст
Админка реализована в `src/interface/admin/app.py`, но не подключена к основному FastAPI приложению. В продакшене админка недоступна.

## План изменений
1. [x] Подключить `admin_app` в `src/interface/api/main.py`:
   - [x] Добавить SessionMiddleware для сессий
   - [x] Добавить `app.canonical = True` для FastHTML
   - [x] Добавить роуты в начало списка
2. [x] Исправить Layout в admin/app.py (Container -> Div)
3. [x] Проверить работу:
   - [x] `/health` возвращает 200
   - [x] `/admin/login` возвращает 200
   - [x] Login POST редиректит
   - [x] Dashboard доступен после авторизации
4. [x] Все тесты проходят

## Верификация
- ✅ API эндпоинты работают
- ✅ Админка доступна на /admin/
- ✅ Авторизация через сессии работает
