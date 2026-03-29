# Library REST API

Библиотечный REST API с JWT авторизацией, CRUD операциями над книгами, поиском и выдачей/возвратом книг.

## Технологии

- Java 17
- Spring Boot 3.1
- Spring Security + JWT
- Spring Data JPA
- PostgreSQL
- Swagger / OpenAPI
- Docker & Docker Compose

## Быстрый старт (Docker)

```bash
# Склонировать репозиторий
git clone https://github.com/your-repo/library-api.git
cd library-api

# Запустить через make
make docker-up

# Или напрямую через docker-compose
docker-compose up --build