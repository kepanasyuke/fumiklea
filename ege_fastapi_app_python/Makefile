.PHONY: build up down logs run

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

run:
	uvicorn app.main:app --reload