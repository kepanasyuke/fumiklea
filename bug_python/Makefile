# Makefile для HARVARD MARK II – автоматический запуск
SCRIPT = bug.py
PYTHON = python3
VENV = venv
PORT = 6000

.PHONY: help install-system install-venv install-web build-web serve-web play clean

help:
	@echo "Команды:"
	@echo "  make install-system  - установить pygame через APT"
	@echo "  make install-venv    - создать venv и установить pygame"
	@echo "  make install-web     - установить pygbag (в venv или через pipx)"
	@echo "  make build-web       - собрать веб-версию (один раз)"
	@echo "  make serve-web       - запустить сервер на порту $(PORT) (без пересборки)"
	@echo "  make play            - автоматически запустить (X11 или браузер)"
	@echo "  make clean           - удалить venv и временные файлы"

install-system:
	sudo apt update && sudo apt install -y python3-pygame

install-venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install pygame

install-web:
	@if [ -f $(VENV)/bin/pip ]; then \
		echo "Установка pygbag в venv..."; \
		$(VENV)/bin/pip install pygbag; \
	else \
		echo "venv не найден. Устанавливаю pygbag через pipx..."; \
		python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install pygbag; \
	fi

# Проверка наличия скрипта
check-script:
	@if [ ! -f $(SCRIPT) ]; then \
		echo "Ошибка: файл $(SCRIPT) не найден!"; \
		exit 1; \
	fi

# Сборка веб-версии (делается один раз)
build-web: check-script install-web
	@echo "Сборка веб-версии (может занять 2-3 минуты)..."
	@if [ -f $(VENV)/bin/python ]; then \
		$(VENV)/bin/python -m pygbag --build $(SCRIPT); \
	else \
		pygbag --build $(SCRIPT); \
	fi

serve-web:
	@echo "Запуск сервера на порту $(PORT)..."
	@if [ -f "build/web/$(SCRIPT)" ]; then \
		if [ -f $(VENV)/bin/python ]; then \
			$(VENV)/bin/python -m pygbag --port $(PORT) --bind 0.0.0.0 build/web/$(SCRIPT); \
		else \
			pygbag --port $(PORT) --bind 0.0.0.0 build/web/$(SCRIPT); \
		fi; \
	else \
		echo "Ошибка: файл build/web/$(SCRIPT) не найден. Сначала выполните 'make build-web'."; \
		exit 1; \
	fi

play:
	@echo "Проверка окружения..."
	@if [ -f $(VENV)/bin/python ]; then \
		PYCMD=$(VENV)/bin/python; \
	else \
		PYCMD=$(PYTHON); \
	fi; \
	if ! $$PYCMD -c "import pygame" 2>/dev/null; then \
		echo "pygame не установлен. Установите: make install-system или make install-venv"; \
		exit 1; \
	fi; \
	if [ -n "$$DISPLAY" ] && $$PYCMD -c "import pygame; pygame.display.init()" 2>/dev/null; then \
		echo "Запуск в окне (X11)…"; \
		$$PYCMD $(SCRIPT); \
	else \
		echo "X11 не доступен. Пробую браузер (http://localhost:$(PORT))…"; \
		if [ ! -d "build/web" ]; then \
			echo "Веб-версия не собрана. Запускаю сборку..."; \
			$(MAKE) build-web; \
		fi; \
		$(MAKE) serve-web; \
	fi

clean:
	rm -rf $(VENV) __pycache__ build dist
	find . -name "*.pyc" -delete