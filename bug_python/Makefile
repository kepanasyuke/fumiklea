# Makefile для HARVARD MARK II – автоматический запуск с поддержкой X11 в Codespaces
SCRIPT = bug.py
PYTHON = python3
VENV = venv
PORT = 6000          # порт для веб-версии игры
VNCPORT = 5900       # порт для VNC (обычно 5900)
WEBPORT = 6080       # порт для noVNC (доступ через браузер)

.PHONY: help install-system install-venv install-web install-x11 start-x11 play clean

help:
	@echo "Команды:"
	@echo "  make install-system  - установить pygame через APT"
	@echo "  make install-venv    - создать venv и установить pygame"
	@echo "  make install-web     - установить pygbag (в venv или через pipx)"
	@echo "  make install-x11     - установить Xvfb, x11vnc, fluxbox, novnc"
	@echo "  make start-x11       - запустить виртуальный X11 дисплей с VNC и веб-доступом"
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

install-x11:
	@echo "Установка Xvfb, x11vnc, fluxbox и novnc..."
	sudo apt update
	sudo apt install -y xvfb x11vnc fluxbox
	@echo "Установка noVNC из репозитория..."
	git clone https://github.com/novnc/noVNC.git /tmp/noVNC || true
	sudo cp -r /tmp/noVNC /usr/local/share/
	sudo ln -sf /usr/local/share/noVNC/vnc.html /usr/local/share/noVNC/index.html
	@echo "Установка websockify..."
	sudo apt install -y websockify || pip3 install websockify
	@echo "X11 окружение установлено."

start-x11:
	@echo "Запуск виртуального дисплея Xvfb :99 ..."
	Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
	sleep 2
	export DISPLAY=:99
	@echo "Запуск оконного менеджера fluxbox..."
	fluxbox -display :99 &
	sleep 1
	@echo "Запуск x11vnc (VNC-сервер) на порту $(VNCPORT)..."
	x11vnc -display :99 -forever -shared -rfbport $(VNCPORT) -passwd codespaces &
	sleep 2
	@echo "Запуск websockify для noVNC на порту $(WEBPORT)..."
	websockify -D --web=/usr/local/share/noVNC $(WEBPORT) localhost:$(VNCPORT)
	@echo "--------------------------------------------------"
	@echo "✅ Виртуальный рабочий стол запущен!"
	@echo "Чтобы открыть его в Codespaces:"
	@echo "1. Откройте вкладку PORTS (внизу)"
	@echo "2. Найдите порт $(WEBPORT) и нажмите на значок глобуса"
	@echo "3. В открывшейся странице нажмите 'Connect' (пароль: codespaces)"
	@echo "4. После входа откройте терминал в этой среде и выполните: make play"
	@echo "--------------------------------------------------"

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
	if [ -n "$$DISPLAY" ]; then \
		echo "Запуск в окне (X11)…"; \
		$$PYCMD $(SCRIPT); \
	else \
		echo "X11 не доступен. Пробую браузер (http://localhost:$(PORT))…"; \
		if ! $$PYCMD -c "import pygbag" 2>/dev/null; then \
			echo "pygbag не установлен. Установите: make install-web"; \
			exit 1; \
		fi; \
		echo "Освобождаю порт $(PORT)…"; \
		fuser -k $(PORT)/tcp 2>/dev/null || true; \
		echo "Запуск pygbag на порту $(PORT)…"; \
		$$PYCMD -m pygbag --port $(PORT) --bind 0.0.0.0 $(SCRIPT); \
	fi

clean:
	rm -rf $(VENV) __pycache__ build dist
	find . -name "*.pyc" -delete