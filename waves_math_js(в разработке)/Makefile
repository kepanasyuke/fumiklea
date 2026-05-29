# Makefile для проекта "Спор о струне"
HTML_FILE = index.html

.PHONY: all
all: help

# Открыть в браузере (только локально с GUI)
.PHONY: open
open:
	@echo "Открываем $(HTML_FILE) в браузере..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(HTML_FILE); \
	elif command -v open > /dev/null; then \
		open $(HTML_FILE); \
	else \
		echo "❌ Не удалось открыть браузер. Запустите 'make serve' и откройте порт 8000."; \
	fi

# Запустить HTTP-сервер
.PHONY: serve
serve:
	@echo "🚀 Запускаем HTTP-сервер на http://localhost:8000"
	@echo "   В CodeSpace: откройте вкладку 'Ports' и нажмите 'Open in Browser'"
	@if command -v python3 > /dev/null; then \
		python3 -m http.server 8000; \
	elif command -v python > /dev/null; then \
		python -m http.server 8000; \
	else \
		echo "❌ Python не установлен."; \
	fi

# Показать URL для ручного открытия
.PHONY: preview
preview:
	@echo "🌐 Откройте в браузере: http://localhost:8000"
	@echo "   В CodeSpace: нажмите на вкладке 'Ports' на глобус 🌐"

# Проверить наличие HTML-файла
.PHONY: check
check:
	@if [ -f $(HTML_FILE) ]; then \
		echo "✅ Файл $(HTML_FILE) найден."; \
	else \
		echo "❌ Файл $(HTML_FILE) не найден."; \
	fi

.PHONY: clean
clean:
	@echo "Очистка не требуется."

.PHONY: help
help:
	@echo "Доступные команды:"
	@echo "  make open     — открыть файл в браузере (только для локальных систем)"
	@echo "  make serve    — запустить HTTP-сервер на порту 8000"
	@echo "  make preview  — показать URL для открытия"
	@echo "  make check    — проверить наличие $(HTML_FILE)"
	@echo "  make help     — показать справку"