# Kanban Board — командная канбан-доска

**Kanban Board** — это лёгкое и понятное приложение для управления задачами малой команды. Основная идея: минимальная зависимость, быстрый запуск, удобное управление задачами и пользователями через браузер.

Проект использует **FastAPI** для REST API, **SQLAlchemy** ORM с **SQLite** для хранения данных, **Jinja2** для server-side rendering, и **Alembic** для управления миграциями базы данных.

---

## 🚀 Быстрый запуск

### 1. Подготовка среды

Требуется **Python 3.12+**.

```bash
# Создание виртуального окружения
python3 -m venv .venv

# Активация окружения
# На Linux/macOS:
source .venv/bin/activate
# На Windows:
.venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Инициализация базы данных

Миграции управляются через **Alembic**. При первом запуске таблицы создадутся автоматически:

```bash
# Применить последнюю миграцию
alembic upgrade head
```

### 3. Запуск сервера

```bash
# Запуск FastAPI с автоперезагрузкой (разработка)
uvicorn app:app --reload

# Или напрямую
python app.py
```

- FastAPI запускается на **`http://localhost:8000`**
- API документация доступна на **`http://localhost:8000/docs`**
- Канбан-доска (UI) доступна по адресу **`http://localhost:8000/`**

### 4. Доступ с других машин

Чтобы дать доступ коллегам из офиса, используйте IP машины вместо `localhost`:

```bash
# На Linux найти IP:
hostname -I

# Затем открыть в браузере:
http://192.168.1.10:8000
```

---

## � Учётные записи

При первом запуске приложения создаются 5 demo-пользователей. Пароль совпадает с логином.

| Имя | Логин | Пароль | Роль |
| --- | --- | --- | --- |
| Иван Иванов | `admin` | `admin` | Администратор |
| Павел Петров | `pavel` | `pavel` | Разработчик |
| Елена Сидорова | `elena` | `elena` | Дизайнер |
| Дмитрий Козлов | `dmitry` | `dmitry` | Тестировщик |
| Анна Морозова | `anna` | `anna` | Менеджер |

---

## 🔐 Админ-панель

**Роль Admin** даёт доступ к админ-панели (`/admin`), где доступно:

- создание новых пользователей;
- смена пароля для существующих пользователей;
- удаление пользователей (кроме `admin`);
- создание, редактирование и удаление подэтапов для раздела «В работе»;
- создание резервных копий базы данных и скачивание архива.

---

## 🧱 Архитектура проекта

### Структура директорий

```
.
├── app.py                   # Точка входа FastAPI, сидирование БД
├── config.py               # Конфигурация приложения
├── database.py             # SQLAlchemy engine и SessionLocal
├── requirements.txt        # Python-зависимости (fastapi, sqlalchemy, alembic и т.д.)
├── README.md              # Этот файл
├── docs/                  # Дополнительная документация и руководства
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── DEVELOPMENT.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   └── MAINTENANCE.md
├── models/
│   ├── __init__.py
│   └── models.py           # ORM-модели (User, Task, SubStage, Comment, TaskHistory)
│
├── routers/
│   ├── __init__.py
│   ├── auth.py            # Аутентификация и управление сессиями
│   ├── board.py           # Основной интерфейс канбан-доски
│   ├── tasks.py           # API для работы с задачами
│   └── admin.py           # Админ-панель
│
├── services/
│   ├── __init__.py
│   ├── backup_service.py  # Резервные копии БД
│   └── excel_service.py   # Экспорт в Excel
│
├── templates/
│   ├── admin.html
│   ├── board.html
│   ├── login.html
│   └── partials/          # Переиспользуемые компоненты HTML
│       └── task_details.html
│
├── tests/
│   └── test_app_import.py # Базовые unit-тесты
│
├── migrations/            # Alembic структура для миграций
│   ├── alembic.ini       # Конфиг Alembic
│   ├── env.py            # Среда выполнения миграций
│   ├── script.py.mako    # Шаблон для новых миграций
│   └── versions/         # Файлы миграций
│       └── ed3683054330_initial_migration.py
│
├── .venv/                # Виртуальное окружение (не коммитим)
├── database.db           # SQLite БД (не коммитим)
└── backups/              # Резервные копии (не коммитим)
```

### Основные компоненты

