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
```

## Удалённый доступ (через туннель)

### 1) ngrok (рекомендуется)

```bash
# Если ngrok ещё не установлен (Linux/macOS)
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok

# Подключить auth token (получить на https://ngrok.com)
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN

# Запустить сервис и туннель
docker-compose up -d
ngrok http 8080
```

В консоли ngrok появится URL вида:

- `https://<your-id>.ngrok-free.app/swagger-ui/index.html`
- `https://<your-id>.ngrok-free.app/v3/api-docs`

### 2) localtunnel (альтернатива без аккаунта)

```bash
npm install -g localtunnel
docker-compose up -d
lt --port 8080 --subdomain library-api-demo
```

Открой:

- `https://library-api-demo.loca.lt/swagger-ui/index.html`
- `https://library-api-demo.loca.lt/v3/api-docs`

### Примечания

- Если отображается “не защищено” или “недоверенный сертификат” — используются временные dev-сертификаты ngrok/localtunnel, для разработки это нормально.
- Если требуется стабильный публичный URL для продакшн, настройте собственный HTTPS (например, через Nginx + DNS).

## Как пользоваться (пользовательский сценарий)

1. Запускаем сервис:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
2. Поднимаем туннель (localtunnel):
   ```bash
   npm install -g localtunnel
   lt --port 8080 --subdomain library-api-demo
   ```
3. Открываем интерфейс Swagger:
   - `https://library-api-demo.loca.lt/swagger-ui/index.html`
4. Пробуем регистрация / вход:
   - `POST /api/auth/register` (JSON: `{ "username": "user", "password": "pass" }`)
   - `POST /api/auth/login` (JSON: `{ "username": "user", "password": "pass" }`)
5. Вставляем JWT в кнопку `Authorize`:
   - `Bearer <token>`
6. Работает с основными эндпоинтами:
   - `GET /api/books`
   - `POST /api/books` / `PUT /api/books/{id}` / `DELETE /api/books/{id}`
   - `GET /api/borrowings` / `POST /api/borrowings` / `POST /api/borrowings/{id}/return`

Если `localtunnel` недоступен, можно использовать `ngrok` или стандартный localhost (для локального запуска):
- `http://127.0.0.1:8080/swagger-ui/index.html`
- `http://127.0.0.1:8080/v3/api-docs`