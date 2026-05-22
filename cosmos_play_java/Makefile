# Makefile для Космического арт-объекта
PORT = 8000
HOST = 127.0.0.1
MODELS_DIR = www/models

.PHONY: all prepare run stop help check clean

all: prepare run

prepare: clean
	@echo "📁 Подготовка файлов проекта..."
	@mkdir -p $(MODELS_DIR)
	@echo "📦 Копирование 3D-моделей планет..."
	@for planet in mercury venus earth mars jupiter saturn uranus neptune; do \
		echo "  - Копирование модели для $$planet"; \
		cp -r models/$$planet $(MODELS_DIR)/ 2>/dev/null || echo "    ⚠️ Модель для $$planet не найдена, будет использована текстура-заглушка"; \
	done
	@echo "✅ Проект готов к запуску!"

run: stop
	@echo "🚀 Запуск локального веб-сервера на порту $(PORT)..."
	@echo "Откройте в браузере: http://$(HOST):$(PORT)"
	@if which python3 > /dev/null; then \
		python3 -m http.server $(PORT); \
	elif which python > /dev/null; then \
		python -m http.server $(PORT); \
	elif which npx > /dev/null; then \
		npx serve -l $(PORT) .; \
	else \
		echo "❌ Ошибка: не найден ни Python3, ни Node.js."; \
		exit 1; \
	fi

stop:
	@echo "🔍 Проверка порта $(PORT)..."
	@lsof -t -i:$(PORT) | xargs kill -9 2>/dev/null || true
	@echo "✅ Порт $(PORT) свободен."

clean:
	@echo "🧹 Очистка папки www..."
	@rm -rf www
	@echo "Очистка завершена."

help:
	@echo "========================================================"
	@echo "  make          - подготовить файлы и запустить сервер"
	@echo "  make prepare  - только подготовить файлы"
	@echo "  make run      - запустить сервер"
	@echo "  make stop     - освободить порт"
	@echo "  make clean    - удалить папку www"
	@echo "========================================================"

check:
	@echo "🔍 Проверка окружения..."
	@which python3 > /dev/null && echo "  [✓] python3" || echo "  [ ] python3"
	@which node > /dev/null && echo "  [✓] node" || echo "  [ ] node"