.PHONY: all install fonts report clean help

all: report

help:
	@echo "📊 Анализ продаж кофейни - доступные команды:"
	@echo ""
	@echo "  make install    - Установить все зависимости"
	@echo "  make report     - Сгенерировать PDF-отчёт"
	@echo "  make fonts      - Установить шрифты DejaVu"
	@echo "  make clean      - Удалить все сгенерированные файлы"
	@echo "  make help       - Показать эту справку"
	@echo ""

install:
	@echo "📦 Установка зависимостей..."
	pip install -r requirements.txt
	@echo "✅ Зависимости установлены!"

fonts:
	@echo "🔤 Установка полного набора шрифтов DejaVu..."
	@mkdir -p fonts
	@if [ -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ]; then \
		cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf fonts/; \
		echo "✅ Шрифт DejaVuSans скопирован в папку fonts/"; \
	else \
		echo "⚠️ Системные шрифты не найдены. Скачайте вручную с https://dejavu-fonts.github.io/"; \
	fi

report:
	@echo "📊 Запуск генерации отчёта..."
	python run.py

clean:
	@echo "🧹 Очистка сгенерированных файлов..."
	@rm -f reports/*.pdf
	@echo "✅ Очищено!"