# 🤝 Руководство по контрибьютингу — Kanban Board

Спасибо, что хотите помочь развивать Kanban Board! Этот документ поможет вам начать.

---

## 📋 Содержание

1. [Начало работы](#начало-работы)
2. [Процесс разработки](#процесс-разработки)
3. [Стандарты кода](#стандарты-кода)
4. [Commit сообщения](#commit-сообщения)
5. [Pull Requests](#pull-requests)
6. [Частые вопросы](#частые-вопросы)

---

## Начало работы

### 1. Fork репозитория

```bash
# На GitHub: нажмите кнопку Fork
# Затем клонируйте ваш fork локально:
git clone https://github.com/YOUR_USERNAME/kanban-board.git
cd kanban-board
```

### 2. Создайте ветку для вашей работы

```bash
# Обновите главную ветку
git checkout main
git pull origin main

# Создайте новую ветку
git checkout -b feature/your-feature-name
# или для багфиксов:
git checkout -b bugfix/your-bugfix-name
```

### 3. Установите зависимости

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Запустите тесты

```bash
python -m unittest discover tests -v
```

Убедитесь, что все тесты проходят перед началом работы.

---

## Процесс разработки

### Шаг 1: Вносите изменения

```bash
# Отредактируйте файлы
# Добавьте код, исправьте ошибки и т.д.
```

### Шаг 2: Если изменили модели — создайте миграцию

```bash
# Добавьте новое поле в models/models.py
# Затем создайте миграцию:
alembic revision --autogenerate -m "descriptive_name"

# Примените миграцию локально для тестирования:
alembic upgrade head
```

### Шаг 3: Напишите или обновите тесты

```bash
# Добавьте тесты в tests/
# Пример: tests/test_my_feature.py
python -m unittest tests.test_my_feature -v
```

### Шаг 4: Проверьте код

```bash
# Убедитесь, что приложение запускается
uvicorn app:app --reload

# Откройте браузер и протестируйте функциональность
# http://localhost:8000
```

### Шаг 5: Коммитьте изменения

```bash
git add .
git commit -m "Add feature: description"
```

### Шаг 6: Push в ваш fork

```bash
git push origin feature/your-feature-name
```

### Шаг 7: Создайте Pull Request

- Откройте GitHub
- Нажмите "New Pull Request"
- Заполните описание PR (см. [Pull Requests](#pull-requests))

---

## Стандарты кода

### Python (PEP 8)

```python
# ✅ Хорошо
def create_task(title: str, description: str) -> Task:
    """Create a new task and return it."""
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
    return task


# ❌ Плохо
def create_task(title,description):
    task=Task(title=title,description=description)
    db.add(task)
    db.commit()
    return task
```

### Правила

1. **Имена переменных:** `snake_case` для переменных, `PascalCase` для классов
   ```python
   user_id = 1  # ✅
   UserId = 1   # ❌
   ```

2. **Максимальная длина строки:** 88 символов
   ```python
   # ✅ Хорошо
   very_long_variable_name = some_function(arg1, arg2, arg3)
   
   # ❌ Плохо (строка слишком длинная)
   very_long_variable_name = some_very_long_function_name(arg1, arg2, arg3, arg4, arg5)
   ```

3. **Импорты:** Группируйте в порядке (стандартная библиотека, сторонние, локальные)
   ```python
   # Стандартная библиотека
   from datetime import datetime
   from typing import List
   
   # Сторонние пакеты
   from fastapi import FastAPI
   from sqlalchemy import Column, Integer
   
   # Локальные импорты
   from database import SessionLocal
   from models.models import Task
   ```

4. **Документация:** Добавьте docstring для функций и классов
   ```python
   def get_task(task_id: int, db: Session) -> Task:
       """
       Retrieve a task by ID from the database.
       
       Args:
           task_id: The ID of the task
           db: Database session
           
       Returns:
           The Task object or None if not found
       """
       return db.query(Task).filter(Task.id == task_id).first()
   ```

5. **Type hints:** Добавьте типы для всех параметров и возвращаемых значений
   ```python
   # ✅ Хорошо
   def add_user(username: str, email: str) -> User:
       ...
   
   # ❌ Плохо
   def add_user(username, email):
       ...
   ```

### HTML/Jinja2 Templates

```html
<!-- ✅ Хорошо -->
<div class="task-card" data-task-id="{{ task.id }}">
  <h3>{{ task.title }}</h3>
  <p>{{ task.description }}</p>
</div>

<!-- ❌ Плохо -->
<div class=task-card>
  <h3>{{ task.title }}</h3>
  <p>{{task.description}}</p>
</div>
```

---

## Commit сообщения

### Формат

```
<type>: <subject>

<body>

<footer>
```

### Типы

- `feat:` — новая функция
- `fix:` — исправление ошибки
- `refactor:` — рефакторинг кода (без изменения функциональности)
- `test:` — добавление или обновление тестов
- `docs:` — обновление документации
- `chore:` — обновление зависимостей, конфигурации и т.д.
- `style:` — изменения форматирования (без логических изменений)

### Примеры

```bash
# ✅ Хорошо
git commit -m "feat: add task priority field to database"
git commit -m "fix: resolve N+1 query issue in get_tasks endpoint"
git commit -m "docs: update API documentation for task endpoints"
git commit -m "test: add unit tests for task creation"

# ❌ Плохо
git commit -m "updated stuff"
git commit -m "fixed bug"
git commit -m "WIP"
```

### Советы

- Используйте повелительное наклонение ("Add" вместо "Added")
- Первая строка ≤ 50 символов
- Объясните "почему", а не "что"
- Каждый коммит должен быть атомарным (решает одну задачу)

---

## Pull Requests

### Заголовок PR

```
[Category] Brief description

Examples:
[Feature] Add task priority levels
[Bugfix] Fix N+1 queries in board view
[Docs] Update DEVELOPMENT.md with Alembic guide
```

### Описание PR

```markdown
## 📝 Описание

Краткое описание что было сделано.

## 🎯 Цель

Почему это изменение нужно (какую проблему решает).

## 🔄 Тип изменения

- [ ] 🐛 Исправление ошибки
- [ ] ✨ Новая функция
- [ ] 📚 Документация
- [ ] ♻️ Рефакторинг
- [ ] 🧪 Тесты

## ✅ Чек-лист

- [ ] Код следует стандартам проекта (PEP 8)
- [ ] Добавлены unit-тесты
- [ ] Документация обновлена
- [ ] Созданы миграции (если изменены модели)
- [ ] Все тесты проходят (`python -m unittest discover tests -v`)
- [ ] Нет конфликтов с main веткой

## 📸 Screenshots (для UI изменений)

[Добавьте скриншоты если применимо]

## 🔗 Related Issues

Closes #123

## 📝 Дополнительная информация

[Добавьте дополнительную информацию если нужна]
```

### Что происходит после PR

1. **Code Review** — разработчики проверяют код
2. **CI/CD** — автоматические тесты
3. **Feedback** — могут быть запросы на изменения
4. **Merge** — когда всё хорошо, ваш PR сливается в main

---

## Частые вопросы

### ❓ Как обновить мою ветку если main изменилась?

```bash
# Обновите main
git checkout main
git pull origin main

# Вернитесь на вашу ветку
git checkout feature/your-feature

# Перебазируйте вашу ветку на main
git rebase main
```

### ❓ Как отменить последний коммит?

```bash
# Если не pushed:
git reset --soft HEAD~1

# Если pushed:
git revert HEAD
git push
```

### ❓ Я создал миграцию, но вы просите её изменить. Что делать?

```bash
# Если миграция ещё не применена:
# Отредактируйте файл миграции в migrations/versions/

# Если применена и нужно откатить:
alembic downgrade -1
# Отредактируйте модель и миграцию
alembic upgrade head
```

### ❓ Как добавить новую зависимость?

```bash
# Установите пакет
pip install new_package

# Обновите requirements.txt
pip freeze > requirements.txt

# Коммитьте изменения
git add requirements.txt
git commit -m "chore: add new_package dependency"
```

### ❓ Что если я хочу закрыть PR?

```bash
# На GitHub нажмите "Close pull request"
# Или через git:
git branch -d feature/your-feature
git push origin --delete feature/your-feature
```

### ❓ Как запустить мой код локально перед PR?

```bash
# 1. Убедитесь, что вы на вашей ветке
git branch

# 2. Запустите приложение
uvicorn app:app --reload

# 3. Откройте браузер
# http://localhost:8000

# 4. Тестируйте функциональность

# 5. Запустите тесты
python -m unittest discover tests -v
```

---

## 🎯 Основные области для контрибьютинга

### 🐛 Ищите баги?

Проверьте раздел Issues и выберите задачу с меткой `bug`.

### ✨ Хотите добавить функцию?

1. Откройте Issue с описанием функции
2. Дождитесь одобрения от мейнтейнеров
3. Начните разработку

### 📚 Хотите улучшить документацию?

Отредактируйте файлы:
- README.md
- DEVELOPMENT.md
- API.md
- ARCHITECTURE.md
- CONTRIBUTING.md (этот файл)

Обновления документации одобряются легче и быстрее!

### 🧪 Хотите добавить тесты?

Добавляйте unit-тесты в `tests/`:
```bash
# Новый файл теста
tests/test_my_feature.py

# Запустите:
python -m unittest tests.test_my_feature -v
```

---

## 📞 Нужна помощь?

- 💬 Создайте Issue с вопросом
- 📧 Посетите обсуждения проекта
- 📚 Прочитайте [DEVELOPMENT.md](DEVELOPMENT.md)
- 🏗️ Посетите [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🙏 Спасибо!

Мы ценим ваш вклад в развитие Kanban Board!

Последний обновлен: **2026-05-25**
