# 📡 API документация — Kanban Board

Полная документация всех REST API endpoint-ов проекта Kanban Board.

---

## 📋 Содержание

- [Аутентификация (auth.py)](#аутентификация-authpy)
- [Доска (board.py)](#доска-boardpy)
- [Задачи (tasks.py)](#задачи-taskspy)
- [Админ-панель (admin.py)](#админ-панель-adminpy)

---

## Аутентификация (auth.py)

### POST /login

Вход пользователя в систему.

**Параметры (Form):**
```
username: str     # Логин пользователя
password: str     # Пароль
```

**Ответ (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "Иван Иванов",
    "is_active": true
  }
}
```

**Пример:**
```bash
curl -X POST http://localhost:8000/login \
  -d "username=admin&password=admin"
```

---

### POST /logout

Выход из системы.

**Ответ (200):**
```json
{
  "message": "Logout successful"
}
```

**Пример:**
```bash
curl -X POST http://localhost:8000/logout
```

---

### GET /me

Получить информацию о текущем пользователе.

**Ответ (200):**
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "Иван Иванов",
  "color": "#3498db",
  "is_active": true
}
```

**Ответ (401):**
```json
{
  "detail": "Not authenticated"
}
```

---

## Доска (board.py)

### GET /

Главная страница канбан-доски (HTML).

**Ответ (200):** HTML страница с интерфейсом доски

**Требует аутентификации:** Да

---

### GET /board

JSON данные для доски.

**Параметры (Query):**
- Нет

**Ответ (200):**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "Иван Иванов"
  },
  "sub_stages": [
    {
      "id": 1,
      "name": "Планирование",
      "display_order": 1,
      "tasks": [...]
    }
  ]
}
```

**Требует аутентификации:** Да

---

## Задачи (tasks.py)

### GET /api/tasks

Получить все задачи.

**Параметры (Query):**
- `status` (опционально): "todo", "in_progress", "done"
- `assignee_id` (опционально): ID исполнителя

**Ответ (200):**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Реализовать авторизацию",
      "description": "Добавить форму входа",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2026-05-25T10:30:00",
      "creator_id": 1,
      "assignee_id": 2,
      "due_date": "2026-05-30",
      "sub_stage_id": 1
    }
  ]
}
```

---

### POST /api/tasks

Создать новую задачу.

**Body (JSON):**
```json
{
  "title": "Новая задача",
  "description": "Описание",
  "priority": "medium",
  "due_date": "2026-06-01",
  "assignee_id": 2,
  "sub_stage_id": 1
}
```

**Ответ (201):**
```json
{
  "id": 10,
  "title": "Новая задача",
  "status": "todo",
  ...
}
```

**Требует аутентификации:** Да

---

### GET /api/tasks/{task_id}

Получить одну задачу по ID.

**Параметры (Path):**
- `task_id` (int): ID задачи

**Ответ (200):**
```json
{
  "id": 1,
  "title": "Реализовать авторизацию",
  "description": "Добавить форму входа",
  "status": "in_progress",
  "comments": [
    {
      "id": 1,
      "text": "В процессе",
      "author_id": 2,
      "created_at": "2026-05-25T11:00:00"
    }
  ],
  "history": [...]
}
```

---

### PUT /api/tasks/{task_id}

Обновить задачу.

**Параметры (Path):**
- `task_id` (int): ID задачи

**Body (JSON):**
```json
{
  "title": "Обновленное название",
  "status": "done",
  "assignee_id": 3,
  "priority": "low"
}
```

**Ответ (200):**
```json
{
  "id": 1,
  "title": "Обновленное название",
  "status": "done",
  ...
}
```

**Требует аутентификации:** Да

---

### DELETE /api/tasks/{task_id}

Удалить задачу.

**Параметры (Path):**
- `task_id` (int): ID задачи

**Ответ (200):**
```json
{
  "message": "Task deleted successfully"
}
```

**Требует аутентификации:** Да

---

### POST /api/tasks/{task_id}/comment

Добавить комментарий к задаче.

**Параметры (Path):**
- `task_id` (int): ID задачи

**Body (JSON):**
```json
{
  "text": "Отличная работа!"
}
```

**Ответ (201):**
```json
{
  "id": 5,
  "text": "Отличная работа!",
  "author_id": 1,
  "task_id": 1,
  "created_at": "2026-05-25T12:00:00"
}
```

**Требует аутентификации:** Да

---

### POST /api/tasks/{task_id}/move

Переместить задачу в другой подэтап.

**Параметры (Path):**
- `task_id` (int): ID задачи

**Body (JSON):**
```json
{
  "sub_stage_id": 2
}
```

**Ответ (200):**
```json
{
  "id": 1,
  "sub_stage_id": 2,
  "status": "in_progress"
}
```

**Требует аутентификации:** Да

---

## Админ-панель (admin.py)

### GET /admin

Страница админ-панели (HTML).

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### GET /api/admin/users

Получить всех пользователей.

**Ответ (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "full_name": "Иван Иванов",
      "is_active": true,
      "color": "#3498db"
    }
  ]
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### POST /api/admin/users

Создать нового пользователя.

**Body (JSON):**
```json
{
  "username": "newuser",
  "password": "password123",
  "full_name": "Новый пользователь",
  "color": "#e74c3c"
}
```

