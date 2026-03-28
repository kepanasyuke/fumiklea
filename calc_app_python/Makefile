PYTHON = python3
VENV_DIR = venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
PIP = $(VENV_DIR)/bin/pip
PYTHON_VENV = $(VENV_DIR)/bin/python

.PHONY: venv install run clean help

help:
	@echo "Доступные команды:"
	@echo "  make venv     — создать виртуальное окружение"
	@echo "  make install  — установить зависимости (Flask)"
	@echo "  make run      — запустить приложение (создаст venv и установит зависимости, если нужно)"
	@echo "  make clean    — удалить виртуальное окружение и __pycache__"
	@echo "  make help     — показать эту справку"

venv:
	@echo "Создание виртуального окружения..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Виртуальное окружение создано."

install: venv
	@echo "Установка зависимостей из requirements.txt..."
	$(PIP) install -r requirements.txt
	@echo "Зависимости установлены."

run: install
	@echo "Запуск Flask-приложения..."
	$(PYTHON_VENV) app.py

clean:
	@echo "Удаление виртуального окружения..."
	rm -rf $(VENV_DIR)
	@echo "Удаление __pycache__..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Очистка завершена."