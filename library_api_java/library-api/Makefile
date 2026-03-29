.PHONY: help build run clean docker-build docker-up docker-down docker-logs test

JAR_NAME=library-api-0.0.1-SNAPSHOT.jar
DOCKER_COMPOSE = docker-compose

help:
	@echo "Available commands:"
	@echo "  make build        - Build the JAR using Maven"
	@echo "  make run          - Run the JAR locally (needs PostgreSQL running)"
	@echo "  make clean        - Clean Maven target"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers (PostgreSQL + app)"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - Show logs from Docker containers"
	@echo "  make test         - Run tests"

build:
	./mvnw clean package -DskipTests

run: build
	java -jar target/$(JAR_NAME)

clean:
	./mvnw clean
	rm -rf target/

docker-build: build
	docker build -t library-api .

docker-up: docker-build
	$(DOCKER_COMPOSE) up -d --build
	@echo "App started at http://localhost:8080"
	@echo "Swagger UI: http://localhost:8080/swagger-ui.html"

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f

test:
	./mvnw test