.PHONY: build up down logs run run-open open install

install:
	pip install -r requirements.txt

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
	@if [ "$$(uname)" = "Darwin" ]; then \
		open http://localhost:8000; \
	elif [ "$$(uname)" = "Linux" ]; then \
		xdg-open http://localhost:8000; \
	elif [ "$$(OS)" = "Windows_NT" ]; then \
		start http://localhost:8000; \
	else \
		echo "Не удалось определить ОС. Откройте http://localhost:8000 вручную."; \
	fi

run-open:
	@echo "Запускаю сервер и открываю браузер..."
	@python -m uvicorn app.main:app --reload &
	@sleep 2
	@make open
	@wait