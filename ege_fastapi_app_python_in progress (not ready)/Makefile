.PHONY: build up down logs run run-open open kill install tunnel

install:
	pip install -r requirements.txt
	npm install -g localtunnel

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

run:
	python -m uvicorn app.main:app --reload

open:
	python -m webbrowser http://localhost:8000

run-open:
	@echo "Запускаю сервер и открываю браузер..."
	@python -m uvicorn app.main:app --reload &
	@sleep 2
	@make open
	@wait

kill:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || echo "Порт 8000 свободен"

tunnel:
	@echo "Запускаю сервер и туннель localtunnel..."
	@python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
	@sleep 2
	@npx localtunnel --port 8000 --subdomain ege-math-trainer