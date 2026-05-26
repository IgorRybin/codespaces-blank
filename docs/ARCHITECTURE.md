# 🏗️ Архитектура проекта — Kanban Board

Подробное описание архитектуры, design patterns и техники, используемых в проекте.

---

## 📋 Содержание

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Стек технологий](#стек-технологий)
3. [Слои приложения](#слои-приложения)
4. [Диаграмма компонентов](#диаграмма-компонентов)
5. [Поток данных](#поток-данных)
6. [Database Design](#database-design)
7. [Security](#security)
8. [Performance](#performance)

---

## Обзор архитектуры

**Kanban Board** построен на классической трёхслойной архитектуре:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (HTML/Jinja2 Templates + API)        │
├─────────────────────────────────────────┤
│       Business Logic Layer              │
│    (FastAPI Routers + Services)         │
├─────────────────────────────────────────┤
│        Data Access Layer                │
│    (SQLAlchemy ORM + SQLite)            │
└─────────────────────────────────────────┘
```

---

## Стек технологий

| Компонент | Технология | Версия | Назначение |
| --- | --- | --- | --- |
| **Web Framework** | FastAPI | >=0.100.0 | REST API и server-side rendering |
| **ASGI Server** | Uvicorn | >=0.20.0 | HTTP сервер для FastAPI |
| **ORM** | SQLAlchemy | >=2.0.0 | Object-Relational Mapping |
| **Database** | SQLite | встроен | Хранилище данных |
| **Async DB Driver** | aiosqlite | >=0.22.1 | Асинхронный драйвер для SQLite |
| **Migrations** | Alembic | >=1.18.4 | Управление версионированием БД |
| **Templates** | Jinja2 | >=3.0.0 | Server-side HTML rendering |
| **Form Processing** | python-multipart | >=0.0.6 | Обработка HTML форм |
| **Excel Export** | openpyxl | >=3.1.0 | Экспорт в Excel |
| **HTTP Client** | httpx | >=0.27.0 | Для тестов и внутренних запросов |

---

## Слои приложения

### 1️⃣ Presentation Layer (Представление)

**Файлы:** `templates/`, `routers/`

**Задача:** Взаимодействие с пользователем

**Компоненты:**
- HTML шаблоны (Jinja2)
- HTTP endpoints (FastAPI routers)
- Error handling и ответы

**Примеры:**
```
GET  /              → board.html (канбан-доска)
GET  /admin         → admin.html (администратор)
GET  /login         → login.html (форма входа)
POST /login         → аутентификация
GET  /api/tasks     → JSON ответ со списком задач
```

### 2️⃣ Business Logic Layer (Бизнес-логика)

**Файлы:** `routers/`, `services/`

**Задача:** Обработка бизнес-правил

**Компоненты:**
- Валидация данных
- Проверка прав доступа
- Обработка задач (создание, обновление, удаление)
- Резервные копии и экспорт

**Примеры:**
```python
# routers/tasks.py
@app.post("/api/tasks")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Проверка: пользователь авторизован? Можно ли создать задачу?
    # Создать задачу в БД
    # Создать запись в TaskHistory
    # Вернуть результат
    pass

# services/backup_service.py
def create_backup():
    # Создать резервную копию БД
    # Сжать в zip архив
    # Сохранить в backups/
    pass
```

### 3️⃣ Data Access Layer (Доступ к данным)

**Файлы:** `database.py`, `models/models.py`

**Задача:** Работа с БД

**Компоненты:**
- SQLAlchemy engine (подключение к БД)
- SessionLocal (фабрика сессий)
- ORM модели
- Relationships между таблицами

**Примеры:**
```python
# database.py
engine = create_engine("sqlite:///./database.db")
SessionLocal = sessionmaker(bind=engine)

# models/models.py
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    assignee = relationship("User")  # Relationship
```

---

## Диаграмма компонентов

```
┌──────────────────────────────────────────────────────────────┐
│                          User Browser                        │
└──────────────────────────────────────────────────────────────┘
                              ↓ HTTP
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Routers (HTTP Endpoints)                   │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │ routers/auth.py    → /login, /logout, /me        │   │ │
│  │  ├──────────────────────────────────────────────────┤   │ │
│  │  │ routers/board.py   → /, /board                   │   │ │
│  │  ├──────────────────────────────────────────────────┤   │ │
│  │  │ routers/tasks.py   → /api/tasks, /api/tasks/{id} │   │ │
│  │  ├──────────────────────────────────────────────────┤   │ │
│  │  │ routers/admin.py   → /admin, /api/admin/*        │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Services (Business Logic)                     │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │ services/backup_service.py   → Создание копий   │   │ │
│  │  ├──────────────────────────────────────────────────┤   │ │
│  │  │ services/excel_service.py    → Экспорт данных    │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         SQLAlchemy ORM (Data Access)                    │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │ models/models.py                                │   │ │
│  │  │ • User          • Comment                        │   │ │
│  │  │ • Task          • TaskHistory                    │   │ │
│  │  │ • SubStage                                      │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │                      SessionLocal                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    SQLite Database                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ users  │ tasks  │ sub_stages  │ comments  │ histories   │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Поток данных

### Пример 1: Создание задачи

```
1. User заполняет форму в браузере
                    ↓
2. POST /api/tasks отправляется на сервер
                    ↓
3. FastAPI получает request в routers/tasks.py
   - Проверяет аутентификацию (JWT/Session)
   - Валидирует данные TaskCreate
                    ↓
4. Business Logic слой обрабатывает
   - Создаёт объект Task
   - Создаёт запись TaskHistory (кто, когда, что сделал)
   - Выполняет дополнительные бизнес-правила
                    ↓
5. SQLAlchemy ORM выполняет
   - db.add(task)  → добавить в сессию
   - db.commit()   → сохранить в БД
                    ↓
6. SQLite БД сохраняет данные в файл database.db
                    ↓
7. FastAPI возвращает JSON response
   {
     "id": 10,
     "title": "...",
     ...
   }
                    ↓
8. Browser получает response и обновляет UI
```

### Пример 2: Получение доски

```
1. User открывает http://localhost:8000
                    ↓
2. GET / запрос на сервер
                    ↓
3. FastAPI маршрут в routers/board.py
   - Проверяет аутентификацию
   - Получает данные из БД
   - Рендерит HTML с Jinja2
                    ↓
4. SQLAlchemy запросы к БД
   - SELECT * FROM sub_stages
   - SELECT * FROM tasks WHERE sub_stage_id = X
                    ↓
5. SQLite возвращает данные
                    ↓
6. Jinja2 шаблон (templates/board.html) рендерится с данными
                    ↓
7. HTML отправляется в браузер
                    ↓
8. Browser отображает канбан-доску
```

---

## Database Design

### Entity-Relationship Diagram (ERD)

```
┌─────────────────────────────┐
│          User               │
├─────────────────────────────┤
│ id (PK)                     │
│ username (UNIQUE)           │
│ password_hash               │
│ full_name                   │
│ color                       │
│ is_active                   │
└─────────────────────────────┘
         ↑ (1)       ↑
         │           │
         │ (N)       │ (N)
         │           │
         │           └─────────────────────┐
         │                                 │
┌─────────────────────────────┐  ┌─────────────────────────────┐
│      SubStage               │  │      Task                   │
├─────────────────────────────┤  ├─────────────────────────────┤
│ id (PK)                     │  │ id (PK)                     │
│ name                        │  │ title                       │
│ display_order               │  │ description                 │
│ default_assignee_id (FK)    │──→ creator_id (FK) → User     │
└─────────────────────────────┘  │ assignee_id (FK) → User     │
         ↑ (1)                   │ sub_stage_id (FK) → SubStage│
         │                       │ status                      │
         │ (N)                   │ priority                    │
         │                       │ created_at                  │
         │                       │ due_date                    │
         │                       │ completed_at                │
         └───────────────────────┴─────────────────────────────┘
                                  ↑ (1)      ↑ (1)
                                  │          │
                                  │ (N)      │ (N)
                                  │          │
                       ┌──────────┴──┐  ┌────┴────────────────┐
                       │             │  │                     │
            ┌──────────────────────┐ │  │  ┌──────────────────────────┐
            │    Comment           │ │  │  │    TaskHistory           │
            ├──────────────────────┤ │  │  ├──────────────────────────┤
            │ id (PK)              │ │  │  │ id (PK)                  │
            │ task_id (FK)─────────┼─┘  │  │ task_id (FK)─────────────┼─┐
            │ author_id (FK) → User    │  │ user_id (FK) → User      │ │
            │ text                 │    │  │ action (created/updated) │ │
            │ created_at           │    │  │ details                  │ │
            └──────────────────────┘    │  │ created_at               │ │
                                        │  └──────────────────────────┘ │
                                        │                              │
                                        └──────────────────────────────┘
```

### Таблицы и их структура

#### users
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  color VARCHAR(7),
  is_active BOOLEAN DEFAULT TRUE
);
```

#### tasks
```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50),
  priority VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  creator_id INTEGER NOT NULL FOREIGN KEY REFERENCES users(id),
  assignee_id INTEGER FOREIGN KEY REFERENCES users(id),
  due_date DATE,
  sub_stage_id INTEGER FOREIGN KEY REFERENCES sub_stages(id)
);
```

#### sub_stages
```sql
CREATE TABLE sub_stages (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  display_order INTEGER,
  default_assignee_id INTEGER FOREIGN KEY REFERENCES users(id)
);
```

#### comments
```sql
CREATE TABLE comments (
  id INTEGER PRIMARY KEY,
  task_id INTEGER NOT NULL FOREIGN KEY REFERENCES tasks(id),
  author_id INTEGER NOT NULL FOREIGN KEY REFERENCES users(id),
  text TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### task_histories
```sql
CREATE TABLE task_histories (
  id INTEGER PRIMARY KEY,
  task_id INTEGER NOT NULL FOREIGN KEY REFERENCES tasks(id),
  user_id INTEGER NOT NULL FOREIGN KEY REFERENCES users(id),
  action VARCHAR(50),
  details TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security

### Аутентификация

**Метод:** Session-based authentication с cookies

```python
# routers/auth.py
@app.post("/login")
async def login(username: str, password: str, response: Response):
    user = db.query(User).filter(User.username == username).first()
    if verify_password(password, user.password_hash):
        response.set_cookie("kanban_session", session_token)
        return {"message": "Login successful"}
```

**Коннеция:**
- Cookie имя: `kanban_session`
- HttpOnly: Да (защита от XSS)
- Secure: Зависит от окружения
- SameSite: Strict

### Авторизация

**Роли:**
- **Admin** — полный доступ к админ-панели
- **User** — доступ к доске и своим задачам

**Проверка:**
```python
@app.get("/admin")
async def admin_panel(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
```

### Password Security

**Требования:**
- Пароли НЕ хранятся в открытом виде
- Используется хеширование (можно улучшить с bcrypt)
- Пароли должны быть ≥ 8 символов

**Текущая реализация:**
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

**Рекомендация:** Использовать `bcrypt` для production

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
```

### CSRF Protection

**Статус:** Нужно добавить для production

**Решение:**
```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/tasks")
async def create_task(csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
```

---

## Performance

### Оптимизации

#### 1. Кэширование

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_sub_stages():
    return db.query(SubStage).all()
```

#### 2. Ленивая загрузка

```python
# Плохо: N+1 query problem
for task in tasks:
    print(task.assignee.full_name)  # 1 query для каждой задачи

# Хорошо: Eager loading
tasks = db.query(Task).options(joinedload(Task.assignee)).all()
```

#### 3. Пагинация

```python
@app.get("/api/tasks")
async def get_tasks(skip: int = 0, limit: int = 50):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks
```

#### 4. Индексы БД

```python
# В модели:
class Task(Base):
    __tablename__ = "tasks"
    status = Column(String(50), index=True)  # Частый фильтр
    assignee_id = Column(Integer, ForeignKey("users.id"), index=True)
```

### Bottlenecks

| Проблема | Причина | Решение |
| --- | --- | --- |
| Медленная загрузка доски | N+1 queries | Использовать joinedload() |
| Медленный экспорт в Excel | Итерация по всем данным | Пагинация, асинхронность |
| Большой размер БД | Без уборки старых данных | Архивирование, очистка |

---

## Масштабируемость (Future Improvements)

### Текущие ограничения

- ❌ SQLite не подходит для concurrent write operations (production)
- ❌ Нет кэширования между запросами
- ❌ Нет очереди задач (background jobs)

### Рекомендации для production

1. **Миграция БД:** SQLite → PostgreSQL
   ```python
   DATABASE_URL = "postgresql://user:pass@localhost/kanban"
   ```

2. **Кэширование:** Добавить Redis
   ```python
   from redis import Redis
   cache = Redis(host='localhost', port=6379)
   ```

3. **Background Jobs:** Celery для асинхронных задач
   ```python
   @celery.task
   def create_backup():
       backup_service.create_backup()
   ```

4. **Мониторинг:** Prometheus + Grafana
   ```python
   from prometheus_client import Counter
   ```

5. **Логирование:** ELK Stack
   ```python
   from pythonjsonlogger import jsonlogger
   ```

---

## Development Workflow

```
1. Разработчик создаёт ветку
   git checkout -b feature/new-feature

2. Вносит изменения в моделях
   models/models.py

3. Создаёт миграцию
   alembic revision --autogenerate -m "new_feature"

4. Добавляет бизнес-логику
   routers/new_router.py

5. Пишет тесты
   tests/test_new_feature.py

6. Коммитит изменения
   git commit -m "Add new feature"

7. Pushит в репозиторий
   git push origin feature/new-feature

8. Создаёт Pull Request
   Code review → Merge

9. Production deployment
   Применяет миграции → Запускает новый код
```

---

Последний обновлен: **2026-05-25**
