# 📖 Индекс документации — Kanban Board

Полный указатель и справочник по всей документации проекта.

---

## 🚀 Начните отсюда

Новички должны начать с этих разделов в таком порядке:

1. **[README.md](README.md)** — Общее описание проекта, быстрый старт (5 мин)
2. **[INSTALLATION.md](INSTALLATION.md)** — Установка на вашу систему (10-15 мин)
3. **[API.md](API.md)** — Как использовать REST API (5 мин)
4. **[DEVELOPMENT.md](DEVELOPMENT.md)** — Для разработчиков, работа с кодом (15 мин)

---

## 📚 Полный справочник

### 📖 Основные документы

| Документ | Объём | Аудитория | Назначение |
| --- | --- | --- | --- |
| **[README.md](README.md)** | 333 строк | Все | Обзор проекта, быстрый старт, дефолт учётные данные |
| **[INSTALLATION.md](INSTALLATION.md)** | 512 строк | Новички | Подробная установка (Linux, macOS, Windows, Docker) |
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | 508 строк | Разработчики | Управление Alembic, миграции, тестирование, FAQ |
| **[API.md](API.md)** | 727 строк | Backend, Интеграторы | Все REST endpoints, примеры, коды ошибок |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 573 строк | Архитекторы, Senior разработчики | Дизайн, слои, ERD, performance, масштабируемость |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 458 строк | Контрибьютеры | Как внести вклад, стандарты кода, PR процесс |
| **[INDEX.md](INDEX.md)** | Этот файл | Все | Навигация по документации |

**Общий размер документации:** 3111 строк (~30-40 минут чтения)

---

## 🎯 Поиск по задачам

### "Как установить проект?"
→ [INSTALLATION.md](INSTALLATION.md)
- Установка на Linux
- Установка на macOS
- Установка на Windows
- Docker инструкции

### "Как запустить приложение?"
→ [README.md#🚀-быстрый-запуск](README.md#-быстрый-запуск)
```bash
uvicorn app:app --reload
```

### "Какие есть endpoint'ы?"
→ [API.md](API.md)
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}
- И ещё 20+ endpoint'ов