- **app.py** — FastAPI приложение, регистрация маршрутов, сидирование БД
- **database.py** — SQLAlchemy engine, sessionmaker, Base для всех моделей
- **models/models.py** — 5 ORM-моделей: User, SubStage, Task, Comment, TaskHistory
- **routers/** — HTTP-маршруты и обработчики
- **services/** — бизнес-логика (резервные копии, экспорт)
- **templates/** — Jinja2 шаблоны (server-side rendering)
- **migrations/** — Alembic структура для версионирования схемы БД

---

## 💾 Управление базой данных

### Alembic и миграции

Проект использует **Alembic** для управления версионированием схемы БД. Это позволяет:
- Отслеживать все изменения схемы в Git
- Легко откатывать и переходить между версиями БД
- Совместно работать над моделями без конфликтов

**Текущая версия миграции:**
```bash
alembic current
```
Вывод: `ed3683054330 (head)`

**История миграций:**
```bash
alembic history
```

**Создать новую миграцию** после изменения моделей в `models/models.py`:
```bash
alembic revision --autogenerate -m "описание_изменения"
```

**Применить миграции:**
```bash
alembic upgrade head
```

**Откатить последнюю миграцию:**
```bash
alembic downgrade -1
```

Подробнее см. [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

---

## ⚙️ Конфигурация

Основные настройки хранятся в `config.py`:

```python
DATABASE_URL = "sqlite:///database.db"
SESSION_COOKIE_NAME = "kanban_session"
BACKUP_ENABLED = True
BACKUP_INTERVAL = "daily"
BACKUP_FOLDER = "backups"
```

Для использования переменных окружения создайте файл `.env` в корне проекта:

```bash
DATABASE_URL=sqlite:///database.db
SESSION_COOKIE_NAME=kanban_session
BACKUP_ENABLED=true
```

---

## 📦 Зависимости проекта

| Пакет | Версия | Назначение |
| --- | --- | --- |
| **fastapi** | >=0.100.0 | Web-фреймворк |
| **uvicorn** | >=0.20.0 | ASGI-сервер |
| **sqlalchemy** | >=2.0.0 | ORM |
| **aiosqlite** | >=0.22.1 | Async SQLite драйвер для Alembic |
| **alembic** | >=1.18.4 | Управление миграциями БД |
| **jinja2** | >=3.0.0 | Server-side templates |
| **python-multipart** | >=0.0.6 | Обработка формяов |
| **openpyxl** | >=3.1.0 | Экспорт в Excel |
| **httpx** | >=0.27.0 | HTTP client для тестов |

Установка зависимостей:
```bash
pip install -r requirements.txt
```

---

## ✅ Тестирование

Базовые unit-тесты находятся в `tests/`:

```bash
# Запуск всех тестов
python -m unittest discover tests -v

# Запуск конкретного теста
python -m unittest tests.test_app_import -v
```

Текущее покрытие:
- ✅ `test_app_import.py` — проверка импорта приложения и /health endpoint

---

## 📚 Документация

Проект включает основную документацию в корне и расширенную документацию в папке `docs/`.

| Документ | Описание |
| --- | --- |
| **[README.md](README.md)** | 📖 Общее описание проекта (этот файл) |
| **[docs/README.md](docs/README.md)** | 📄 Навигация по документации и обзор проекта |
| **[docs/INSTALLATION.md](docs/INSTALLATION.md)** | 💻 Подробная инструкция по установке |
| **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** | 👨‍💻 Гайд для разработчиков и работа с Alembic |
| **[docs/API.md](docs/API.md)** | 📡 Полная документация REST API |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | 🏗️ Архитектура проекта и ключевые решения |
| **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** | 🤝 Руководство по контрибьютингу |

### Быстрые команды для разработки

```bash
# Запуск с автоперезагрузкой
uvicorn app:app --reload

# Просмотр API документации в браузере
# http://localhost:8000/docs

# Создание миграции после изменения моделей
alembic revision --autogenerate -m "my_change"

# Применение миграций
alembic upgrade head

# Просмотр текущей версии миграции
alembic current

# Запуск тестов
python -m unittest discover tests -v
```

---

## 🛠️ Поддержка и контрибьютинг

Для поддержки и внесения изменений используйте следующие шаги:

1. **Обновите документацию** — `README.md` и файлы в `docs/`.
2. **Проверяйте структуру** — список файлов и назначение модулей.
3. **Тестируйте изменения** — `python -m unittest discover tests`.
4. **Соблюдайте семантику коммитов**:
   - `fix:` — багфикс;
   - `feat:` — новая функциональность;
   - `docs:` — документация;
   - `refactor:` — чистка кода.

Подробнее по процессу поддержки — `docs/MAINTENANCE.md`.

---

## 📚 Документация проекта

Дополнительные руководства доступны в папке `docs/`:

- `docs/README.md` — обзор проекта и навигация по документации;
- `docs/MAINTENANCE.md` — инструкция по поддержке, ветвлению и изменению функционала;
- `docs/API.md` — структура API, OpenAPI / Swagger и список маршрутов.

---

## ✅ Тестирование

```bash
python -m unittest discover tests
```

---

## 🧠 Вайб кодинга

Пиши изменения аккуратно и понятно:

- небольшие коммиты;
- ясные имена функций и шаблонов;
- не ломай админскую логику при каждом изменении;
- поддерживай совместимость с SQLite и серверными шаблонами.
