# Selectel Vacancies API — исправленная версия

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**FastAPI‑приложение для парсинга публичных вакансий Selectel с CRUD‑интерфейсом и фоновым обновлением данных.**

---

## О проекте

Данный репозиторий содержит **полностью отлаженную версию** тестового задания.  
Исходный код включал 8 намеренных багов — все они устранены.  
Проект успешно запускается в Docker, парсит вакансии, сохраняет их в PostgreSQL и предоставляет полный набор CRUD‑операций.
---

## Как запустить

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/alexey-smirnov/selectel-vacancies-fixed.git
   cd selectel-vacancies-fixed
   ```

2. Создайте файл `.env` из шаблона:
   ```bash
   cp .env.example .env
   ```

3. Запустите контейнеры:
   ```bash
   docker compose up --build
   ```

После успешного старта:
- API будет доступно по адресу [http://localhost:8000](http://localhost:8000)
- Документация Swagger — [http://localhost:8000/docs](http://localhost:8000/docs)
- Первый парсинг выполнится автоматически.

---

## Переменные окружения

| Переменная                 | Описание                              | Значение по умолчанию                                   |
|----------------------------|---------------------------------------|--------------------------------------------------------|
| `DATABASE_URL`             | Асинхронный DSN PostgreSQL           | `postgresql+asyncpg://postgres:postgres@db:5432/postgres` |
| `LOG_LEVEL`                | Уровень логирования                 | `INFO`                                                 |
| `PARSE_SCHEDULE_MINUTES`   | Интервал фонового парсинга (минуты) | `5`                                                    |

---

## API (кратко)

Базовый путь: `/api/v1`

### Вакансии

| Метод | Эндпоинт               | Описание                         | Статусы ответа           |
|-------|------------------------|----------------------------------|--------------------------|
| GET   | `/vacancies/`          | Список вакансий                 | 200                      |
| GET   | `/vacancies/{id}`      | Детали вакансии                 | 200, 404                 |
| POST  | `/vacancies/`          | Создать вакансию               | 201, 409 (duplicate)     |
| PUT   | `/vacancies/{id}`      | Обновить вакансию              | 200, 404, 409 (conflict) |
| DELETE| `/vacancies/{id}`      | Удалить вакансию               | 204, 404                 |

### Парсинг

| Метод | Эндпоинт    | Описание               | Ответ                  |
|-------|-------------|------------------------|------------------------|
| POST  | `/parse/`   | Ручной запуск парсинга | `{"created": integer}` |

---

## Примеры запросов (curl)

**Создание вакансии**
```bash
curl -X POST http://localhost:8000/api/v1/vacancies/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "timetable_mode_name": "Full-time",
    "tag_name": "Backend",
    "city_name": "Moscow",
    "published_at": "2026-02-12T10:00:00Z",
    "is_remote_available": true,
    "is_hot": false,
    "external_id": 1001
  }'
```

**Попытка создать дубликат (ответ 409)**
```json
{
  "detail": "Vacancy with external_id already exists"
}
```

**Обновление вакансии с конфликтом external_id (ответ 409)**
```json
{
  "detail": "External ID already in use by another vacancy"
}
```

---

## Тестирование

В корне репозитория находится скрипт `test_project.py`, который автоматически:
- поднимает окружение через `docker compose`;
- выполняет 10 интеграционных тестов (включая граничные случаи);
- проверяет работу планировщика;
- формирует отчёт `test_report.txt`.

Запуск тестов:
```bash
python3 test_project.py
```

**Результат последнего прогона:**  
✅ 10/10 тестов пройдено успешно.  
Детали — в файле [`TEST_REPORT.md`](TEST_REPORT.md).

---

## Структура проекта (основные модули)

```
.
├── app/
│   ├── api/v1/          # эндпоинты (vacancies, parse)
│   ├── core/            # конфигурация, логирование
│   ├── crud/            # операции с БД
│   ├── db/              # сессия, базовый класс
│   ├── models/          # SQLAlchemy модели
│   ├── schemas/         # Pydantic схемы
│   └── services/        # парсер, планировщик
├── alembic/             # миграции
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Стек технологий

- **Python 3.11**
- **FastAPI** + Uvicorn
- **SQLAlchemy 2.0** (asyncio)
- **PostgreSQL 16**
- **Alembic** (миграции)
- **APScheduler** (фоновые задачи)
- **httpx** (HTTP‑клиент)
- **Docker** / Docker Compose

---
