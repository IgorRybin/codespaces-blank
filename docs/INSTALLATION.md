# 💻 Инструкция по установке — Kanban Board

Подробные пошаговые инструкции по установке проекта на разные операционные системы.

---

## 📋 Содержание

1. [Требования](#требования)
2. [Linux/macOS](#linuxmacos)
3. [Windows](#windows)
4. [Docker (опционально)](#docker-опционально)
5. [Первый запуск](#первый-запуск)
6. [Проверка установки](#проверка-установки)
7. [Решение проблем](#решение-проблем)

---

## Требования

### Обязательное

- **Python 3.12+** (скачайте с [python.org](https://www.python.org))
- **Git** (скачайте с [git-scm.com](https://git-scm.com))
- **~50 MB** свободного места на диске

### Опционально

- **Docker** (если хотите запустить в контейнере)
- **SQLite3** (для работы с БД напрямую, обычно уже установлен)
- **Visual Studio Code** (рекомендуется для разработки)

---

## Linux/macOS

### Шаг 1: Проверка версии Python

```bash
python3 --version
# Должно быть 3.12 или выше
```

Если Python не установлен или версия старая:

**На Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv git
```

**На macOS (с Homebrew):**
```bash
brew install python@3.12 git
```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/IgorRybin/kanban-board.git
cd kanban-board
```

Или если используете свой fork:
```bash
git clone https://github.com/YOUR_USERNAME/kanban-board.git
cd kanban-board
```

### Шаг 3: Создание виртуального окружения

```bash
# Создать виртуальное окружение
python3 -m venv .venv

# Активировать окружение
source .venv/bin/activate

# Проверить, что активировано (слева от команды должно быть (.venv))
which python
```

### Шаг 4: Установка зависимостей

```bash
# Обновить pip
pip install --upgrade pip

# Установить зависимости из requirements.txt
pip install -r requirements.txt

# Проверить установку
pip list | grep -E "fastapi|sqlalchemy|alembic"
```

### Шаг 5: Инициализация базы данных

```bash
# Применить миграции
alembic upgrade head

# Проверить текущую версию миграции
alembic current
# Должно вывести: ed3683054330 (head)

# Проверить наличие БД
ls -lah database.db
# Должен быть файл ~50KB
```

### Шаг 6: Запуск приложения

```bash
# Запустить с автоперезагрузкой (для разработки)
uvicorn app:app --reload

# ИЛИ просто
python app.py
```

Вывод:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Шаг 7: Открытие в браузере

Откройте http://localhost:8000

Вы должны увидеть форму логина. Используйте учётные данные:
- **Логин:** admin
- **Пароль:** admin

---

## Windows

### Шаг 1: Установка Python

1. Перейдите на [python.org/downloads](https://www.python.org/downloads)
2. Скачайте **Python 3.12** для Windows
3. Запустите установщик
4. **ВАЖНО:** Отметьте ☑ "Add Python to PATH"
5. Нажмите "Install Now"

### Шаг 2: Проверка установки

Откройте **Command Prompt** (cmd.exe) или **PowerShell**:

```cmd
python --version
# Должно быть 3.12 или выше
```

### Шаг 3: Клонирование репозитория

```cmd
git clone https://github.com/IgorRybin/kanban-board.git
cd kanban-board
```

### Шаг 4: Создание виртуального окружения

```cmd
# Создать
python -m venv .venv

# Активировать
.venv\Scripts\activate

# Должна появиться приставка (.venv) перед командой
```

### Шаг 5: Установка зависимостей

```cmd
# Обновить pip
python -m pip install --upgrade pip

# Установить требуемые пакеты
pip install -r requirements.txt
```

### Шаг 6: Инициализация базы данных

```cmd
# Применить миграции
alembic upgrade head

# Проверить
alembic current
```

### Шаг 7: Запуск

```cmd
# Запустить приложение
python app.py

# ИЛИ через uvicorn
uvicorn app:app --reload
```

### Шаг 8: Доступ

Откройте браузер и перейдите на http://localhost:8000

---

## Docker (опционально)

Если у вас установлен Docker, можете запустить приложение в контейнере.

### Создание Dockerfile

Создайте файл `Dockerfile` в корне проекта:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY . .

# Инициализировать БД
RUN alembic upgrade head || true

# Запустить приложение
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Создание .dockerignore

```
.venv
.git
__pycache__
*.pyc
database.db
backups
exports
.env
```

### Запуск контейнера

```bash
# Собрать образ
docker build -t kanban-board .

# Запустить контейнер
docker run -p 8000:8000 kanban-board

# Приложение доступно на http://localhost:8000
```

### Docker Compose (для production)

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database.db:/app/database.db
      - ./backups:/app/backups
    environment:
      - DATABASE_URL=sqlite:///./database.db
```

Запуск:
```bash
docker-compose up
```

---

## Первый запуск

### Что происходит при первом запуске?

1. **Создание БД** — если БД не существует, создаётся новая
2. **Применение миграций** — создаются таблицы
3. **Сидирование** — добавляются demo-пользователи

### После первого запуска

```
✅ Приложение работает
✅ БД инициализирована (database.db создана)
✅ 5 demo-пользователей добавлены
✅ 4 подэтапа созданы
```

### Доступ

| Логин | Пароль | Роль |
| --- | --- | --- |
| admin | admin | Администратор |
| pavel | pavel | Разработчик |
| elena | elena | Дизайнер |
| dmitry | dmitry | Тестировщик |
| anna | anna | Менеджер |

---

## Проверка установки

### 1. Проверить Python

```bash
python3 --version
# Должно быть 3.12+

python3 -c "import sys; print(sys.executable)"
# Должна быть ссылка на .venv
```

### 2. Проверить окружение

```bash
# Linux/macOS
which python
# Должна быть ссылка на .venv/bin/python

# Windows
where python
# Должна быть ссылка на .venv\Scripts\python.exe
```

### 3. Проверить установленные пакеты

```bash
pip list | grep -E "fastapi|sqlalchemy|alembic|uvicorn"
# Должны быть все эти пакеты
```

### 4. Проверить БД

```bash
# Файл должен существовать
ls -lah database.db

# Проверить таблицы
sqlite3 database.db ".tables"
# Должны быть: comments, sub_stages, task_histories, tasks, users
```

### 5. Запустить тесты

```bash
python -m unittest discover tests -v
# Должны быть зелёные галочки (OK)
```

### 6. Проверить API

```bash
curl -X GET http://localhost:8000/health
# Должен вернуть: {"status": "ok"}
```

---

## Решение проблем

### ❌ Ошибка: "Python 3.12 не найден"

**Решение:**
```bash
# Проверить установленные версии Python
python3 --version

# Установить Python 3.12
# Linux:
sudo apt install python3.12

# macOS:
brew install python@3.12

# Использовать конкретную версию
python3.12 -m venv .venv
```

### ❌ Ошибка: "No module named 'fastapi'"

**Решение:**
```bash
# Убедитесь, что окружение активировано
source .venv/bin/activate    # Linux/macOS
# или
.venv\Scripts\activate        # Windows

# Переустановите зависимости
pip install -r requirements.txt
```

### ❌ Ошибка: "Address already in use" при запуске

**Решение:**
```bash
# Другой сервис уже использует порт 8000
# Используйте другой порт:
uvicorn app:app --port 8001

# ИЛИ найдите и убейте процесс на порту 8000
# Linux/macOS:
lsof -i :8000
kill -9 PID

# Windows:
netstat -ano | findstr :8000
taskkill /PID PID /F
```

### ❌ Ошибка: "The asyncio extension requires an async driver to be used"

**Решение:**
```bash
# Установить aiosqlite
pip install aiosqlite

# Проверить alembic.ini
grep sqlalchemy.url alembic.ini
# Должно быть: sqlite+aiosqlite:///./database.db

# Если нет, отредактируйте вручную
```

### ❌ Ошибка: "database.db is locked"

**Решение:**
```bash
# Закройте все другие подключения к БД
# Удалите БД и создайте новую
rm database.db
alembic upgrade head

# Или используйте WAL mode:
sqlite3 database.db "PRAGMA journal_mode=WAL;"
```

### ❌ Ошибка при входе: "Login failed"

**Решение:**
```bash
# Пересоздайте БД
rm database.db
python app.py    # Запустит сидирование

# Используйте правильные учётные данные
# Логин: admin
# Пароль: admin
```

### ❌ Медленное выполнение команд

**Решение:**
```bash
# Убедитесь, что используется правильный Python
which python
# Должна быть ссылка на .venv

# Переустановите зависимости
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## ✅ Успешная установка

Если вы видите это:
1. ✅ Приложение запустилось без ошибок
2. ✅ Браузер открыл http://localhost:8000
3. ✅ Вы смогли войти с admin/admin
4. ✅ Видите канбан-доску

**Поздравляем! Установка успешна! 🎉**

---

## 📚 Дальнейшие шаги

После установки:

1. **Прочитайте документацию:** [README.md](README.md)
2. **Для разработки:** [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Для API:** [API.md](API.md)
4. **Для архитектуры:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🤝 Нужна помощь?

- Создайте Issue на GitHub
- Проверьте раздел [Решение проблем](#решение-проблем)
- Посетите обсуждения проекта

---

Последний обновлен: **2026-05-25**
