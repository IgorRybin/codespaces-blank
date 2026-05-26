# 👨‍💻 Гайд для разработчиков — Kanban Board

Этот документ содержит подробную информацию для разработчиков, работающих над проектом Kanban Board.

---

## 📋 Содержание

1. [Настройка среды разработки](#настройка-среды-разработки)
2. [Управление миграциями (Alembic)](#управление-миграциями-alembic)
3. [Структура моделей](#структура-моделей)
4. [Работа с маршрутами (Routers)](#работа-с-маршрутами-routers)
5. [Тестирование](#тестирование)
6. [Частые вопросы](#частые-вопросы)

---

## Настройка среды разработки

### Создание виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate    # Linux/macOS
# или
.venv\Scripts\activate        # Windows
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Проверка установки

```bash
python -c "import fastapi, sqlalchemy, alembic; print('✅ Все зависимости установлены')"
```

---

## Управление миграциями (Alembic)

### Что такое Alembic?

**Alembic** — это инструмент для управления версионированием схемы базы данных. Он отслеживает все изменения структуры таблиц и позволяет легко откатывать и переходить между версиями.

### Структура миграций

```
migrations/
├── alembic.ini                    # Конфигурация Alembic
├── env.py                         # Среда выполнения (импорты моделей)
├── script.py.mako                 # Шаблон для новых миграций
├── README
└── versions/
    └── ed3683054330_initial_migration.py  # Файл миграции
```

### Конфиг Alembic (alembic.ini)

Ключевая строка — подключение к БД:

```ini
sqlalchemy.url = sqlite+aiosqlite:///./database.db
```

**Важно:** Используется `sqlite+aiosqlite` (асинхронный драйвер), а не `sqlite://` (синхронный).

### Среда выполнения (migrations/env.py)

Этот файл импортирует ВСЕ модели для автогенерации:

```python
from database import Base
from models.models import User, SubStage, Task, Comment, TaskHistory

target_metadata = Base.metadata
```

**Правило:** При добавлении новой модели добавьте её импорт сюда!

### Рабочий процесс: создание и применение миграции

#### Шаг 1: Измените модель в `models/models.py`

```python
# Например, добавляем новое поле
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    priority = Column(String(50), default="medium")  # ← НОВОЕ ПОЛЕ
    # ... остальные поля
```

#### Шаг 2: Создайте миграцию

```bash
alembic revision --autogenerate -m "add_priority_to_task"
```

Это создаст файл в `migrations/versions/xxxxx_add_priority_to_task.py`:

```python
def upgrade() -> None:
    op.add_column('tasks', sa.Column('priority', sa.String(length=50), nullable=True))

def downgrade() -> None:
    op.drop_column('tasks', 'priority')
```

#### Шаг 3: Проверьте миграцию

Откройте файл миграции и убедитесь, что изменения корректны.

#### Шаг 4: Примените миграцию

```bash
alembic upgrade head
```

Вывод должен быть:
```
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, add_priority_to_task
```

#### Шаг 5: Коммитьте в Git

```bash
git add migrations/versions/
git commit -m "Add priority field to Task model"
```

### Полезные команды Alembic

| Команда | Описание |
| --- | --- |
| `alembic current` | Показать текущую версию миграции |
| `alembic history` | История всех миграций |
| `alembic upgrade head` | Применить все миграции до последней |
| `alembic downgrade -1` | Откатить последнюю миграцию |
| `alembic downgrade base` | Откатить все миграции |
| `alembic heads` | Показать все "головные" версии |
| `alembic branches` | Показать ветви миграций |

### Типичные ошибки и решения

#### ❌ Ошибка: "The asyncio extension requires an async driver"

**Причина:** Используется `sqlite://` вместо `sqlite+aiosqlite://`

**Решение:**
```bash
# Обновить alembic.ini
sqlalchemy.url = sqlite+aiosqlite:///./database.db

# Установить драйвер
pip install aiosqlite
```

#### ❌ Ошибка: "No such table" при миграции

**Причина:** Модель не импортирована в `migrations/env.py`

**Решение:**
```python
# Добавить в migrations/env.py
from models.models import YourNewModel
```

#### ❌ Ошибка: "Can't find referenced table"

**Причина:** Foreign Key ссылается на таблицу, которая ещё не создана

**Решение:** Отредактируйте файл миграции вручную, изменив порядок операций

---

## Структура моделей

### Базовые модели (models/models.py)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    color = Column(String(7), default="#3498db")
    is_active = Column(Boolean, default=True)
```

### Взаимосвязи между моделями

```
User (1) ──→ (N) Task           (creator_id, assignee_id)
User (1) ──→ (N) SubStage       (default_assignee_id)
SubStage (1) ──→ (N) Task       (sub_stage_id)
Task (1) ──→ (N) Comment        (task_id)
Task (1) ──→ (N) TaskHistory    (task_id)
```

### Создание новой модели

1. Добавьте класс в `models/models.py`:

```python
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#9b59b6")
```

2. Добавьте импорт в `migrations/env.py`:

```python
from models.models import User, SubStage, Task, Comment, TaskHistory, Tag
```

3. Создайте миграцию:

```bash
alembic revision --autogenerate -m "add_tag_model"
alembic upgrade head
```

---

## Работа с маршрутами (Routers)

### Структура маршрутов

```
routers/
├── auth.py          # POST /login, POST /logout, GET /me
├── board.py         # GET /, GET /board (UI)
├── tasks.py         # GET /api/tasks, POST /api/tasks/...
└── admin.py         # GET /admin, POST /admin/...
```

### Создание нового маршрута

#### 1. Создайте файл `routers/my_router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Task

router = APIRouter(prefix="/api", tags=["my-feature"])

@router.get("/my-endpoint")
async def get_my_data(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": [t.title for t in tasks]}
```

#### 2. Зарегистрируйте в `app.py`:

```python
from routers import my_router

app.include_router(my_router.router)
```

#### 3. Проверьте в браузере:

```
http://localhost:8000/docs  # Swagger документация
```

---

## Тестирование

### Запуск тестов

```bash
# Все тесты
python -m unittest discover tests -v

# Конкретный модуль
python -m unittest tests.test_app_import -v

# Конкретный тест
python -m unittest tests.test_app_import.TestAppImport.test_health_endpoint -v
```

### Структура тестов

```
tests/
└── test_app_import.py
```

### Написание нового теста

```python
import unittest
from fastapi.testclient import TestClient
from app import app

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_get_tasks(self):
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
    
    def test_create_task(self):
        response = self.client.post("/api/tasks", json={
            "title": "Test Task",
            "description": "A test task"
        })
        self.assertEqual(response.status_code, 201)

if __name__ == "__main__":
    unittest.main()
```

### Тестирование с БД

Для тестирования с реальной БД используйте `SessionLocal`:

```python
from database import SessionLocal
from models.models import Task

def test_with_db():
    db = SessionLocal()
    task = Task(title="Test", description="Test task")
    db.add(task)
    db.commit()
    
    result = db.query(Task).filter(Task.title == "Test").first()
    assert result is not None
    
    db.close()
```

---

## Частые вопросы

### ❓ Где хранится БД?

В файле `database.db` в корне проекта. Это SQLite файл.

```bash
ls -lah database.db
sqlite3 database.db ".tables"  # Список таблиц
```

### ❓ Как просмотреть данные в БД?

```bash
# Установить sqlite3
# На macOS:
brew install sqlite3
# На Ubuntu:
sudo apt-get install sqlite3

# Открыть БД
sqlite3 database.db

# Команды в SQLite:
.tables                    # Список таблиц
SELECT * FROM users;       # Просмотр пользователей
SELECT COUNT(*) FROM tasks; # Количество задач
```

### ❓ Как полностью пересоздать БД?

```bash
# 1. Удалить текущую БД
rm database.db

# 2. Пересоздать таблицы (запустить app)
python app.py

# 3. Или применить миграции
alembic upgrade head
```

### ❓ Можно ли изменить пароль пользователя в БД?

```bash
sqlite3 database.db

-- Обновить пароль (NOTE: В проекте пароли хешируются!)
-- Это примерная команда, используйте app UI для смены пароля
UPDATE users SET password_hash = 'new_hash' WHERE username = 'admin';
```

### ❓ Как добавить поле в существующую таблицу?

1. Отредактируйте модель в `models/models.py`
2. Создайте миграцию:
   ```bash
   alembic revision --autogenerate -m "add_new_field"
   ```
3. Примените миграцию:
   ```bash
   alembic upgrade head
   ```

### ❓ Почему миграция пустая (только pass)?

Если `alembic revision --autogenerate` создаёт пустую миграцию:
- Возможно, Alembic не обнаружил изменений
- Или таблицы уже существуют в БД

**Решение:** Удалите БД и пересоздайте:
```bash
rm database.db
alembic upgrade head
```

### ❓ Как откатить миграцию?

```bash
# На 1 версию назад
alembic downgrade -1

# На 2 версии назад
alembic downgrade -2

# На конкретную версию
alembic downgrade ed3683054330

# На начало (удалить все таблицы)
alembic downgrade base
```

### ❓ Как заливать изменения в Git?

```bash
# Изменили модели
git add models/models.py

# Создали миграцию
git add migrations/versions/

# Коммитьте вместе
git commit -m "Add priority field to Task model"
```

**Важно:** Никогда не коммитьте `database.db` — он генерируется автоматически!

---

## 🚀 Быстрые команды

```bash
# Запуск приложения с перезагрузкой
uvicorn app:app --reload

# Смотреть API документацию
curl http://localhost:8000/docs

# Создать миграцию
alembic revision --autogenerate -m "your_change_name"

# Применить миграции
alembic upgrade head

# Откатить последнюю
alembic downgrade -1

# История миграций
alembic history

# Текущая версия
alembic current

# Запустить тесты
python -m unittest discover tests -v

# Посмотреть БД
sqlite3 database.db
```

---

## 📞 Нужна помощь?

Если возникла проблема:

1. Проверьте лог ошибки в терминале
2. Посмотрите в этом документе раздел "Частые вопросы"
3. Посетите [Alembic документацию](https://alembic.sqlalchemy.org/)
4. Посетите [FastAPI документацию](https://fastapi.tiangolo.com/)
5. Посетите [SQLAlchemy документацию](https://docs.sqlalchemy.org/)

Удачи в разработке! 🎉
