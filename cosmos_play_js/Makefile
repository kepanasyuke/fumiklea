# Makefile для космической сцены
PORT = 8000
HOST = 127.0.0.1

.PHONY: all prepare run stop help check clean

all: prepare run

prepare:
	@echo "📁 Подготовка файлов проекта..."
	@mkdir -p .tmp
	@echo "✅ Сцена готова к запуску."

run: stop
	@echo "🚀 Запуск локального веб-сервера на порту $(PORT)..."
	@echo "Откройте в браузере: http://$(HOST):$(PORT)"
	@if which python3 > /dev/null; then \
		python3 -m http.server $(PORT) --bind $(HOST); \
	elif which python > /dev/null; then \
		python -m http.server $(PORT) --bind $(HOST); \
	elif which npx > /dev/null; then \
		npx serve -l $(PORT) .; \
	else \
		echo "❌ Ошибка: не найден ни Python3, ни Node.js."; \
		exit 1; \
	fi

stop:
	@echo "🔍 Проверка порта $(PORT)..."
	@lsof -t -i:$(PORT) 2>/dev/null | xargs -r kill -9
	@echo "✅ Порт $(PORT) свободен."

clean:
	@echo "🧹 Очистка временных файлов..."
	@rm -rf .tmp
	@echo "Очистка завершена."

help:
	@echo "========================================================"
	@echo "  make          - подготовить файлы и запустить сервер"
	@echo "  make prepare  - только подготовить файлы"
	@echo "  make run      - запустить сервер"
	@echo "  make stop     - освободить порт"
	@echo "  make clean    - удалить временную папку"
	@echo "========================================================"

check:
	@echo "🔍 Проверка окружения..."
	@which python3 > /dev/null && echo "  [✓] python3" || echo "  [ ] python3"
	@which node > /dev/null && echo "  [✓] node" || echo "  [ ] node"