### "Как создать миграцию?"
→ [DEVELOPMENT.md#рабочий-процесс-создание-и-применение-миграции](DEVELOPMENT.md#рабочий-процесс-создание-и-применение-миграции)
```bash
alembic revision --autogenerate -m "my_change"
alembic upgrade head
```

### "Как написать тесты?"
→ [DEVELOPMENT.md#тестирование](DEVELOPMENT.md#тестирование)

### "Как внести вклад в проект?"
→ [CONTRIBUTING.md](CONTRIBUTING.md)
- Процесс разработки
- Стандарты кода
- Commit сообщения
- Pull Request процесс

### "Какова архитектура проекта?"
→ [ARCHITECTURE.md](ARCHITECTURE.md)
- Трёхслойная архитектура
- Диаграмма компонентов
- Database Design
- Security
- Performance

### "Как решить проблему при установке?"
→ [INSTALLATION.md#решение-проблем](INSTALLATION.md#решение-проблем)

### "Почему проект использует Alembic?"
→ [DEVELOPMENT.md#что-такое-alembic](DEVELOPMENT.md#что-такое-alembic)

### "Какие default учётные данные?"
→ [README.md#-учётные-записи](README.md#-учётные-записи)

### "Как получить доступ с другого компьютера?"
→ [README.md#4-доступ-с-других-машин](README.md#4-доступ-с-других-машин)

---

## 🏗️ Архитектура быстрая справка

### Структура папок
```
kanban-board/
├── app.py              ← Точка входа
├── database.py         ← БД конфиг
├── models/models.py    ← ORM модели
├── routers/            ← API endpoints
├── templates/          ← HTML шаблоны
├── services/           ← Бизнес-логика
├── migrations/         ← Alembic миграции
└── tests/              ← Unit-тесты
```

### Стек технологий
- **FastAPI** — Web framework
- **SQLAlchemy** — ORM
- **SQLite** — База данных
- **Alembic** — Миграции
- **Jinja2** — Templates
- **Uvicorn** — ASGI сервер

### Основные модели
- **User** — Пользователи
- **Task** — Задачи
- **SubStage** — Статусы в "В работе"
- **Comment** — Комментарии
- **TaskHistory** — История изменений

---

## 🔐 Аутентификация быстрая справка

### Дефолтные пользователи

| Логин | Пароль | Роль |
| --- | --- | --- |
| admin | admin | Администратор |
| pavel | pavel | Разработчик |
| elena | elena | Дизайнер |
| dmitry | dmitry | Тестировщик |
| anna | anna | Менеджер |

**Важно:** Эти данные только для разработки. В production используйте безопасные пароли!

---

## 📡 API быстрая справка

### Аутентификация
```
POST /login         — Вход
POST /logout        — Выход
GET  /me            — Текущий пользователь
```

### Задачи
```
GET    /api/tasks           — Получить все
POST   /api/tasks           — Создать
GET    /api/tasks/{id}      — Получить одну
PUT    /api/tasks/{id}      — Обновить
DELETE /api/tasks/{id}      — Удалить
POST   /api/tasks/{id}/comment  — Добавить комментарий
POST   /api/tasks/{id}/move     — Переместить в другой статус
```

### Админ
```
GET  /admin                 — Админ-панель
GET  /api/admin/users       — Получить пользователей
POST /api/admin/users       — Создать пользователя
PUT  /api/admin/users/{id}  — Обновить
DELETE /api/admin/users/{id} — Удалить
POST /api/admin/backup      — Создать резервную копию
```

Полная документация: [API.md](API.md)

---

## 🛠️ Разработка быстрая справка

### Запуск
```bash
# С перезагрузкой
uvicorn app:app --reload

# Или напрямую
python app.py
```

### Миграции
```bash
# Создать
alembic revision --autogenerate -m "name"

# Применить
alembic upgrade head

# Откатить
alembic downgrade -1

# История
alembic history
alembic current
```

### Тесты
```bash
# Все
python -m unittest discover tests -v

# Конкретный
python -m unittest tests.test_app_import -v
```

### API документация
```
http://localhost:8000/docs     ← Swagger UI
http://localhost:8000/redoc    ← ReDoc
```

---

## 🎓 Обучающие материалы

### Для новичков
1. Прочитайте [README.md](README.md) — узнайте что это
2. Установите через [INSTALLATION.md](INSTALLATION.md)
3. Попробуйте [API.md](API.md) endpoints
4. Прочитайте [ARCHITECTURE.md](ARCHITECTURE.md) для понимания структуры

### Для разработчиков
1. [DEVELOPMENT.md](DEVELOPMENT.md) — как кодить
2. [ARCHITECTURE.md](ARCHITECTURE.md) — как всё организовано
3. [CONTRIBUTING.md](CONTRIBUTING.md) — как помочь проекту

### Для DevOps/Архитекторов
1. [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура и design
2. [INSTALLATION.md](INSTALLATION.md) — как развернуть
3. [DEVELOPMENT.md#масштабируемость-future-improvements](DEVELOPMENT.md#масштабируемость-future-improvements) — как масштабировать

---

## 🔍 Вход в документацию по ролям

### 👤 Я новичок, где начать?
1. [README.md](README.md) (5 мин)
2. [INSTALLATION.md](INSTALLATION.md) (15 мин)
3. Попробуйте запустить приложение

### 👨‍💻 Я разработчик Python
1. [INSTALLATION.md](INSTALLATION.md) (установка)
2. [ARCHITECTURE.md](ARCHITECTURE.md) (понимание кода)
3. [DEVELOPMENT.md](DEVELOPMENT.md) (как писать код)
4. [CONTRIBUTING.md](CONTRIBUTING.md) (как помочь)

### 🔌 Я разработчик Frontend
1. [API.md](API.md) (какие endpoints есть)
2. [ARCHITECTURE.md](ARCHITECTURE.md) — раздел "Поток данных"
3. Примеры curl запросов в [API.md](API.md)

### 🏗️ Я архитектор/DevOps
1. [ARCHITECTURE.md](ARCHITECTURE.md) (архитектура и масштабируемость)
2. [INSTALLATION.md](INSTALLATION.md) (development & Docker)
3. [DEVELOPMENT.md#масштабируемость-future-improvements](DEVELOPMENT.md#масштабируемость-future-improvements) (production improvements)

### 🤝 Я хочу внести вклад
1. [CONTRIBUTING.md](CONTRIBUTING.md) (правила)
2. [DEVELOPMENT.md](DEVELOPMENT.md) (как писать код)
3. Выберите Issue на GitHub

---

## 📊 Статистика документации

| Метрика | Значение |
| --- | --- |
| Всего документов | 6 основных + этот |
| Всего строк | 3111 |
| Всего символов | ~85 KB |
| Средний размер файла | ~520 строк |
| Время чтения всего | 30-40 минут |
| Быстрый старт | 5 минут |

---

## 🔗 Быстрые ссылки

### На GitHub
- [Repository](https://github.com/IgorRybin/kanban-board)
- [Issues](https://github.com/IgorRybin/kanban-board/issues)
- [Discussions](https://github.com/IgorRybin/kanban-board/discussions)

### На документацию проектов
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy docs](https://docs.sqlalchemy.org/)
- [Alembic docs](https://alembic.sqlalchemy.org/)
- [Python docs](https://docs.python.org/3.12/)

### На локальный сервер (при запуске)
- [Главная](http://localhost:8000)
- [Swagger API docs](http://localhost:8000/docs)
- [ReDoc API docs](http://localhost:8000/redoc)
- [Health endpoint](http://localhost:8000/health)

---

## 💡 Советы

1. **Используйте Ctrl+F** для поиска в документе
2. **Читайте README первым** — это самое важное
3. **Для кодирования** смотрите DEVELOPMENT.md
4. **Для интеграции** используйте API.md
5. **Для production** читайте ARCHITECTURE.md

---

## ❓ FAQ

**В: Где дефолтные пароли?**
A: [README.md#-учётные-записи](README.md#-учётные-записи)

**В: Как создать миграцию?**
A: [DEVELOPMENT.md#рабочий-процесс-создание-и-применение-миграции](DEVELOPMENT.md#рабочий-процесс-создание-и-применение-миграции)

**В: Какие есть API endpoints?**
A: [API.md](API.md)

**В: Как установить на Windows?**
A: [INSTALLATION.md#windows](INSTALLATION.md#windows)

**В: Как помочь проекту?**
A: [CONTRIBUTING.md](CONTRIBUTING.md)

**В: Как это все работает?**
A: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📞 Нужна помощь?

- 📖 Посмотрите в документации
- 💬 Создайте Issue на GitHub
- 📧 Посетите Discussions
- 🐛 Найдите решение в [FAQ](DEVELOPMENT.md#частые-вопросы)

---

**Последний обновлен:** 2026-05-25

**Версия документации:** 1.0

**Версия Kanban Board:** 1.0.0
