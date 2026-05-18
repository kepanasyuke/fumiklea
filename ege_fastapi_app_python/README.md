# EGE Math Trainer 2026

Лёгкое FastAPI-приложение для тренировки решений ЕГЭ по математике.

## Структура проекта

- `app/` — основной Python-приложение
  - `app/main.py` — FastAPI-приложение и маршруты
  - `app/core/` — настройки, зависимости, безопасность и исключения
  - `app/api/v1/` — REST API версия 1
  - `app/domain/` — доменные модели и сервисы
  - `app/infrastructure/` — SQLAlchemy, репозитории и внешние сервисы
  - `app/schemas/` — Pydantic-схемы
- `web/` — статические фронтенд-ресурсы
- `data/` — файловая база данных SQLite
- `Dockerfile` — контейнерная сборка
- `docker-compose.yml` — запуск контейнера и сервисов
- `requirements.txt` — Python-зависимости
- `.env.example` — пример переменных окружения

## Быстрый старт

1. Установить зависимости:

```bash
cd ege_fastapi_app_python
make install
```

2. Запустить приложение локально:

```bash
make run
```

3. Перейти в браузер:

```bash
make open
```

4. Для проброса через `localtunnel`:

```bash
make tunnel
```

## Docker

Собрать контейнер:

```bash
make build
```

Запустить контейнер:

```bash
make up
```

Остановить контейнеры:

```bash
make down
```

Просмотр логов:

```bash
make logs
```

Очистить артефакты и локальную БД:

```bash
make clean
```

## Настройки

Проект читает `.env` в корне (через `pydantic-settings`). Если нужно, скопируйте `.env.example`:

```bash
cp .env.example .env
```

### Важные пути

- Статический фронтенд: `web/`
- Точка входа FastAPI: `app/main.py`
- SQLite БД: `data/ege_math.db`

## Примечание

Сервер на `uvicorn` запускается из корня проекта, поэтому важно оставаться в папке `ege_fastapi_app_python` перед выполнением `make`.