**Ответ (201):**
```json
{
  "id": 6,
  "username": "newuser",
  "full_name": "Новый пользователь",
  "is_active": true
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### PUT /api/admin/users/{user_id}

Обновить пользователя.

**Параметры (Path):**
- `user_id` (int): ID пользователя

**Body (JSON):**
```json
{
  "full_name": "Новое имя",
  "is_active": false,
  "color": "#2ecc71"
}
```

**Ответ (200):**
```json
{
  "id": 2,
  "username": "pavel",
  "full_name": "Новое имя",
  "is_active": false
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### DELETE /api/admin/users/{user_id}

Удалить пользователя.

**Параметры (Path):**
- `user_id` (int): ID пользователя

**Ответ (200):**
```json
{
  "message": "User deleted successfully"
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin  
**Ограничение:** Нельзя удалить пользователя "admin"

---

### POST /api/admin/password

Изменить пароль пользователя.

**Body (JSON):**
```json
{
  "user_id": 2,
  "new_password": "newpassword123"
}
```

**Ответ (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### GET /api/admin/sub-stages

Получить все подэтапы.

**Ответ (200):**
```json
{
  "sub_stages": [
    {
      "id": 1,
      "name": "Планирование",
      "display_order": 1,
      "default_assignee_id": null
    }
  ]
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### POST /api/admin/sub-stages

Создать новый подэтап.

**Body (JSON):**
```json
{
  "name": "Тестирование",
  "display_order": 4,
  "default_assignee_id": 3
}
```

**Ответ (201):**
```json
{
  "id": 5,
  "name": "Тестирование",
  "display_order": 4,
  "default_assignee_id": 3
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

### PUT /api/admin/sub-stages/{sub_stage_id}

Обновить подэтап.

**Параметры (Path):**
- `sub_stage_id` (int): ID подэтапа

**Body (JSON):**
```json
{
  "name": "Переработка",
  "display_order": 2
}
```

**Ответ (200):**
```json
{
  "id": 1,
  "name": "Переработка",
  "display_order": 2
}
```

---

### DELETE /api/admin/sub-stages/{sub_stage_id}

Удалить подэтап.

**Параметры (Path):**
- `sub_stage_id` (int): ID подэтапа

**Ответ (200):**
```json
{
  "message": "Sub-stage deleted successfully"
}
```

---

### POST /api/admin/backup

Создать резервную копию БД.

**Ответ (200):**
```json
{
  "message": "Backup created successfully",
  "filename": "backup_2026-05-25_12-30-45.zip"
}
```

**Требует аутентификации:** Да  
**Требует роли:** Admin

---

## 🔑 Коды ответов

| Код | Описание |
| --- | --- |
| 200 | OK — успешный запрос |
| 201 | Created — ресурс создан |
| 400 | Bad Request — неверные параметры |
| 401 | Unauthorized — не аутентифицирован |
| 403 | Forbidden — нет прав доступа |
| 404 | Not Found — ресурс не найден |
| 500 | Internal Server Error — ошибка сервера |

---

## 🧪 Тестирование API

### Использование curl

```bash
# Вход
curl -X POST http://localhost:8000/login \
  -d "username=admin&password=admin"

# Получить текущего пользователя
curl -X GET http://localhost:8000/me \
  --cookie "kanban_session=your_session_id"

# Получить все задачи
curl -X GET http://localhost:8000/api/tasks \
  --cookie "kanban_session=your_session_id"

# Создать задачу
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","status":"todo"}' \
  --cookie "kanban_session=your_session_id"
```

### Использование Swagger UI

Откройте в браузере: **http://localhost:8000/docs**

Здесь можно:
- Просмотреть все endpoint-ы
- Прочитать описание параметров
- Протестировать endpoint-ы онлайн

### Использование ReDoc

Откройте в браузере: **http://localhost:8000/redoc**

Альтернативная документация для API.

---

## 📝 Форматы данных

### User объект

```json
{
  "id": 1,
  "username": "admin",
  "full_name": "Иван Иванов",
  "color": "#3498db",
  "is_active": true
}
```

### Task объект

```json
{
  "id": 1,
  "title": "Название задачи",
  "description": "Описание",
  "status": "in_progress",
  "priority": "high",
  "created_at": "2026-05-25T10:30:00",
  "completed_at": null,
  "creator_id": 1,
  "assignee_id": 2,
  "due_date": "2026-06-01",
  "sub_stage_id": 1
}
```

### Comment объект

```json
{
  "id": 1,
  "task_id": 1,
  "author_id": 2,
  "text": "Комментарий",
  "created_at": "2026-05-25T11:00:00"
}
```

### SubStage объект

```json
{
  "id": 1,
  "name": "Планирование",
  "display_order": 1,
  "default_assignee_id": null
}
```

---

## ⚡ Быстрые примеры

### Workflow: Создание и завершение задачи

```bash
# 1. Вход
curl -X POST http://localhost:8000/login -d "username=admin&password=admin"

# 2. Создать задачу
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новая задача",
    "status": "todo",
    "priority": "high"
  }'

# 3. Получить ID задачи из ответа
TASK_ID=10

# 4. Переместить в "В работе"
curl -X POST http://localhost:8000/api/tasks/$TASK_ID/move \
  -H "Content-Type: application/json" \
  -d '{"sub_stage_id": 2}'

# 5. Добавить комментарий
curl -X POST http://localhost:8000/api/tasks/$TASK_ID/comment \
  -H "Content-Type: application/json" \
  -d '{"text": "Начал работу"}'

# 6. Завершить задачу
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

---

Последний обновлен: **2026-05-25**
