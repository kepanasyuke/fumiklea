# Makefile для HARVARD MARK II – автоматический запуск
SCRIPT = bug.py
PYTHON = python3
VENV = venv

.PHONY: help install-system install-venv install-web play clean

help:
	@echo "Команды:"
	@echo "  make install-system  - установить pygame через APT"
	@echo "  make install-venv    - создать venv и установить pygame"
	@echo "  make install-web     - установить pygbag (в venv или через pipx)"
	@echo "  make play            - автоматически запустить (окно X11 или браузер)"
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
		echo "X11 не доступен. Пробую браузер (http://localhost:6000)…"; \
		if ! $$PYCMD -c "import pygbag" 2>/dev/null; then \
			echo "pygbag не установлен. Установите: make install-web"; \
			exit 1; \
		fi; \
		$$PYCMD -m pygbag $(SCRIPT); \
	fi

clean:
	rm -rf $(VENV) __pycache__ build dist
	find . -name "*.pyc" -delete