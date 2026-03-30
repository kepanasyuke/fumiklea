.PHONY: help build run clean docker-build docker-up docker-down docker-logs test

JAR_NAME = library-api-0.0.1-SNAPSHOT.jar

help:
	@echo "Available commands:"
	@echo "  make build       - Build the JAR locally using Maven (skip tests)"
	@echo "  make run         - Run the JAR locally (needs PostgreSQL running)"
	@echo "  make clean       - Clean Maven target"
	@echo "  make docker-build - Build Docker image (without starting)"
	@echo "  make docker-up   - Start Docker containers (PostgreSQL + app)"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make docker-logs - Show logs from Docker containers"
	@echo "  make docker-clean-ports - Remove containers using ports 5432 and 8080"
	@echo "  make test        - Run tests"

docker-build:
	docker-compose build

docker-up: docker-build
	docker-compose up -d
	@echo "App started at http://localhost:8080"
	@echo "Swagger UI: http://localhost:8080/swagger-ui.html"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	mvn test 

docker-clean-ports:
	@echo "Stopping and removing containers using ports 5432 and 8080..."
	@docker ps -a --filter "publish=5432" -q | xargs -r docker rm -f
	@docker ps -a --filter "publish=8080" -q | xargs -r docker rm -f
	@echo "Ports cleared."
