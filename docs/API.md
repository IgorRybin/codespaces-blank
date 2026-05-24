# API-документация Kanban Board

Проект использует FastAPI, поэтому OpenAPI спецификация доступна автоматически.

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Основные маршруты

### Авторизация

- `GET /auth/login` — страница входа.
- `POST /auth/login` — логин пользователя.
  - form fields: `username`, `password`, `next`
- `GET /auth/logout` — выход из системы.

### Канбан-доска

- `GET /` — основной интерфейс доски.
  - query params: `q`, `assignee_id`, `priority`, `sort_by`

### Задачи

- `POST /tasks/create` — создать задачу.
  - form fields: `title`, `description`, `priority`, `due_date`, `assignee_id`, `sub_stage_id`, `status`
- `GET /tasks/{id}` — получить детали задачи.
- `POST /tasks/{id}/edit` — изменить задачу.
  - form fields: `title`, `description`, `priority`, `due_date`, `assignee_id`, `status`, `sub_stage_id`
- `POST /tasks/{id}/move` — переместить задачу через drag-and-drop.
  - JSON body: `status`, `sub_stage_id`
- `POST /tasks/{id}/comments` — добавить комментарий к задаче.
  - form fields: `text`
- `POST /tasks/{id}/delete` — удалить задачу.
- `GET /tasks/action/export-excel` — экспорт задач в Excel.

### Админ-панель

- `GET /admin` — админская панель.
- `POST /admin/users/create` — создать пользователя.
  - form fields: `username`, `password`, `full_name`, `color`
- `POST /admin/users/{id}/password` — сменить пароль пользователя.
  - form fields: `password`
- `POST /admin/users/{id}/delete` — удалить пользователя.
- `POST /admin/sub-stages/create` — создать подэтап.
  - form fields: `name`, `display_order`, `default_assignee_id`
- `POST /admin/sub-stages/{id}/edit` — обновить подэтап.
  - form fields: `name`, `display_order`, `default_assignee_id`
- `POST /admin/sub-stages/{id}/delete` — удалить подэтап.
- `POST /admin/backup/create` — создать бэкап базы.
- `GET /admin/backup/download/{filename}` — скачать бэкап.

## Ответы и поведение

- При отсутствии авторизации большинство защищенных маршрутов возвращают `401` или перенаправляют на `/auth/login`.
- Роуты, работающие с формами, обычно возвращают редирект на `/` или `/admin`.
- `POST /tasks/{id}/move` возвращает JSON с результатом перемещения.

## Поддержка OpenAPI

FastAPI автоматически генерирует спецификацию OpenAPI. Для расширения API достаточно добавить новый маршрут в `routers/` и описать параметры в аннотациях.

Для поддержки фронтенда по API можно использовать:

- `GET /openapi.json` — базовый JSON-спецификацию.
- `GET /docs` — Swagger UI.
- `GET /redoc` — ReDoc.
