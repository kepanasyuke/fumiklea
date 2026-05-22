# Makefile для Космического арт-объекта
# Команды:
#   make         - загрузить модели и запустить сервер (основная цель)
#   make download - только загрузить модели (без запуска)
#   make run      - только запустить сервер (без загрузки моделей)
#   make clean    - удалить папку с моделями и временные файлы
#   make help     - показать справку

# Переменные
NASA_3D_REPO = https://github.com/nasa/NASA-3D-Resources/archive/refs/heads/master.zip
MODELS_DIR = models
PORT = 8000
HOST = 127.0.0.1

# Цель по умолчанию: загрузка + запуск
all: download run

# Справка
help:
	@echo "========================================================"
	@echo "   КОСМИЧЕСКАЯ КИНЕМАТИКА: КОМАНДЫ ЗАПУСКА"
	@echo "========================================================"
	@echo "  make         - загрузить модели и запустить сервер"
	@echo "  make download - загрузить 3D-модели NASA"
	@echo "  make run      - запустить локальный веб-сервер"
	@echo "  make clean    - удалить папку с моделями"
	@echo "  make help     - показать эту справку"
	@echo "========================================================"

# Загрузка моделей
download: clean_download
	@echo "🌐 Загрузка 3D-моделей из репозитория NASA..."
	@curl -L -o models.zip $(NASA_3D_REPO)
	@echo "📦 Распаковка архивов..."
	@unzip -q models.zip -d $(MODELS_DIR)
	@echo "📁 Организация файлов..."
	@mv $(MODELS_DIR)/NASA-3D-Resources-master/3D\ Models/* $(MODELS_DIR)/ 2>/dev/null || true
	@rm -rf $(MODELS_DIR)/NASA-3D-Resources-master
	@echo "🗑️ Удаление временных файлов..."
	@rm -f models.zip
	@echo "✅ Модели успешно загружены в папку '$(MODELS_DIR)'."

# Очистка предыдущей загрузки
clean_download:
	@echo "🧹 Очистка старых файлов..."
	@rm -rf $(MODELS_DIR)
	@rm -f models.zip

# Очистка всего (моделей и временных файлов)
clean: clean_download
	@echo "✅ Очистка завершена."

# Запуск локального сервера с авто-выбором технологии
run: stop
	@echo "🚀 Запуск локального веб-сервера на порту $(PORT)..."
	@if which python3 > /dev/null; then \
		echo "Используется Python3 HTTP сервер"; \
		echo "Откройте в браузере: http://$(HOST):$(PORT)"; \
		python3 -m http.server $(PORT); \
	elif which python > /dev/null; then \
		echo "Используется Python HTTP сервер"; \
		echo "Откройте в браузере: http://$(HOST):$(PORT)"; \
		python -m http.server $(PORT); \
	elif which npx > /dev/null; then \
		echo "Используется Node.js serve"; \
		echo "Откройте в браузере: http://$(HOST):$(PORT)"; \
		npx serve -l $(PORT) .; \
	else \
		echo "❌ Ошибка: не найден ни Python3, ни Node.js. Установите один из них."; \
		exit 1; \
	fi

# Принудительная остановка сервера (освобождение порта)
stop:
	@echo "🔍 Проверка порта $(PORT)..."
	@lsof -t -i:$(PORT) | xargs kill -9 2>/dev/null || true
	@echo "Порт $(PORT) свободен."

# Быстрый запуск (download + run без очистки)
start: download run

# Цель для разработки: очистка, загрузка моделей, запуск
dev: clean download run
