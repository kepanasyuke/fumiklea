.PHONY: build up down logs run run-open open kill install clean test lint tunnel docker-clean

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
	python -m uvicorn app.main:app --host 0.0.0.0 --reload

open:
	python -m webbrowser http://localhost:8000

run-open:
	@echo "Запускаю сервер и открываю браузер..."
	@python -m uvicorn app.main:app --host 0.0.0.0 --reload &
	@sleep 2
	@make open
	@wait

kill:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || echo "Порт 8000 свободен"

clean:
	@echo "Cleaning project artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .pytest_cache
	@rm -f data/*.db data/*.db-journal

test:
	@python -m pytest

lint:
	@python -m flake8 app

docker-clean:
	@docker-compose down --rmi all --volumes --remove-orphans


tunnel:
	@echo "Убеждаюсь, что порт 8000 свободен..."
	@make kill
	@echo "Запускаю сервер в фоне..."
	@python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
	@sleep 3
	@echo "Запускаю localtunnel..."
	@npx localtunnel --port 8000 --subdomain ege-math-trainer