# Makefile для HARVARD MARK II – только X11 (локально или через VNC)
SCRIPT = bug.py
PYTHON = python3
VENV = venv

.PHONY: help install-system install-venv install-x11 start-x11 play clean

help:
	@echo "Команды:"
	@echo "  make install-system  - установить pygame через APT"
	@echo "  make install-venv    - создать venv и установить pygame"
	@echo "  make install-x11     - установить Xvfb, x11vnc, fluxbox, novnc (для удалённого доступа)"
	@echo "  make play            - запустить игру в текущем X11 (или через start-x11)"
	@echo "  make clean           - удалить venv и временные файлы"

install-system:
	sudo apt update && sudo apt install -y python3-pygame

install-venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install pygame

install-x11:
	@echo "Установка Xvfb, x11vnc, fluxbox и novnc..."
	sudo apt update
	sudo apt install -y xvfb x11vnc fluxbox
	@echo "X11 окружение установлено."

play:
	@echo "Проверка окружения..."
	@if [ -z "$$DISPLAY" ]; then \
		echo "Ошибка: переменная DISPLAY не установлена."; \
		echo "Если вы в Codespaces, сначала запустите 'make start-x11', затем выполните 'export DISPLAY=:99'"; \
		exit 1; \
	fi
	@if [ -f $(VENV)/bin/python ]; then \
		PYCMD=$(VENV)/bin/python; \
	else \
		PYCMD=$(PYTHON); \
	fi; \
	if ! $$PYCMD -c "import pygame" 2>/dev/null; then \
		echo "pygame не установлен. Установите: make install-system или make install-venv"; \
		exit 1; \
	fi; \
	echo "Запуск игры в X11 (DISPLAY=$$DISPLAY)…"; \
	$$PYCMD $(SCRIPT)

clean:
	rm -rf $(VENV) __pycache__ build dist
	find . -name "*.pyc" -delete