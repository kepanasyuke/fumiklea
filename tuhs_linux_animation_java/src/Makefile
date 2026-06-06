# Находим первый попавшийся файл .java на любой глубине (включая все подпапки)
SRC_FILE := $(shell find . -name "*.java" | head -n 1)
CLASS_NAME := $(shell basename $(SRC_FILE) .java)
SRC_DIR := $(shell dirname $(SRC_FILE))

all: deps compile run

# Установка графических утилит и VNC-сервера для трансляции в браузер
deps:
	@if ! dpkg -s libxtst6 x11vnc fluxbox >/dev/null 2>&1; then \
		echo "========================================================"; \
		echo "  [DEPS] Установка X11, VNC и оконного менеджера..."; \
		echo "========================================================"; \
		sudo apt-get update && sudo apt-get install -y libxtst6 libxrender1 libxi6 xvfb x11vnc fluxbox; \
	fi

compile:
	@if [ -z "$(SRC_FILE)" ]; then \
		echo "  [ERROR] Нет .java файлов!"; \
		exit 1; \
	fi
	@echo "  [BUILD] Сборка: $(SRC_FILE) (Класс: $(CLASS_NAME))..."; \
	javac $(SRC_FILE)

run:
	@echo "========================================================"
	@echo "  [LAUNCH] Инициализация графического окружения..."
	@echo "========================================================"
	@# 1. Запускаем виртуальный дисплей :1 в фоне, если он еще не запущен
	@Xvfb :1 -screen 0 640x480x24 > /dev/null 2>&1 & sleep 1
	@# 2. Запускаем легковесный менеджер окон Fluxbox, чтобы окно Java имело рамки и фокус клавиатуры
	@DISPLAY=:1 fluxbox > /dev/null 2>&1 & sleep 1
	@# 3. Запускаем VNC сервер на стандартном порту 6080 для веб-трансляции
	@x11vnc -display :1 -nopw -listen localhost -xkb -forever -bg > /dev/null 2>&1 & sleep 1
	@echo "  [SUCCESS] Графический сервер готов!"
	@echo "  [LAUNCH] Запуск Java-приложения на экране :1..."
	@echo "========================================================"
	DISPLAY=:1 java -cp $(SRC_DIR):. $(CLASS_NAME)

clean:
	find . -name "*.class" -delete
	pkill -f Xvfb || true
	pkill -f fluxbox || true
	pkill -f x11vnc || true







