# Настройки окружения
PYTHON = venv/bin/python
PIP = venv/bin/pip
STREAMLIT = venv/bin/streamlit
SCRIPT = app.py
DATA_FILE = banking_transactions.csv

.PHONY: all help venv install run lint clean

# Команда по умолчанию
all: help

# Автоматическое документирование команд
help:
	@echo "========================================================================"
	@echo "⚙️  RISK ANALYTICS ENGINE - DEVELOPMENT INTERFACE"
	@echo "========================================================================"
	@echo "Доступные команды:"
	@echo "  make venv     - Создать изолированное виртуальное окружение"
	@echo "  make install  - Установить production-зависимости"
	@echo "  make run      - Запустить аналитическую панель (Streamlit)"
	@echo "  make lint     - Проверить код на соответствие стандартам PEP8"
	@echo "  make clean    - Удалить кэш, временные файлы и окружение"
	@echo "========================================================================"

# 1. Создание виртуального окружения
venv:
	@echo "📦 Создание виртуального окружения venv..."
	python3 -m venv venv
	@echo "✅ Окружение успешно создано."

# 2. Установка зависимостей уровня Enterprise
install: venv
	@echo "📥 Обновление pip и установка пакетов..."
	$(PIP) install --upgrade pip
	$(PIP) install streamlit pandas plotly numpy
	$(PIP) install flake8  # Для проверки качества кода
	@if [ ! -f $(DATA_FILE) ]; then \
		echo "⚠️  Внимание: Файл $(DATA_FILE) не обнаружен в корневой директории!"; \
	fi
	@echo "✅ Все зависимости установлены."

# 3. Запуск продакшн-дашборда
run:
	@echo "🛡️ Запуск Risk Analytics Engine..."
	$(STREAMLIT) run $(SCRIPT)

# 4. Проверка качества кода (Линтинг)
lint:
	@echo "🔍 Проверка кода утилитой Flake8 (PEP8)..."
	@if [ -d "venv" ]; then \
		venv/bin/flake8 $(SCRIPT) --max-line-length=120 || true; \
	else \
		flake8 $(SCRIPT) --max-line-length=120 || echo "Разверните venv через 'make install'"; \
	fi

# 5. Полная очистка проекта
clean:
	@echo "🧹 Очистка временных файлов и кэша..."
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .streamlit/cache
	@echo "✨ Проект полностью очищен."
