# Makefile для проекта "Спор о струне"
# Используется для удобного запуска статического сайта

# Имя основного HTML-файла
HTML_FILE = index.html

# Цель по умолчанию
.PHONY: all
all: help

# Открыть HTML в браузере по умолчанию
.PHONY: open
open:
	@echo "Открываем $(HTML_FILE) в браузере..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(HTML_FILE); \
	elif command -v open > /dev/null; then \
		open $(HTML_FILE); \
	else \
		echo "Не удалось определить команду для открытия браузера. Откройте $(HTML_FILE) вручную."; \
	fi

# Запустить простой HTTP-сервер на Python (порт 8000)
.PHONY: serve
serve:
	@echo "Запускаем HTTP-сервер на http://localhost:8000"
	@if command -v python3 > /dev/null; then \
		python3 -m http.server 8000; \
	elif command -v python > /dev/null; then \
		python -m http.server 8000; \
	else \
		echo "Python не установлен. Установите Python или откройте $(HTML_FILE) напрямую."; \
	fi

# Проверить, что HTML-файл существует
.PHONY: check
check:
	@if [ -f $(HTML_FILE) ]; then \
		echo "✅ Файл $(HTML_FILE) найден."; \
	else \
		echo "❌ Файл $(HTML_FILE) не найден. Убедитесь, что он находится в текущей папке."; \
	fi

# Очистка (в данном проекте нечего удалять, заглушка)
.PHONY: clean
clean:
	@echo "В проекте нет временных файлов. Очистка не требуется."

# Помощь
.PHONY: help
help:
	@echo "Доступные команды:"
	@echo "  make open    — открыть $(HTML_FILE) в браузере"
	@echo "  make serve   — запустить локальный HTTP-сервер на порту 8000"
	@echo "  make check   — проверить наличие $(HTML_FILE)"
	@echo "  make clean   — очистка (ничего не делает)"
	@echo "  make help    — показать эту справку"